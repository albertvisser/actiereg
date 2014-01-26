from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^actiereg/', include('actiereg.foo.urls')),
    (r'^$','actiereg.views.index'),
    (r'^new/$','actiereg.views.new'),
    (r'^add/$','actiereg.views.add'),
    (r'^addext/$','actiereg.views.add_from_doctool'),
    (r'^addext/(?P<proj>\d+)/(?P<name>\w+)/(?P<desc>.+)/$',
        'actiereg.views.add_from_doctool'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/profile/$', 'actiereg.views.index'),
    (r'^logout/$','actiereg.views.log_out'),
    (r'^basic/', include('actiereg._basic.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', include(admin.site.urls)),
)
