from django.urls import path, include
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('msg/<msg>/', views.index, name='index_with_message'),
    path('new/', views.new_project, name='new'),
    path('add/', views.add_project, name='add'),
    # path('addext/', views.add_from_doctool, name='add_from_doctool'),
    # path('addext/<int:proj>/<name>/<desc>/', views.add_from_doctool, name='add_from_doctool'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    # path('accounts/profile/', views.index, name='index'),
    path('logout/', views.log_out, name='log_out'),
    path('<int:proj>/', include([
        path('', views.show_project),
        path('index/', views.show_project),
        path('meld/<msg>/', views.show_project),
        path('select/', views.show_selection),
        path('setsel/', views.setselection),
        path('order/', views.show_ordering),
        path('setorder/', views.setordering),
        path('settings/', views.show_settings),
        path('wijzigusers/', views.setusers),
        path('wijzigtabs/', views.settabs),
        path('wijzigtypes/', views.settypes),
        path('wijzigstats/', views.setstats),
        # path('koppel/', views.add_action_from_doctool),
        path('nieuw/', views.new_action),
        path('nieuw/update/', views.add_action),
        ])),
    path('<int:proj>/<int:actie>/', include([
        path('', views.show_action),
        path('detail/', views.show_action),
        path('mld/<msg>/', views.show_action),
        path('update/', views.update_action),
        # misschien ook:
        # path('arch/', views.archiveer -> views.update_action (was: wijzig)
        # path('herl/', views.herleef -> views.update_action (was: wijzig)
        path('meld/', views.show_meld),
        path('meld/mld/<msg>/', views.show_meld),
        path('meld/update/', views.update_meld),
        path('oorz/', views.show_oorz),
        path('oorz/meld/<msg>/', views.show_oorz),
        path('oorz/update/', views.update_oorz),
        path('opl/', views.show_opl),
        path('opl/meld/<msg>/', views.show_opl),
        path('opl/update/', views.update_opl),
        path('verv/', views.show_verv),
        path('verv/meld/<msg>/', views.show_verv),
        path('verv/update/', views.update_verv),
        path('voortg/', views.show_events),
        path('voortg/meld/<msg>/', views.show_events),
        path('voortg/nieuw/', views.new_event),
        path('voortg/nieuw/update/', views.add_event),
        path('voortg/<int:event>/', views.edit_event),
        path('voortg/<int:event>/update/', views.update_event),
        ])),
    ]
