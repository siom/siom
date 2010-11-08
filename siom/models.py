# vim:set ts=4 sw=4 noexpandtab:

from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
	code = models.CharField(max_length=255, unique=True)
	title = models.CharField(max_length=255)
	timeLimitMS = models.IntegerField()
	memoryLimitMB = models.IntegerField()
	input = models.CharField(max_length=255, blank=True)
	output = models.CharField(max_length=255, blank=True)
	text = models.TextField()

class Course(models.Model):
	owner = models.ForeignKey(User, limit_choices_to={'is_staff': True})
	name = models.CharField(max_length=255)
	users = models.ManyToManyField(User, related_name='courses')

class Entry(models.Model):
	owner = models.ForeignKey(User, limit_choices_to={'is_staff': True})
	courses = models.ManyToManyField(Course, related_name='entries')
	tasks = models.ManyToManyField(Task, related_name='entries')
	type = models.CharField(max_length=255, db_index=True)
	title = models.CharField(max_length=255)
	text = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	publish = models.DateTimeField(null=True, blank=True)

class Submission(models.Model):
	LANGUAGES = [('cpp', 'C++'), ('c', 'C'), ('pascal', 'Pascal')]
	task = models.ForeignKey(Task)
	user = models.ForeignKey(User)
	code = models.TextField()
	language = models.CharField(max_length=16, choices=LANGUAGES)
	verdict = models.NullBooleanField()
	message = models.TextField()
	submitted = models.DateTimeField(auto_now_add=True)
