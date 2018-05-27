"""Url configuration
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'actiereg._basic.views',
    url(r'^$', 'index'),
    url(r'^index/$', 'index'),
    url(r'^meld/(?P<msg>.+)/$', 'index'),
    url(r'^select/$', 'select'),
    url(r'^setsel/$', 'setsel'),
    url(r'^order/$', 'order'),
    url(r'^setorder/$', 'setorder'),
    url(r'^settings/$', 'settings'),
    url(r'^wijzigusers/$', 'setusers'),
    url(r'^wijzigtabs/$', 'settabs'),
    url(r'^wijzigtypes/$', 'settypes'),
    url(r'^wijzigstats/$', 'setstats'),
    url(r'^koppel/$', 'koppel'),
    url(r'^(?P<actie>nieuw)/$', 'detail'),
    url(r'^(?P<actie>\d+)/$', 'detail'),
    url(r'^(?P<actie>\d+)/detail/$', 'detail'),
    url(r'^(?P<actie>\d+)/mld/(?P<msg>.+)/$', 'detail'),
    ## url(r'^(?P<actie>nieuw)/update/$',  'wijzig'),
    ## url(r'^(?P<actie>\d+)/update/$',  'wijzig'),
    ## url(r'^(?P<actie>(nieuw|\d+))/update/$', 'wijzig'),
    ## url(r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', 'arch'),
    url(r'^(?P<actie>(nieuw|\d+))/(?P<doe>(update|arch|herl))/$', 'wijzig'),
    url(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/$', 'tekst'),
    url(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/meld/(?P<msg>.+)/$', 'tekst'),
    url(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/update/$', 'wijzigtekst'),
    url(r'^(?P<actie>\d+)/voortg/$', 'events'),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>nieuw)/$', 'events'),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>\d+)/$', 'events'),
    url(r'^(?P<actie>\d+)/voortg/meld/(?P<msg>.+)/$', 'events'),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>nieuw)/update/$', 'wijzigevents'),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>\d+)/update/$', 'wijzigevents'),
    url(r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', 'detail'),

    # Uncomment this for admin:
    #     url(r'^admin/', include('django.contrib.admin.urls')),
    )
