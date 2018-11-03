"""Url configuration
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^index/$', views.index),
    url(r'^meld/(?P<msg>.+)/$', views.index),
    url(r'^select/$', views.select),
    url(r'^setsel/$', views.setsel),
    url(r'^order/$', views.order),
    url(r'^setorder/$', views.setorder),
    url(r'^settings/$', views.settings),
    url(r'^wijzigusers/$', views.setusers),
    url(r'^wijzigtabs/$', views.settabs),
    url(r'^wijzigtypes/$', views.settypes),
    url(r'^wijzigstats/$', views.setstats),
    url(r'^koppel/$', views.koppel),
    url(r'^(?P<actie>nieuw)/$', views.detail),
    url(r'^(?P<actie>\d+)/$', views.detail),
    url(r'^(?P<actie>\d+)/detail/$', views.detail),
    url(r'^(?P<actie>\d+)/mld/(?P<msg>.+)/$', views.detail),
    ## url(r'^(?P<actie>nieuw)/update/$',  views.wijzig),
    ## url(r'^(?P<actie>\d+)/update/$',  views.wijzig),
    ## url(r'^(?P<actie>(nieuw|\d+))/update/$', views.wijzig),
    ## url(r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', views.arch),
    url(r'^(?P<actie>(nieuw|\d+))/(?P<doe>(update|arch|herl))/$', views.wijzig),
    url(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/$', views.tekst),
    url(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/meld/(?P<msg>.+)/$', views.tekst),
    url(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/update/$', views.wijzigtekst),
    url(r'^(?P<actie>\d+)/voortg/$', views.events),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>nieuw)/$', views.events),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>\d+)/$', views.events),
    url(r'^(?P<actie>\d+)/voortg/meld/(?P<msg>.+)/$', views.events),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>nieuw)/update/$', views.wijzigevents),
    url(r'^(?P<actie>\d+)/voortg/(?P<event>\d+)/update/$', views.wijzigevents),
    url(r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', views.detail),

    # Uncomment this for admin:
    #     url(r'^admin/', include('django.contrib.admin.urls')),
]
