from django.urls import include, path
## from django.views.generic.simple import redirect_to
from django.contrib.auth.views import LoginView
from . import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('', views.index),
    path('msg/<slug:msg>/', views.index),
    path('new/', views.new),
    path('add/', views.add),
    # path('addint/<slug:name>/', views.add_from_actiereg),
    path('addext/', views.add_from_doctool),
    path('addext/<int:proj>/<slug:name>/<desc>/', views.add_from_doctool),
    path('accounts/login/', LoginView.as_view()),
    path('accounts/profile/', views.index),
    path('logout/', views.log_out),
    path('basic/', include('actiereg._basic.urls')),
    path('probreg_pc/', include('actiereg.probreg_pc.urls')),
    path('jvsdoe/', include('actiereg.jvsdoe.urls')),
    path('leesjcl/', include('actiereg.leesjcl.urls')),
    path('actiereg_web/', include('actiereg.actiereg_web.urls')),
    path('doctool/', include('actiereg.doctool.urls')),
    path('afrift/', include('actiereg.afrift.urls')),
    path('htmledit/', include('actiereg.htmledit.urls')),
    path('tcmdrkeys/', include('actiereg.tcmdrkeys.urls')),
    path('versies/', include('actiereg.versies.urls')),
    path('xmledit/', include('actiereg.xmledit.urls')),
    path('apropos/', include('actiereg.apropos.urls')),
    path('doctree/', include('actiereg.doctree.urls')),
    path('todo/', include('actiereg.todo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    path('admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),
]
