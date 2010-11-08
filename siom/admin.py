# vim:set ts=4 sw=4 noexpandtab:

from django.contrib import admin
from siom.models import *

admin.site.register(Task)
admin.site.register(Course)
admin.site.register(Entry)
admin.site.register(Submission)
