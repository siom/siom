# vim:set ts=4 sw=4 noexpandtab:

from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.views import login
from django.http import Http404
from siom.models import *
from siom.forms import *
from siom.utils import course_view
from grader.tasks import GradeTask

def course_index(request):
    course_list = Course.objects.filter(open=True)
    my_course_list = Course.objects.filter(users=request.user, open=False) if request.user.is_authenticated() else []
    return render_to_response('course_index.html',
        {'course_list': course_list, 'my_course_list': my_course_list},
        RequestContext(request))

@course_view
def course_home(request, course, type='home'):
    entries = course.entries.filter(type=type, publish__isnull=False, publish__lte=datetime.now()).order_by('-publish')
    return render_to_response('course.html',
        {'course': course, 'entries': entries },
        RequestContext(request))

@course_view
def entry(request, course, id):
    entry = get_object_or_404(Entry, pk=int(id), courses=course, publish__isnull=False)
    submissions = list(Submission.objects.filter(task__entries=entry, user__courses=course))
    return render_to_response('entry.html',
        {'course': course, 'entry': entry, 'submissions': submissions},
        RequestContext(request))

@course_view
def task(request, course, code):
    task = get_list_or_404(Task, code=code, entries__courses=course)[0]
    return render_to_response('task.html',
        {'course': course, 'task': task},
        RequestContext(request))

@course_view
def submit(request, course):
    if not request.user.in_course:
        raise Http404
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid() and request.user.courses.filter(entries__tasks=form.cleaned_data['task']):
            submission = form.save(commit=False)
            submission.user = request.user
            submission.code = form.cleaned_data['source_file'].read()
            submission.save()
            GradeTask.delay(submission.id)
            return redirect('siom.views.submission', course.code, submission.id)
    else:
        form = SubmissionForm()
    course_entries = course.entries.all()
    if request.user != course.owner:
        course_entries = course_entries.filter(publish__isnull=False, publish__lte=datetime.now())
    form.fields['task'].queryset = Task.objects.filter(entries__in=course_entries)
    return render_to_response('submit.html',
        {'course': course, 'form': form},
        RequestContext(request))

@course_view
def scoreboard(request, course):
	return render_to_response('scoreboard.html', {
		'course': course,
	}, RequestContext(request))

@course_view
def submission(request, course, id):
    course_tasks = Task.objects.filter(entries__courses=course).distinct()
    submission = get_object_or_404(Submission, pk=int(id), task__in=course_tasks, user__courses=course)
    all_submissions = Submission.objects.filter(user=submission.user, task=submission.task)
    show_source = request.user.is_authenticated() and (request.user.is_staff or
            submission.user == request.user or
            Submission.objects.filter(user=request.user, task=submission.task,
                                      verdict=True).exists())
    return render_to_response('submission.html',
        {'course': course,
         'submission': submission,
         'all_submissions': all_submissions,
         'show_source': show_source},
        RequestContext(request))

def course_login(request, course_code, *args, **kwargs):
    course = get_object_or_404(Course, code=course_code)
    kwargs.setdefault('extra_context', {})['course'] = course
    return login(request, *args, **kwargs)
