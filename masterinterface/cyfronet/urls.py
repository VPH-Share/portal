from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'cyfronet.views',
    url(r'^cloudmanager/$', 'cloudmanager'),
    url(r'^datamanager/$', 'datamanager'),

    # default rollback to cloudmanager
    url(r'', 'index'),
)
