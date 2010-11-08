# vim:set ts=4 sw=4 noexpandtab:

from django.contrib import admin
from siom.models import *

class TaskAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {
			'fields': ['code', 'title', 'text'],
		}),
		('Limits', {
			'fields': ['time_limit_ms', 'memory_limit_mb'],
		}),
		('File names', {
			'fields': ['input', 'output'],
			'classes': ['collapse'],
		}),
	]

admin.site.register(Task, TaskAdmin)
admin.site.register(Course)
admin.site.register(Entry)
admin.site.register(Submission)
