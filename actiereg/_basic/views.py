"""Views for the various pages

Since these are copied for each project, these call routines reside (and are
documented) in a separate module
"""
from django.contrib.auth.decorators import login_required
import actiereg._basic.models as my
from actiereg import core
ROOT = "basic"
NAME = "demo"


def koppel(request):
    "redirect"
    return core.koppel(ROOT, my, request)


@login_required
def index(request, msg=''):
    "redirect"
    return core.index(ROOT, NAME, my, request, msg)


@login_required
def settings(request):
    "redirect"
    return core.settings(ROOT, NAME, my, request)


@login_required
def setusers(request):
    "redirect"
    return core.setusers(ROOT, my, request)


@login_required
def settabs(request):
    "redirect"
    return core.settabs(ROOT, my, request)


@login_required
def settypes(request):
    "redirect"
    return core.settypes(ROOT, my, request)


@login_required
def setstats(request):
    "redirect"
    return core.setstats(ROOT, my, request)


@login_required
def select(request):
    "redirect"
    return core.select(ROOT, NAME, my, request)


@login_required
def setsel(request):
    "redirect"
    return core.setsel(ROOT, my, request)


@login_required
def order(request):
    "redirect"
    return core.order(ROOT, NAME, my, request)


@login_required
def setorder(request):
    "redirect"
    return core.setorder(ROOT, my, request)


@login_required
def detail(request, actie="", msg=""):
    "redirect"
    return core.detail(ROOT, NAME, my, request, actie, msg)


@login_required
def wijzig(request, actie="", doe=""):
    "redirect"
    return core.wijzig(ROOT, my, request, actie, doe)


@login_required
def tekst(request, actie="", page="", msg=""):
    "redirect"
    return core.tekst(ROOT, NAME, my, request, actie, page, msg)


@login_required
def wijzigtekst(request, actie="", page=""):
    "redirect"
    return core.wijzigtekst(ROOT, my, request, actie, page)


@login_required
def events(request, actie="", event="", msg=""):
    "redirect"
    return core.events(ROOT, NAME, my, request, actie, event, msg)


@login_required
def wijzigevents(request, actie="", event=""):
    "redirect"
    return core.wijzigevents(ROOT, my, request, actie, event)
