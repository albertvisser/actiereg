"""loaddata - submodule voor newapp.py
"""
import sqlite3 as sql
import sys
import os
from django.contrib.auth.models import User  # , Group
sys.path.append("/home/albert/django/actiereg")
os.environ["DJANGO_SETTINGS_MODULE"] = 'actiereg.settings'
import settings
import actiereg._basic.models as my
sys.path.append("/home/albert/projects/probreg")
from probreg import dml
TABS = ['index', 'detail', 'meld', 'oorz', 'opl', 'verv', 'voortg']
TITLES = ["Lijst", "Titel/Status", "Probleem/Wens", "Oorzaak/Analyse", "Oplossing",
          "Vervolgactie", "Voortgang"]


def loadsett(fnaam):
    """Importeer settings van probreg project in actiereg project
    """
    data = dml.Settings(fnaam)
    data.read()
    my.Status.objects.all().delete()
    for stat, gegs in data.stat.items():
        title, order = gegs
        my.Status.objects.create(value=stat, title=title, order=order)
    my.Soort.objects.all().delete()
    for srt, gegs in data.cat.items():
        title, order = gegs
        my.Soort.objects.create(value=srt, title=title, order=order)
    my.Page.objects.all().delete()
    for value, title in data.kop.items():
        order = int(value)
        link = TABS[order]
        my.Page.objects.create(order=order, link=link, title=title)
    while order < 6:
        order += 1
        link = TABS[order]
        title = TITLES[order]
        try:
            my.Page.objects.create(order=order, link=link, title=title)
        except sql.IntegrityError:  # duplicate "order" - mag genegeerd worden
            pass


def loaddata(fnaam, dbnaam):
    """importeer data van probreg project in actiereg project
    """
    con = sql.connect(settings.DATABASE_NAME)
    data = [actie[0] for actie in dml.Acties(fnaam, arch="alles").lijst]
    for item in data:
        actie = dml.Actie(fnaam, item)
        try:
            about, what = actie.titel.split(": ", 1)
        except ValueError:
            try:
                about, what = actie.titel.split(" - ", 1)
            except ValueError:
                about = ""
                what = actie.titel
        if actie.status == "":
            actie.status = " "
        nieuw = my.Actie.objects.create(nummer=actie.id,
                                        starter=User.objects.get(pk=1),
                                        about=about,
                                        title=what,
                                        lasteditor=User.objects.get(pk=1),
                                        status=my.Status.objects.get(value=actie.status),
                                        soort=my.Soort.objects.get(value=actie.soort),
                                        behandelaar=User.objects.get(pk=1),
                                        gewijzigd=actie.datum,
                                        arch=actie.arch,
                                        melding=actie.melding,
                                        oorzaak=actie.oorzaak,
                                        oplossing=actie.oplossing,
                                        vervolg=actie.vervolg)
        # datums goed zetten
        cmd = "update {}_actie set start = ?, gewijzigd = ? where id = ?".format(
            dbnaam)
        con.execute(cmd, (actie.datum, actie.updated, nieuw.id))
        con.commit()
        for start, text in actie.events:
            if not text:
                text = ""
            ok = my.Event.objects.create(actie=nieuw,
                                         start=start,
                                         starter=User.objects.get(pk=1),
                                         text=text)
            # datums goed zetten
            cmd = "update {}_event set start = ? where id = ?".format(dbnaam)
            con.execute(cmd, (start, ok.id))
            con.commit()
