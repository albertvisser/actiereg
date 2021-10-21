"""Url configuration
"""
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index),
    path('index/', views.index),
    path('meld/<msg>/', views.index),
    path('select/', views.select),
    path('setsel/', views.setsel),
    path('order/', views.order),
    path('setorder/', views.setorder),
    path('settings/', views.settings),
    path('wijzigusers/', views.setusers),
    path('wijzigtabs/', views.settabs),
    path('wijzigtypes/', views.settypes),
    path('wijzigstats/', views.setstats),
    path('koppel/', views.koppel),
    re_path(r'^(?P<actie>(nieuw|\d+))/$', views.detail),
    # path(r'^(?P<actie>\d+)/$', views.detail),
    path('<int:actie>/detail/', views.detail),
    path('<int:actie>/mld/<msg>/', views.detail),
    ## path(r'^(?P<actie>nieuw)/update/$',  views.wijzig),
    ## path(r'^(?P<actie>\d+)/update/$',  views.wijzig),
    ## path(r'^(?P<actie>(nieuw|\d+))/update/$', views.wijzig),
    ## path(r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', views.arch),
    ## path(r'^(?P<actie>\d+)/(?P<arch>(arch|herl))/$', views.detail),
    re_path(r'^(?P<actie>(nieuw|\d+))/(?P<doe>(update|arch|herl))/$', views.wijzig),
    re_path(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/$', views.tekst),
    re_path(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/meld/(?P<msg>.+)/$', views.tekst),
    re_path(r'^(?P<actie>\d+)/(?P<page>(meld|oorz|opl|verv))/update/$', views.wijzigtekst),
    path('<int:actie>/voortg/', views.events),
    re_path(r'^(?P<actie>(nieuw|\d+))/voortg/(?P<event>nieuw)/$', views.events),
    #  path('(<actie>\d+)/voortg/(?P<event>\d+)/$', views.events),
    path('<int:actie>/voortg/meld/<msg>/', views.events),
    # path('(<actie>)/voortg/(?P<event>nieuw)/update/$', views.wijzigevents),
    # path('(<actie>)/voortg/(?P<event>\d+)/update/$', views.wijzigevents),
    re_path(r'^(?P<actie>\d+)/voortg/(?P<event>(nieuw|\d+))/update/$', views.wijzigevents),

    # Uncomment this for admin:
    #     path(r'^admin/', include('django.contrib.admin.urls')),
]
