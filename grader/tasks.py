from celery.task import Task
from celery.registry import tasks
from siom.models import Submission
from django.template.loader import render_to_string

import random

class GradeTask(Task):
	def run(self, id):
		try:
			sub = Submission.objects.get(pk=id)
		except Submission.DoesNotExist:
			return
		if sub.task.code.startswith('z'):
			return # cannot grade, no tests, etc.
		compile = random.choice([True, False])
		if compile:
			ntests = random.randint(5, 10)
			pgood = random.random()
			tests = [(random.random() < pgood, random.uniform(0, 2)) for i in range(ntests)]
			tests_passed = len([r for r, t in tests if r])
			score = float(tests_passed) / ntests
			verdict = tests_passed == ntests
			msg = render_to_string('results.html', {
				'submission': sub,
				'tests': tests,
				'score': score,
			})
		else:
			score = 0
			verdict = False
			msg = "Compile error."
		sub.verdict = verdict
		sub.message = msg
		sub.score = score
		sub.save()

tasks.register(GradeTask)