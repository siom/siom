# vim:set ts=4 sw=4 noexpandtab:

from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404, redirect
from siom.models import *
from siom.forms import *
from grader.tasks import GradeTask

def course_index(request):
	course_list = get_list_or_404(Course)
	return render_to_response('course_index.html',
		{'course_list': course_list},
		RequestContext(request))

def course_home(request, course_code, type='home'):
	course = get_object_or_404(Course, code=course_code)
	entries = course.entries.filter(type=type, publish__isnull=False, publish__lte=datetime.now()).order_by('-publish')
	return render_to_response('course.html',
		{'course': course, 'entries': entries },
		RequestContext(request))

def entry(request, course_code, id):
	course = get_object_or_404(Course, code=course_code)
	entry = get_object_or_404(Entry, pk=int(id), courses=course, publish__isnull=False)
	submissions = list(Submission.objects.filter(task__entries=entry, user__courses=course))
	return render_to_response('entry.html',
		{'course': course, 'entry': entry, 'submissions': submissions},
		RequestContext(request))

def task(request, course_code, code):
	course = get_object_or_404(Course, code=course_code)
	task = get_object_or_404(Task, code=code, entries__courses=course)
	return render_to_response('task.html',
		{'course': course, 'task': task},
		RequestContext(request))

def submit(request, course_code):
	course = get_object_or_404(Course, code=course_code)
	#TODO: filter tasks
	if request.method == 'POST':
		form = SubmissionForm(request.POST, request.FILES)
		if form.is_valid():
			submission = form.save(commit=False)
			submission.user = request.user
			submission.code = form.cleaned_data['source_file'].read()
			submission.save()
			GradeTask.delay(submission.id)
			return redirect('siom.views.submission', course.code, submission.id)
	else:
		form = SubmissionForm()
	return render_to_response('submit.html',
		{'course': course, 'form': form},
		RequestContext(request))

def submission(request, course_code, id):
	course = get_object_or_404(Course, code=course_code)
	submission = get_object_or_404(Submission, pk=int(id), task__entries__courses=course, user__courses=course)
	all_submissions = Submission.objects.filter(user=submission.user, task=submission.task)
	return render_to_response('submission.html',
		{'course': course, 'submission': submission, 'all_submissions': all_submissions},
		RequestContext(request))
