"""Url configuration
"""
from django.conf.urls import patterns

urlpatterns = patterns(
    'actiereg._basic.views',
    (r'^$', 'index'),
    (r'^index/$', 'index'),
    (r'^meld/(?P<msg>.+)/$', 'index'),
    (r'^select/$', 'select'),
    (r'^setsel/$', 'setsel'),
    (r'^order/$', 'order'),
    (r'^setorder/$', 'setorder'),
    (r'^settings/$', 'settings'),
    (r'^wijzigusers/$', 'setusers'),
    (r'^wijzigtabs/$', 'settabs'),
    (r'^wijzigtypes/$', 'settypes'),
    (r'^wijzigstats/$', 'setstats'),
    (r'^koppel/$', 'koppel'),
    (r'^(?P<actie>nieuw)/$', 'detail'),
    (r'^(?P<actie>\d+)/$', 'detail'),
    (r'^(?P<actie>\d+)/detail/$', 'detail'),
    (r'^(?P<actie>\d+)/mld/(?P<msg>.+)/$', 'detail'),
    ## (r'^(?P<actie>nieuw)/update/$',  'wijzig'),
    ## (r'^(?P<actie>\d+)/update/$',  'wijzig'),
    ## (r'^(?P<actie>(nieuw|\d+))/update/$', 'wijzig'),
    ## (r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', 'arch'),
    (r'^(?P<actie>(nieuw|\d+))/(?P<doe>(update|arch|herl))/$', 'wijzig'),
    (r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/$', 'tekst'),
    (r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/meld/(?P<msg>.+)/$', 'tekst'),
    (r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/update/$', 'wijzigtekst'),
    (r'^(?P<actie>\d+)/voortg/$', 'events'),
    (r'^(?P<actie>\d+)/voortg/(?P<event>nieuw)/$', 'events'),
    (r'^(?P<actie>\d+)/voortg/(?P<event>\d+)/$', 'events'),
    (r'^(?P<actie>\d+)/voortg/meld/(?P<msg>.+)/$', 'events'),
    (r'^(?P<actie>\d+)/voortg/(?P<event>nieuw)/update/$', 'wijzigevents'),
    (r'^(?P<actie>\d+)/voortg/(?P<event>\d+)/update/$', 'wijzigevents'),
    (r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', 'detail'),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
    )
