# vim:set ts=4 sw=4 noexpandtab:

import django.views.static
from django.conf import settings
from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^a/', include(admin.site.urls)),
    url(r'^m/(?P<path>.*)$', django.views.static.serve, { 'document_root': settings.MEDIA_ROOT }),
    url(r'', include('siom.urls')),
]
