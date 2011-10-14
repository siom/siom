from django import template
from django.template.loader import render_to_string

from siom.models import Submission

register = template.Library()

@register.tag(name="results_table")
def do_results_table(parser, token):
	try:
		tag_name, tasks_var = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])
	return ResultsTableNode(tasks_var)

class ResultsTableNode(template.Node):
	def __init__(self, tasks_var):
		self.tasks_var = template.Variable(tasks_var)
	def render(self, context):
		try:
			tasks = self.tasks_var.resolve(context)
			return results_table(context, tasks)
		except template.VariableDoesNotExist:
			return ''

def results_table(context, tasks):
	course = context['course']
	if not isinstance(tasks, list):
		tasks = list(tasks)
	submissions = Submission.objects.filter(task__in=tasks, user__courses=course)
	submission_dict = {}
	for sub in submissions:
		submission_dict.setdefault(sub.user_id, {}).setdefault(sub.task_id, []).append(sub)
	submission_table = []
	for user in course.users.all():
		row = []
		user_dict = submission_dict.get(user.id, {})
		for task in tasks:
			subs = user_dict.get(task.id, [])
			if subs:
				best = max(subs, key=lambda sub: (sub.verdict, sub.score))
				verdict = best.verdict
				score = best.score * 100
			else:
				best = None
				verdict = None
				score = None
			row.append({'task': task, 'best': best, 'verdict': verdict, 'score': score, 'count': len(subs)})
		submission_table.append((user, row))
	#TODO: maybe sort rows by smth
	return render_to_string('tags/results_table.html',
		{'tasks': tasks, 'submissions': submission_table},
		context)

