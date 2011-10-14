# vim:set ts=4 sw=4 noexpandtab:

from django.conf.urls.defaults import *

urlpatterns = patterns('siom.views',
	(r'^$', 'course_index'),
	(r'^(\w+)/$', 'course_home'),
	(r'^(\w+)/f/(\w+)\.html$', 'course_home'),
	(r'^(\w+)/e/(\d+)\.html$', 'entry'),
	(r'^(\w+)/t/(\w+)\.html$', 'task'),
	(r'^(\w+)/s/(\d+)\.html$', 'submission'),
	(r'^(\w+)/submit\.html$', 'submit'),
	(r'^(\w+)/login\.html$', 'course_login',
		{ 'template_name': 'login.html',
		'extra_context': { 'base_template': 'course_base.html' } }),
)

urlpatterns += patterns('django.contrib.auth.views',
	(r'^login\.html$', 'login',
		{ 'template_name': 'login.html',
		'extra_context': { 'base_template': 'base.html' } }),
	(r'^logout\.html$', 'logout'),
)
