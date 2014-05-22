# vim:set ts=4 sw=4 noexpandtab:

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class Task(models.Model):
	code = models.CharField(max_length=255, unique=True)
	title = models.CharField(max_length=255)
	time_limit_ms = models.IntegerField()
	memory_limit_mb = models.IntegerField()
	input = models.CharField(max_length=255, blank=True)
	output = models.CharField(max_length=255, blank=True)
	text = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return u'{0.title} ({0.code})'.format(self)

class Course(models.Model):
	owner = models.ForeignKey(User, limit_choices_to={'is_staff': True})
	name = models.CharField(max_length=255)
	users = models.ManyToManyField(User, related_name='courses', blank=True)
	code = models.CharField(max_length=50, unique=True, validators=[MinLengthValidator(2)]) # short identifier, used in URLs
	open = models.BooleanField() # this course is open (visible) to users
	
	def __unicode__(self):
		return u'{0.name} ({0.code})'.format(self)

class Entry(models.Model):
	owner = models.ForeignKey(User, limit_choices_to={'is_staff': True})
	courses = models.ManyToManyField(Course, related_name='entries')
	tasks = models.ManyToManyField(Task, related_name='entries', blank=True)
	type = models.CharField(max_length=255, db_index=True)
	title = models.CharField(max_length=255)
	text = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	publish = models.DateTimeField(null=True, blank=True) # when entry was/will be published
	
	def __unicode__(self):
		return u'{0.title} on {1}'.format(self, ', '.join([c.name for c in self.courses.all()]))
	
	class Meta:
		verbose_name_plural = 'entries'

class Submission(models.Model):
	LANGUAGES = [('cpp', 'C++'), ('c', 'C'), ('pascal', 'Pascal')]
	task = models.ForeignKey(Task)
	user = models.ForeignKey(User)
	code = models.TextField()
	language = models.CharField(max_length=16, choices=LANGUAGES)
	verdict = models.NullBooleanField()
	score = models.FloatField(null=True, blank=True)
	message = models.TextField()
	submitted = models.DateTimeField(auto_now_add=True)

def get_solved(self):
	submissions = Submission.objects.filter(user=self, verdict=True).values('task', 'verdict')
	verdicts = {}
	for s in submissions:
		task = s['task']
		verdict = s['verdict']
		if task not in verdicts or not verdicts[task]:
			verdicts[task] = verdict
	solved = set()
	tried = set()
	for id, verdict in verdicts.iteritems():
		if verdict:
			solved.add(id)
		else:
			tried.add(id)
	return solved, tried

User.add_to_class('solved_tasks', get_solved)
