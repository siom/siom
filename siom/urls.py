# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4:

from django.conf.urls import *
from django.contrib.auth.views import logout, password_change, login
import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^courses$', views.course_index, name='course_index'),
    url(r'^register$', views.register, name='register'),
    url(r'^(\w+)/$', views.course_home, name='course_home'),
    url(r'^(\w+)/f/(\w+)\.html$', views.course_home, name='course_home'),
    url(r'^(\w+)/e/(\d+)\.html$', views.entry, name='entry'),
    url(r'^task/(\w+)\.html$', views.task, name='task'),
    url(r'^submission/(\d+)\.html$', views.submission, name='submission'),
    url(r'^archive/(\d+)\.html$', views.archive, name='archive'),
    url(r'^submit/(\d+)\.html$', views.submit, name='submit'),
    url(r'^(\w+)/scoreboard\.html$', views.scoreboard, name='scoreboard'),
]

urlpatterns += [
    url(r'^login\.html$', login,
        { 'template_name': 'login.html',
        'extra_context': { 'base_template': 'base.html' } }, name='django.contrib.auth.views.login'),
    url(r'^logout\.html$', logout, name='django.contrib.auth.views.logout'),
    url(r'^passwd\.html$', password_change,
        { 'template_name': 'passwd.html',
        'post_change_redirect': '/',
        'extra_context': { 'base_template': 'base.html' } }, name='django.contrib.auth.views.password_change'),
]
