"""loaddata - submodule voor newapp.py"""

import sys
import os
sys.path.append("/home/albert/django")
os.environ["DJANGO_SETTINGS_MODULE"] = 'actiereg.settings'
import sqlite3 as sql
import settings
import actiereg._basic.models as my
from django.contrib.auth.models import User, Group
sys.path.append("/home/albert/probreg")
from probreg import dml

def loadsett(fnaam):
    data = dml.Settings(fnaam)
    data.read()
    # pp.pprint(data.stat)
    my.Status.objects.all().delete()
    for stat,gegs in data.stat.items():
        title,order = gegs
        my.Status.objects.create(value=stat,title=title,order=order)
    # pp.pprint(data.cat)
    my.Soort.objects.all().delete()
    for srt,gegs in data.cat.items():
        title,order = gegs
        my.Soort.objects.create(value=srt,title=title,order=order)
    # pp.pprint(data.kop)
    my.Page.objects.all().delete()
    for value,title in data.kop.items():
        order = int(value)
        link = ['index','detail','meld','oorz','opl','verv','voortg'][order]
        my.Page.objects.create(order=order,link=link,title=title)
    while order < 6:
        order += 1
        link = ['index','detail','meld','oorz','opl','verv','voortg'][order]
        title = ["Lijst", "Titel/Status", "Probleem/Wens", "Oorzaak/Analyse",
                 "Oplossing", "Vervolgactie", "Voortgang"][order]
        try:
            my.Page.objects.create(order=order,link=link,title=title)
        except sql.IntegrityError: # duplicate "order" - mag genegeerd worden
            pass

def loaddata(fnaam, dbnaam):
    con = sql.connect(settings.DATABASE_NAME)
    data = [actie[0] for actie in dml.Acties(fnaam, arch="alles").lijst]
    for item in data:
        actie = dml.Actie(fnaam, item)
        try:
            about, what = actie.titel.split(": ",1)
        except ValueError:
            try:
                about, what = actie.titel.split(" - ",1)
            except ValueError:
                about = ""
                what = actie.titel
        if actie.status == "":
            actie.status = " "
        nieuw = my.Actie.objects.create(
            nummer = actie.id,
            starter = User.objects.get(pk=1),
            about = about,
            title = what,
            lasteditor = User.objects.get(pk=1),
            status = my.Status.objects.get(value=actie.status),
            soort = my.Soort.objects.get(value=actie.soort),
            behandelaar = User.objects.get(pk=1),
            gewijzigd = actie.datum,
            arch = actie.arch,
            melding = actie.melding,
            oorzaak = actie.oorzaak,
            oplossing = actie.oplossing,
            vervolg = actie.vervolg,
            )
        # datums goed zetten
        cmd = "update {0}_actie set start = ?, gewijzigd = ? where id = ?".format(dbnaam)
        con.execute(cmd, (actie.datum, actie.updated, nieuw.id))
        con.commit()
        for start,text in actie.events:
            if not text:
                text = ""
            ok= my.Event.objects.create(
                actie = nieuw,
                start = start,
                starter = User.objects.get(pk=1),
                text = text,
                )
            # datums goed zetten
            cmd = "update {0}_event set start = ? where id = ?".format(dbnaam)
            con.execute(cmd, (start, ok.id))
            con.commit()