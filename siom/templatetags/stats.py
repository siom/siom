from django import template
from django.template.loader import render_to_string

from siom.models import Submission, Entry

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
	user_subs = {}
	for submission in Submission.objects.filter(user__courses=course):
		if submission.user not in user_subs:
			user_subs[submission.user] = []
		user_subs[submission.user].append(submission)
	
	#TODO: move to models?
	tasks = set()
	for entry in Entry.objects.filter(courses=course):
		for task in entry.tasks.all():
			tasks.add(task)
		#tasks = tasks | set(entry.tasks)

	scores = []
	for user in user_subs:
		score = {}
		score['user'] = user
		solved = set()
		for sub in user_subs[user]:
			if sub.verdict:
				solved.add(sub.task)
				#solved[sub.task] = True
		solved = filter(lambda x : x in tasks, solved)
		score['score'] = len(solved)
		scores.append(score)
	scores.sort(reverse=True, key=lambda score:score['score'])

	return render_to_string('tags/scoreboard_table.html', {
		'scores': scores,
		'total': len(tasks),
	}, context)
