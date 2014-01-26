# -*- coding: utf-8 -*-
## from django.template import Context, loader
## from django.http import HttpResponse
## from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from settings import MEDIA_ROOT
import os
import shutil
appsfile = os.path.join(os.path.split(__file__)[0],"apps.dat")

def index(request):
    if request.user.is_authenticated():
        msg = 'U bent ingelogd als <i>{0}</i>. '.format(request.user.username)
        msg += 'Klik <a href="/logout/?next=/">hier</a> om uit te loggen'
    else:
        msg = 'U bent niet ingelogd. '
        msg += 'Klik <a href="accounts/login/?next=/">hier</a> om in te loggen,'
        msg += ' <a href="/">hier</a> om terug te gaan naar het begin.'
    msg = request.GET.get("msg","")
    app_list = [{"name": ''},]
    new_apps = []
    with open(appsfile) as apps:
        for app in apps:
            ok,root,name,desc = app.split(";")
            if name == "Demo":
                continue
            if ok == "X":
                for ix, item in enumerate(app_list):
                    inserted = False
                    if item['name'].lower() > name.lower():
                        app_list.insert(ix, {"root": root,"name": name,"desc": desc})
                        inserted = True
                        break
                if not inserted:
                    app_list.append({"root": root,"name": name,"desc": desc})
            else:
                new_apps.append({"root": root,"name": name,"desc": desc})
    app_list.pop(0)
    return render_to_response('index.html',
        {"apps": app_list, "new": new_apps, "msg": msg, "who": request.user})

def new(request):
    "Toon het scherm om een nieuw project op te voeren"
    if not request.user.is_authenticated():
        return HttpResponse('Om een project aan te kunnen vragen moet u zijn ingelogd.'
            '<br/>Klik <a href="/accounts/login/?next=/new/">hier</a> om in te loggen'
            ',  <a href="/">hier</a> om terug te gaan naar het begin.')
    return render_to_response('nieuw.html',{})

@login_required
def add(request):
    "project opvoeren en naar het startscherm ervan"
    # regel toevoegen aan apps.py
    data = request.POST
    name = data.get("name","")
    desc = data.get("desc","")
    with open(appsfile,"a") as _out:
        _out.write(";".join(("_",name,name,desc))+ "\n")
    # email versturen aan site admin voor opvoeren nieuw project
    return HttpResponseRedirect('/?msg=De aanvraag voor het project "{0}" is verstuurd'.format(name))

def login(request):
    return render_to_response('login.html',{})

def log_out(request):
    next = request.GET.get("next","/")
    logout(request)
    return render_to_response("logged_out.html",{"next": "/accounts/login/?next={0}".format(next)})

def viewdoc(request):
    parts = request.path.split('files/')
    return render_to_response(MEDIA_ROOT + parts[1],{})
