from django import template
from django.template.loader import render_to_string

from siom.models import Submission

register = template.Library()

@register.simple_tag(takes_context=True)
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
				best = max(subs, key=lambda sub: (sub.verdict, sub.score, sub.submitted))
				verdict = best.verdict
				score = best.score * 100 if best.score is not None else None
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

