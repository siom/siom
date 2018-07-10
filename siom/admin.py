# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4:

from django.contrib import admin
from siom.models import *
from grader.tasks import GradeTask
from mptt.admin import DraggableMPTTAdmin

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

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'language', 'verdict', 'score', 'submitted')
    list_filter = ('task', 'user', 'language', 'verdict')

    actions = ['regrade_submissions']

    def regrade_submissions(modeladmin, request, queryset):
        for submission in queryset:
            GradeTask.delay(submission.id)


admin.site.register(Task, TaskAdmin)
admin.site.register(Course, filter_horizontal=('users',))
admin.site.register(Entry)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Directory, DraggableMPTTAdmin)
