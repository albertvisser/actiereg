from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^probreg/', include('probreg.foo.urls')),
    (r'^$','probreg.views.index'),
    (r'^new/$','probreg.views.new'),
    (r'^add/$','probreg.views.add'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$','probreg.views.log_out'),
    (r'^basic/', include('probreg._basic.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
