"""views for Django project pages
"""
# import os
import pathlib
# import shutil
# import subprocess
# from django.http import Http404
from django.contrib.auth import logout  # , login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render  # , get_object_or_404
from django.db import connection
# from django.views.decorators.csrf import csrf_exempt
from actiereg.settings import MEDIA_ROOT, SITES  # , DATABASES['default']['NAME']
# from actiereg.core import is_admin
# from actiereg.newapp import allnew, NewProj
# appsfile = os.path.join(os.path.split(__file__)[0], "apps.dat")
appsfile = pathlib.Path(__file__).parent / "apps.dat"


def index(request, msg=""):
    """Start pagina voor ActieReg
    """
    if not msg:
        msg = request.GET.get("msg", "")
    if msg:
        msg += '<br/><br/>'
    user = request.GET.get("user", "") or request.user
    if user and user.is_authenticated:
        msg += f'U bent ingelogd als <i>{user.username}</i>.'
        msg += ' Klik <a href="/logout/?next=/">hier</a> om uit te loggen'
    else:
        msg += ('U bent niet ingelogd.'
                ' Klik <a href="accounts/login/?next=/">hier</a> om in te loggen,'
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
                doe = f"select count(*) from {root}_actie"
                all_items = cursor.execute(doe).fetchone()[0]
                doe += " where arch = 0"
                all_open = cursor.execute(doe).fetchone()[0]
                doe += " and status_id > 1"
                all_active = cursor.execute(doe).fetchone()[0]
                for ix, item in enumerate(app_list):
                    inserted = False
                    if item['name'].lower() > name.lower():
                        app_list.insert(ix,
                                        {"root": root, "name": name, "desc": desc,
                                         "alle": all_items, "open": all_open,
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
                                          "msg": msg, "who": user})


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
    text = ('Deze view werkt maar gedeeltelijk,',
            f' stop de server en voer `python newapp.py {name}` handmatig uit')
    return HttpResponseRedirect(f'/msg/{text}/')
    # if name == 'all':
    #     result = allnew()
    #     if result:
    #         return HttpResponseRedirect('/msg/{}/'.format(result))
    # else:
    #     build = NewProj(name, 'all')
    #     if build.msg:
    #         return HttpResponseRedirect('/msg/{}/'.format(test.msg))
    #     build.do_stuff()

    # result = subprocess.run(['binfab', 'server.restart' '-n' 'actiereg']) # FIXME: gebruikt sudo
    # # return HttpResponseRedirect('/msg/De wsgi-server wordt gerestart. Ververs de pagina s.v.p.')
    # if result.returncode:
    #     return HttpResponse('restarting server ended with rc {} {}'.format(result.returncode,
    #                                                                        result.stderr))
    # return HttpResponseRedirect('/msg/project(en) geactiveerd/')


def add_from_doctool(request, proj='', name='', desc=''):
    "project opvoeren en terug naar DocTool"
    with appsfile.open("a") as _out:
        _out.write(";".join(("_", name, name, desc)) + "\n")
    notify_admin(name)
    return HttpResponseRedirect(f"{SITES['doctool']}/{proj}/meld/De aanvraag"
                                f' voor het project "{name}" is verstuurd/')


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
    return HttpResponseRedirect('/msg/De aanvraag voor het project "{name}" is verstuurd/')


def login(request):  # redefinition of unused 'login' from line 5
    """show login form"""
    return render(request, 'login.html', {},)


def log_out(request):
    """log out and show next page if given, else start page
    """
    next = request.GET.get("next", "/")
    logout(request)
    return render(request, "logged_out.html", {"next": f"/accounts/login/?next={next}"})


def viewdoc(request):
    """Show an uploaded document (?)
    """
    parts = request.path.split('files/')
    return render(request, MEDIA_ROOT + parts[1], {})
