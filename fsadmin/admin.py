# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.conf.urls import url

from .views import build_views


class Media(models.Model):
    ROOT = "/home/www/siom/web/media"
    class Meta:
        managed = False
        verbose_name_plural = "Media"

class TestCase(models.Model):
    ROOT = "/home/www/siom/grader/tasks"
    class Meta:
        managed = False
        verbose_name_plural = "TestCases"


def build_admin(model_identifier, root_dir):
    class UploadAdmin(admin.ModelAdmin):

        def get_urls(self):
            views = build_views(model_identifier, root_dir)
            return [
                url(r'^(?:list/)?$', admin.sites.site.admin_view(views["index"]), {},
                    'fsadmin_{}_changelist'.format(model_identifier)),

                url(r'^list/_upload$',
                    admin.sites.site.admin_view(views["upload"]), {},
                    'fsadmin_{}_upload'.format(model_identifier)),
                url(r'^list/(.*)/_upload$',
                    admin.sites.site.admin_view(views["upload"]), {},
                    'fsadmin_{}_upload'.format(model_identifier)),

                url(r'^list/_add-dir$',
                    admin.sites.site.admin_view(views["add_directory"]), {},
                    'fsadmin_{}_add_directory'.format(model_identifier)),
                url(r'^list/(.*)/_add-dir$',
                    admin.sites.site.admin_view(views["add_directory"]), {},
                    'fsadmin_{}_add_directory'.format(model_identifier)),

                url(r'^list/(.*)/$', admin.sites.site.admin_view(views["index"]),
                    {}, 'fsadmin_{}_changelist'.format(model_identifier)),
                url(r'^delete/$', admin.sites.site.admin_view(views["delete"]), {},
                    'fsadmin_{}_delete'.format(model_identifier)),
                url(r'^rename/$', admin.sites.site.admin_view(views["rename"]), {},
                    'fsadmin_{}_rename'.format(model_identifier)),

                url(r'^_linklist$', admin.sites.site.admin_view(views["link_list"]),
                    {}, 'fsadmin_link_list'),

            ]
    return UploadAdmin

admin.site.register(Media, build_admin("media", Media.ROOT))
admin.site.register(TestCase, build_admin("testcase", TestCase.ROOT))
