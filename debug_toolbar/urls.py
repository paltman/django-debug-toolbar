"""
URLpatterns for the debug toolbar. 

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^__debug__/m/(.*)$', 'debug_toolbar.views.debug_media'),
    url(r'^__debug__/sql_select/$', 'debug_toolbar.views.sql_select', name='sql_select'),
    url(r'^__debug__/sql_explain/$', 'debug_toolbar.views.sql_explain', name='sql_explain'),
    url(r'^__debug__/sql_profile/$', 'debug_toolbar.views.sql_profile', name='sql_profile'),
    url(r'^__debug__/template_source/$', 'debug_toolbar.views.template_source', name='template_source'),
    url(r'^__debug__/logs/(?P<uid>[a-f0-9-]+)/$', 'debug_toolbar.views.report', name="report")
)
