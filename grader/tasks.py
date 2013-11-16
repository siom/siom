import os, os.path, shutil, subprocess, shlex, re
try:
	from os import symlink as link
except ImportError:
	from shutil import copy as link

from django.template.loader import render_to_string
from django.conf import settings
from celery.task import Task
from celery.registry import tasks
from siom.models import Submission

class SubmissionGrader(object):
	def __init__(self, submission):
		self.submission = submission
		self.task = submission.task
		self.rundir = settings.GRADER_RUN_DIR
		self.boxdir = os.path.join(settings.GRADER_RUN_DIR, 'box')
		self.taskdir = os.path.join(settings.GRADER_TASK_DIR, self.task.code)
		self.filename = '{0}.{1}'.format(self.task.code, settings.GRADER_FILE_EXT[submission.language])
		self.filepath = os.path.join(self.rundir, self.filename)
		self.tests = []
		self.inputfile = os.path.join(self.rundir, self.task.code + '.in')
		self.outputfile = os.path.join(self.rundir, self.task.code + '.out')
		self.solfile = os.path.join(self.rundir, self.task.code + '.sol')
		self.checker = os.path.join(settings.GRADER_SYS_DIR, 'checker.py')
		self.boxinputfile = os.path.join(self.boxdir, self.task.input) if self.task.input else None
		self.boxoutputfile = os.path.join(self.boxdir, self.task.output) if self.task.output else None
	
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
	
	def prepareRunDir(self):
		self.cleanDir(self.rundir)
		with open(self.filepath, 'w') as f:
			f.write(self.submission.code.encode('utf8'))
	
	def cleanBoxDir(self):
		self.cleanDir(self.boxdir)
	
	def doCompile(self):
		self.cleanBoxDir()
		shutil.copy(self.filepath, self.boxdir)
		self.list('prepare compile')
		compile_cmd = shlex.split(settings.GRADER_COMPILE_ARGS[self.submission.language].format(filename=self.filename, executable=self.task.code))
		comp_proc = subprocess.Popen(compile_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.boxdir)
		comp_out, _ = comp_proc.communicate()
		self.list('after compile')
		success = comp_proc.returncode == 0
		if success:
			self.execfile = os.path.join(self.rundir, self.task.code)
			shutil.copy(os.path.join(self.boxdir, self.task.code), self.execfile)
		self.list('compile done')
		return success, comp_out
	
	def prepareTest(self, inputfile, outputfile):
		self.removeFile(self.inputfile)
		self.removeFile(self.outputfile)
		self.removeFile(self.solfile)
		link(inputfile, self.inputfile)
		link(outputfile, self.solfile)
		self.list('test prepared')
	
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
	
	def doRun(self):
		self.cleanBoxDir()
		shutil.copy(self.execfile, self.boxdir)
		execfile = os.path.join(self.boxdir, os.path.basename(self.execfile))
		if self.boxinputfile:
			link(self.inputfile, self.boxinputfile)
		infofile = os.path.join(self.rundir, 'process.info')
		self.list('run prepared')
		
		cmd = [ os.path.join(settings.GRADER_SYS_DIR, 'box'),
			'-c', self.boxdir,
			'-a2', '-f',
			'-m', str(self.task.memory_limit_mb * 1024),
			'-k', str(self.task.memory_limit_mb * 1024),
			'-t', str(self.task.time_limit_ms / 1000.0),
			'-w', str(self.task.time_limit_ms / 1000.0), '-x1',
			'-M', infofile,
		]
		if not self.boxinputfile:
			cmd.extend(['-i', self.inputfile])
		if not self.boxoutputfile:
			cmd.extend(['-o', self.outputfile])
		cmd.extend(['--', execfile])
		run_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		run_out, run_err = run_proc.communicate()
		info = self.readProcessInfoFile(infofile)
		self.list('after run')
		
		if self.boxoutputfile and os.path.exists(self.boxoutputfile):
			shutil.copy(self.boxoutputfile, self.outputfile)
		
		success = info.get('status', 'OK') == 'OK'
		time = float(info['time'])
		msg = info.get('message', '')
		
		self.list('run done')
		return success, time, msg
	
	def doGrade(self):
		self.cleanBoxDir()
		inputfile = self.boxinputfile or os.path.join(self.boxdir, self.task.code + '.in')
		outputfile = self.boxoutputfile or os.path.join(self.boxdir, self.task.code + '.out')
		solfile = os.path.join(self.boxdir, self.task.code + '.sol')
		checker = os.path.join(self.boxdir, 'checker')
		link(self.inputfile, inputfile)
		link(self.outputfile, outputfile)
		link(self.solfile, solfile)
		link(self.checker, checker)
		self.list('grade prepared')
		try:
			grade_proc = subprocess.Popen([checker] + map(os.path.basename, [inputfile, outputfile, solfile]),
					stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.boxdir)
			grade_out, _ = grade_proc.communicate()
			points, msg = grade_out.split('\n', 1)
		except:
			points, msg = 0, 'Checker error'
		success = points and points != '0'
		self.list('grade done')
		return success, msg
	
	def process(self):
		self.prepareRunDir()
		self.list('prepareRunDir')
		compile_success, compile_msg = self.doCompile()
		results = []
		success_count = 0
		if compile_success:
			self.findTests()
			for infn, outfn in self.tests:
				infile = os.path.join(self.taskdir, infn)
				outfile = os.path.join(self.taskdir, outfn)
				self.prepareTest(infile, outfile)
				success, time, msg = self.doRun()
				if success:
					success, msg = self.doGrade()
				if success:
					success_count += 1
				results.append((success, time, msg))
		self.submission.verdict = compile_success and success_count == len(self.tests)
		self.submission.score = float(success_count) / len(self.tests) if self.tests else 0
		self.submission.message = render_to_string('results.html', {
			'submission': self.submission,
			'compile_success': compile_success,
			'compile_msg': compile_msg,
			'results': results,
		})

	def list(self, msg=None):
		return
		if msg:
			print msg
		subprocess.call(['ls', '-lR', self.rundir])

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
