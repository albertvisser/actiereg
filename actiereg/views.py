"""views for Django project pages
"""
## import os
import pathlib
## import shutil
## from django.template import Context, loader
## from django.http import HttpResponse
## from django.http import Http404
from django.contrib.auth import login, logout  # , authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response  # , get_object_or_404
from django.db import connection
from django.template import RequestContext
## from django.views.decorators.csrf import csrf_exempt
from actiereg.settings import MEDIA_ROOT, SITES  # , DATABASES['default']['NAME']
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
    return render_to_response('index.html', {"apps": app_list, "new": new_apps,
                                             "msg": msg, "who": request.user},
                              context_instance=RequestContext(request))


def new(request):
    "Toon het scherm om een nieuw project op te voeren"
    if not request.user.is_authenticated():
        return HttpResponse('Om een project aan te kunnen vragen moet u zijn ingelogd.<br>'
                            'Klik <a href="/accounts/login/?next=/new/">hier</a> om in te'
                            'loggen, <a href="/">hier</a> om terug te gaan naar het begin.')
    return render_to_response('nieuw.html', {},
                              context_instance=RequestContext(request))


def notify_admin():
    """email versturen aan site admin voor opvoeren nieuw project
    """
    pass


def add_from_doctool(request, proj='', name='', desc=''):
    "project opvoeren en terug naar DocTool"
    ## data = request.GET
    ## doc = data.get("from", "")
    ## name = data.get("name", "")
    ## desc = data.get("desc", "")
    ## return HttpResponse("{0} {1} {2}".format(doc, name, desc))
    with appsfile.open("a") as _out:
        _out.write(";".join(("_", name, name, desc)) + "\n")
    notify_admin()
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
    notify_admin()
    return HttpResponseRedirect(
        '/msg/De aanvraag voor het project "{}" is verstuurd/'.format(name))


def login(request):  # redefinition of unused 'login' from line 5
    """show login form"""
    return render_to_response('login.html', {},
                              context_instance=RequestContext(request))


def log_out(request):
    """log out and show next page if given, else start page
    """
    next = request.GET.get("next", "/")
    logout(request)
    return render_to_response("logged_out.html",
                              {"next": "/accounts/login/?next={}".format(next)})


def viewdoc(request):
    """Show an uploaded document (?)
    """
    parts = request.path.split('files/')
    return render_to_response(MEDIA_ROOT + parts[1], {})
