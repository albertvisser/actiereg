"""views for Django project pages
"""
## import os
import pathlib
## import shutil
import subprocess
## from django.http import Http404
from django.contrib.auth import logout  # , login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render  # , get_object_or_404
from django.db import connection
## from django.views.decorators.csrf import csrf_exempt
from actiereg.settings import MEDIA_ROOT, SITES  # , DATABASES['default']['NAME']
from actiereg.core import is_admin
from actiereg.newapp import allnew, NewProj
## appsfile = os.path.join(os.path.split(__file__)[0], "apps.dat")
appsfile = pathlib.Path(__file__).parent / "apps.dat"


def index(request, msg=""):
    """Start pagina voor ActieReg
    """
    ## msg = request.GET.get("msg", "")
    if not msg:
        if request.user.is_authenticated():
            msg = 'U bent ingelogd als <i>{}</i>. '.format(request.user.username)
            msg += 'Klik <a href="/logout/?next=/">hier</a> om uit te loggen'
        else:
            msg = ('U bent niet ingelogd. '
                   'Klik <a href="accounts/login/?next=/">hier</a> om in te loggen,'
                   ' <a href="/">hier</a> om terug te gaan naar het begin.')
    app_list = [{"name": ''}]
    new_apps = []
    cursor = connection.cursor()
    with appsfile.open() as apps:
        for app in apps:
            ok, root, name, desc = app.split(";")
            if name == "Demo":
                continue
            if ok == "X":
                doe = "select count(*) from {}_actie".format(root)
                all = cursor.execute(doe).fetchone()[0]
                doe += " where arch = 0"
                all_open = cursor.execute(doe).fetchone()[0]
                doe += " and status_id > 1"
                all_active = cursor.execute(doe).fetchone()[0]
                for ix, item in enumerate(app_list):
                    inserted = False
                    if item['name'].lower() > name.lower():
                        app_list.insert(ix,
                                        {"root": root, "name": name, "desc": desc,
                                         "alle": all, "open": all_open,
                                         "active": all_active})
                        inserted = True
                        break
                if not inserted:
                    app_list.append({"root": root, "name": name, "desc": desc,
                                     "alle": all, "open": all_open, "active": all_active})
            else:
                new_apps.append({"root": root, "name": name, "desc": desc})
    app_list.pop(0)
    return render(request, 'index.html', {"apps": app_list, "new": new_apps,
                                          "msg": msg, "who": request.user})


def new(request):
    "Toon het scherm om een nieuw project op te voeren"
    if not request.user.is_authenticated():
        return HttpResponse('Om een project aan te kunnen vragen moet u zijn ingelogd.<br>'
                            'Klik <a href="/accounts/login/?next=/new/">hier</a> om in te'
                            'loggen, <a href="/">hier</a> om terug te gaan naar het begin.')
    return render(request, 'nieuw.html', {})


def notify_admin(name):
    """admin informeren voor opvoeren nieuw project

    kan aangestuurd worden vanuit MyProjects of door link op admin scherm
    """


def add_from_actiereg(request, name=''):
    "project opvoeren en activeren vanaf admin link"
    if not name:
        return HttpResponseRedirect('/msg/Geen projectnaam opgegeven om te activeren')
    if name == 'all':
        allnew()
    else:
        test = NewProj(name, 'all')
        if test.msg:
            return HttpResponseRedirect('/msg/{}'.format(test.msg))
    subprocess.run(['binfab', 'restart_server:actiereg'])
    # return HttpResponseRedirect('/msg/De wsgi-server wordt gerestart. Ververs de pagina s.v.p.')
    return HttpResponseRedirect('/')


def add_from_doctool(request, proj='', name='', desc=''):
    "project opvoeren en terug naar DocTool"
    with appsfile.open("a") as _out:
        _out.write(";".join(("_", name, name, desc)) + "\n")
    notify_admin(name)
    return HttpResponseRedirect('{}/{}/meld/De aanvraag voor het project "{}"'
                                ' is verstuurd/'.format(SITES['doctool'], proj, name))


@login_required
def add(request):
    "project opvoeren en naar het startscherm ervan"
    # regel toevoegen aan apps.py
    data = request.POST
    name = data.get("name", "")
    desc = data.get("desc", "")
    with appsfile.open("a") as _out:
        _out.write(";".join(("_", name, name, desc)) + "\n")
    notify_admin(name)
    return HttpResponseRedirect(
        '/msg/De aanvraag voor het project "{}" is verstuurd/'.format(name))


def login(request):  # redefinition of unused 'login' from line 5
    """show login form"""
    return render(request, 'login.html', {},)


def log_out(request):
    """log out and show next page if given, else start page
    """
    next = request.GET.get("next", "/")
    logout(request)
    return render(request, "logged_out.html",
                  {"next": "/accounts/login/?next={}".format(next)})


def viewdoc(request):
    """Show an uploaded document (?)
    """
    parts = request.path.split('files/')
    return render(request, MEDIA_ROOT + parts[1], {})
