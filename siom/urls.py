# vim:set ts=4 sw=4 noexpandtab:

from django.conf.urls.defaults import *

urlpatterns = patterns('siom.views',
	('$^', 'course_index'),
)
