from django import template
from django.template.loader import render_to_string

from siom.models import Submission, Entry, Task

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

@register.simple_tag(takes_context=True)
def scoreboard_table(context, course):
	tasks = course.tasks()
	submissions = Submission.objects.filter(task__in=tasks)
	submission_dict = {}
	for sub in submissions:
		if sub.verdict:
			submission_dict.setdefault(sub.user_id, set()).add(sub.task_id)
	scores = []
	for user in course.users.all():
		score = len(submission_dict.get(user.id, {}))
		scores.append({
			'user': user,
			'score': score
		})
	scores.sort(key=lambda score: score['user'].first_name + ' ' + score['user'].last_name)
	scores.sort(key=lambda score: score['score'], reverse=True)

	return render_to_string('tags/scoreboard_table.html', {
		'scores': scores,
		'total': tasks.count(),
	}, context)

@register.inclusion_tag('tags/tasks.html', takes_context=True)
def tasks(context, course):
	tasks = course.tasks()
	#TODO: sort by number of solved users?
	user = context['user']
	submissions = Submission.objects.filter(user=user, task__in=tasks)
	solved = set()
	tried = set()
	for sub in submissions:
		if sub.verdict:
			solved.add(sub.task)
		else:
			tried.add(sub.task)

	tasks = course.tasks()
	tasks_list = []
	for task in reversed(tasks):
		status = 'solved' if task in solved else 'tried' if task in tried else 'unsolved'
		print status
		task_item = {
			'task': task,
			'status': status,
		}
		tasks_list.append(task_item)
	return {
		'course': course,
		'tasks': tasks_list,
	}
