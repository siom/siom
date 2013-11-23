# vim:set ts=4 sw=4 noexpandtab:

import django.views.static
from django.conf import settings
from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^d/', include('d.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^a/', include(admin.site.urls)),
    (r'^m/(?P<path>.*)$', django.views.static.serve, { 'document_root': settings.MEDIA_ROOT }),
    (r'', include('siom.urls')),
)
