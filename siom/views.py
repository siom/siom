# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4:
from datetime import datetime
from django.views.decorators.http import require_POST
from django.template import RequestContext
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.contrib.auth import authenticate
from django.http import Http404
from siom.models import *
from siom.forms import *
from siom.utils import course_view
from grader.tasks import GradeTask
import logging

logger = logging.getLogger("django")


def index(request):
    return render(request, 'index.html', {})

def course_index(request):
    active_courses = Course.objects.filter(open=True)
    closed_courses = Course.objects.filter(open=False)
    return render(request, 'course_index.html', {'active_courses': active_courses, 'closed_courses': closed_courses})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return render_to_response('registration_complete.html', {
                'user': user,
            },RequestContext(request))
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def course_home(request, course_code, type='home'):
    course = get_object_or_404(Course, code=course_code)
    entries = course.entries.filter(type=type, publish__isnull=False, publish__lte=datetime.now()).order_by('-publish')
    solved, tried = request.user.solved_tasks() if request.user.is_authenticated() else ({}, {})

    return render(request, 'course.html',
        {
            'course': course,
            'entries': entries,
            'solved': solved,
            'tried': tried,
        })

def archive(request, directory_pk):
    directory = get_object_or_404(Directory, pk=directory_pk)
    return render(request, 'archive.html', {'directory': directory, 'tasks': directory.tasks})

def entry(request, course_code, id):
    course = get_object_or_404(Course, code=course_code)
    entry = get_object_or_404(Entry, pk=int(id), courses=course, publish__isnull=False)
    submissions = list(Submission.objects.filter(task__entries=entry, user__courses=course))
    solved, tried = request.user.solved_tasks() if request.user.is_authenticated() else ({}, {})
    return render(request, 'entry.html',
         {
            'course': course,
            'entry': entry,
            'submissions': submissions,
            'solved': solved,
            'tried': tried,
        })

def task(request, code):
    form = SubmissionForm()
    task = get_list_or_404(Task, code=code)[0]

    if request.user.is_authenticated():
        submissions = Submission.objects.filter(user=request.user, task=task)
        last_submission = None
        if submissions.exists():
            last_submission = max(submissions, key=lambda s: s.submitted)
        return render(request, 'task.html', {'task': task, 'form': form, 'last_submission': last_submission})
    return render(request, 'task.html', {'task': task, 'form': form})

@login_required
@require_POST
def submit(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.POST:
        form = SubmissionForm(request.POST, request.FILES)

        if form.is_valid():
            submission = form.save(commit=False)
            submission.task = task
            submission.user = request.user
            submission.code = form.cleaned_data['source_file'].read()
            submission.save()
            GradeTask.delay(submission.pk)
            return redirect('submission', submission.pk)

def scoreboard(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    return render(request, 'scoreboard.html', {'course': course})

def submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk)
    all_submissions = Submission.objects.filter(user=submission.user, task=submission.task)
    show_source = request.user.is_authenticated() and (request.user.is_staff or
            submission.user == request.user or
            Submission.objects.filter(user=request.user, task=submission.task,
                                      verdict=True).exists())
    return render(request, 'submission.html',
        { 'submission': submission,
         'all_submissions': all_submissions,
         'show_source': show_source})
