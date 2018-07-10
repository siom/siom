import os, os.path, shutil, shlex, re
from subprocess import call, Popen, PIPE, STDOUT
try:
	from os import symlink as link
except ImportError:
	from shutil import copy as link

from django.template.loader import render_to_string
from django.conf import settings
from celery.task import Task
from celery.registry import tasks
from siom.models import Submission
import logging

class Sandbox(object):
	def __init__(self, options):
		self.bid = -1
		rc = -1
		while rc != 0:
			self.bid += 1
			init_cmd = ["isolate", "-b", str(self.bid)] + options + ["--init"]
			proc = Popen(init_cmd, stdout=PIPE)
			output, err = proc.communicate()
			rc = proc.returncode

		self.path = os.path.join(output.rstrip("\n"), "box")

	def run(self, options, command, args=None):
		run_cmd = ["isolate", "-b", str(self.bid)] + options + ["--run"] + ["--"] + [command]
		if args:
			run_cmd.extend(args)
		ret = call(run_cmd)
		return ret

	def clean(self, options):
		clean_cmd = ["isolate", "-b", str(self.bid)] + options + ["--cleanup"]
		ret = call(clean_cmd)
		return ret

class SubmissionGrader(object):
	def __init__(self, submission):
		self.submission = submission
		self.task = submission.task
		self.compiledir = settings.GRADER_COMPILE_DIR
		self.taskdir = os.path.join(settings.GRADER_TASK_DIR, self.task.code)
		self.filename = '{0}.{1}'.format(self.task.code, settings.GRADER_FILE_EXT[submission.language])
		self.filepath = os.path.join(self.compiledir, self.filename)
		self.execfile = os.path.splitext(self.filepath)[0]
		self.tests = []
		self.checker = os.path.join(settings.GRADER_SANDBOX_DIR, 'checker.py')

	def canProcess(self):
		return os.path.exists(self.taskdir)

	def findTests(self):
		self.tests = []
		for file in os.listdir(self.taskdir):
			base, ext = os.path.splitext(file)
			if ext != '.in':
				continue
			solfile = base + '.sol'
			if not os.path.exists(os.path.join(self.taskdir, solfile)):
				continue
			self.tests.append((file, solfile))
		self.tests.sort()
		r = re.compile(r'^checker(?:\.\w+)?$')
		for file in os.listdir(self.taskdir):
			if r.match(file) and os.access(os.path.join(self.taskdir, file), os.X_OK):
				self.checker = os.path.join(self.taskdir, file)
				break

	def cleanDir(self, dir):
		if os.path.exists(dir):
			shutil.rmtree(dir)
		os.mkdir(dir, 0770)

	def removeFile(self, file):
		if os.path.exists(file):
			# maybe add chmod +w
			os.unlink(file)

	def prepareCompileDir(self):
		self.cleanDir(self.compiledir)
		with open(self.filepath, 'w') as f:
			f.write(self.submission.code.encode('utf8'))

	def doCompile(self):
		compile_cmd = shlex.split(settings.GRADER_COMPILE_ARGS[self.submission.language].format(filename=self.filename, executable=self.task.code))
		comp_proc = Popen(compile_cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=self.compiledir)
		comp_out, _ = comp_proc.communicate()
		success = comp_proc.returncode == 0
		return success, comp_out

	def readProcessInfoFile(self, infofile):
		with open(infofile) as f:
			lines = f.readlines()
		info = {}
		sep = ':'
		for line in lines:
			key, p, val = line.partition(sep)
			if p != sep:
				continue
			info[key] = val
		return info

	def doRun(self, box):
		infofile = os.path.join(self.compiledir, "process.info")
		options = [
			'--cg',
			'-m', str(self.task.memory_limit_mb * 1024),
			'-k', str(self.task.memory_limit_mb * 1024),
			'-t', str(self.task.time_limit_ms / 1000.0),
			'-w', str(self.task.time_limit_ms / 1000.0),
			'-x', str(self.task.time_limit_ms / 1000.0),
			'-M', infofile,
		]
		if not self.task.input:
			options.extend(['-i', self.task.code + ".in"])
		if not self.task.output:
			options.extend(['-o', self.task.code + ".out"])

		command = self.task.code
		box.run(options, command)
		info = self.readProcessInfoFile(infofile)
		success = info.get('status', 'OK') == 'OK'
		time = float(info['time'])
		msg = info.get('message', '')

		return success, time, msg

	def doGrade(self, box):
		inputfile = os.path.join(box.path, self.task.code + '.in')
		outputfile = os.path.join(box.path, self.task.code + '.out')
		solfile = os.path.join(box.path, self.task.code + '.sol')
		checker = os.path.join(box.path, 'checker.py')
		shutil.copy(self.checker, checker)
		try:
			grade_proc = Popen([checker] + map(os.path.basename, [inputfile, outputfile, solfile]),
					stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=box.path)
			grade_out, _ = grade_proc.communicate()
			points, msg = grade_out.split('\n', 1)
		except:
			points, msg = 0, 'Checker error'
		success = points and points != '0'
		return success, msg

	def process(self):
		try:
			self.prepareCompileDir()
		except UnicodeDecodeError:
			return
		compile_success, compile_msg = self.doCompile()
		results = []
		success_count = 0
		if compile_success:
			self.findTests()
			for infn, outfn in self.tests:
				infile = os.path.join(self.taskdir, infn)
				outfile = os.path.join(self.taskdir, outfn)
				isolate = Sandbox(["--cg"])
				shutil.copy(infile, os.path.join(isolate.path, self.task.code + '.in'))
				shutil.copy(self.execfile, os.path.join(isolate.path, self.task.code))
				success, time, msg = self.doRun(isolate)
				if success:
					shutil.copy(outfile, os.path.join(isolate.path, self.task.code + '.sol'))
					success, msg = self.doGrade(isolate)
				if success:
					success_count += 1
				results.append((success, time, msg))
				isolate.clean(["--cg"])
		self.submission.verdict = compile_success and success_count == len(self.tests)
		self.submission.score = float(success_count) / len(self.tests) if self.tests else 0
		self.submission.message = render_to_string('results.html', {
			'submission': self.submission,
			'compile_success': compile_success,
			'compile_msg': compile_msg,
			'results': results,
		})

	def list(self, path, msg=None):
		return
		if msg:
			logging.info(msg)
		logging.info(call(['ls', '-l', path]))

class GradeTask(Task):
	def run(self, id):
		try:
			sub = Submission.objects.get(pk=id)
		except Submission.DoesNotExist:
			return
		grader = SubmissionGrader(sub)
		if not grader.canProcess():
			print "Skipping submission."
			return
		grader.process()
		sub.save()

tasks.register(GradeTask)
