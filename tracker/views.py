"""views for Django project pages
"""
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import tracker.models as my
from tracker import core
from actiereg.settings import SITES
default_admin = my.User.objects.get(username='avisser')

def index(request, msg=""):
    """Start pagina voor ActieReg
    """
    if not msg:
        msg = request.GET.get("msg", "")
    if msg:
        msg += '<br/><br/>'
    user = request.GET.get("user", "") or request.user
    msg += core.get_appropriate_login_message(user)
    # if not user.is_authenticated:
    #     msg += ' <a href="/">hier</a> om terug te gaan naar het begin.'
    app_list = []
    new_apps = []
    for project in my.Project.objects.all():
        app = {'root': project.id, 'name': project.name, 'desc': project.description,
               'alle': 0, 'open': 0, 'active': 0}
        for actie in project.acties.all():
            app['alle'] += 1
            if not actie.arch:
                app['open'] += 1
                if actie.status.value > 1:
                    app['active'] += 1
        app_list.append(app)
    return render(request, 'index.html', {"apps": sorted(app_list, key=lambda x: x['name']),
                                          "new": new_apps, "msg": msg, "who": user})


@login_required
def log_out(request):
    """log out and show next page if given, else start page
    """
    next_ = request.GET.get("next", "/")
    logout(request)
    return render(request, "logged_out.html", {"next": f"/accounts/login/?next={next_}"})


def new_project(request):
    "Toon het scherm om een nieuw project op te voeren"
    if not request.user.is_authenticated:
        return core.not_logged_in_message('een project aan te kunnen maken')
    page_data = core.build_pagedata_for_newproj()
    return render(request, 'nieuw.html', page_data)


@login_required
def add_project(request):
    "project opvoeren en naar het startscherm ervan"
    data = request.POST
    name = data.get("name", "")
    desc = data.get("desc", "")
    admins = data.get("admin", [])
    core.add_project(name, desc, admins)
    return HttpResponseRedirect('/msg/project aangemaakt/')


def add_from_doctool(request, proj='', name='', desc=''):
    "project opvoeren en terug naar DocTool"
    projectid = core.add_project(name, desc, [default_admin])
    return HttpResponseRedirect(f"{SITES['doctool']}/{proj}/meld/Project {name}"
                                f" is aangemaakt met id {projectid}/")


def show_project(request, proj, msg=''):
    """samenstellen van de lijst met acties:
    - selecteer en sorteer de acties volgens de voor de user vastgelegde regels
      (het selecteren op actienummer en beschrijving is nog even niet actief)
    - de soort user wordt meegegeven aan het scherm om indien nodig diverse knoppen
        te verbergen
    """
    if not msg:
        msg = core.get_appropriate_login_message(request.user, proj)
        if request.user.is_authenticated:
            msg += "Klik op een actienummer om de details te bekijken."
    page_data = core.build_pagedata_for_project(request, proj, msg)
    return render(request, 'tracker/index.html', page_data)


@login_required
def show_settings(request, proj):
    """settings scherm opbouwen
    """
    project = my.Project.objects.get(pk=proj)
    if not core.is_admin(project, request.user):
        return core.no_authorization_message('instellingen te wijzigen', proj)
    page_data = core.build_pagedata_for_settings(request, proj)
    return render(request, 'tracker/settings.html', page_data)


@login_required
def setusers(request, proj):
    """users aan project koppelen
    """
    project = my.Project.objects.get(pk=proj)
    if not core.is_admin(project, request.user):
        return core.no_authorization_message('instellingen te wijzigen', proj)
    core.set_users(request, proj)
    return HttpResponseRedirect(f"/{proj}/settings/")


@login_required
def setadmins(request, proj):
    """admins aan project koppelen
    """
    project = my.Project.objects.get(pk=proj)
    if not core.is_admin(project, request.user):
        return core.no_authorization_message('instellingen te wijzigen', proj)
    core.set_admins(request, proj)
    return HttpResponseRedirect(f"/{proj}/settings/")


@login_required
def settabs(request, proj):
    """tab titels aanpassen en terug naar settings scherm
    """
    project = my.Project.objects.get(pk=proj)
    if not core.is_admin(project, request.user):
        return core.no_authorization_message('instellingen te wijzigen', proj)
    core.set_tabs(request)
    return HttpResponseRedirect(f"/{proj}/settings/")


@login_required
def settypes(request, proj):
    """soort-gegevens aanpassen en terug naar settings scherm
    """
    project = my.Project.objects.get(pk=proj)
    if not core.is_admin(project, request.user):
        return core.no_authorization_message('instellingen te wijzigen', proj)
    core.set_types(request, proj)
    return HttpResponseRedirect(f"/{proj}/settings/")


@login_required
def setstats(request, proj):
    """status-gegevens aanpassen en terug naar settings scherm
    """
    project = my.Project.objects.get(pk=proj)
    if not core.is_admin(project, request.user):
        return core.no_authorization_message('instellingen te wijzigen', proj)
    core.set_stats(request, proj)
    return HttpResponseRedirect(f"/{proj}/settings/")


@login_required
def show_selection(request, proj):
    "presenteer selectie mogelijkheden"
    # if request.user.is_authenticated:  # niet nodig met die decorator?
    msg = core.logged_in_message(request, proj)
    # else:
    #     core.not_logged_in_message('de selectie voor dit scherm te mogen wijzigen', proj)
    # project = my.Project.objects.get(pk=proj)
    page_data, msg = core.build_pagedata_for_selection(request, proj, msg)
    if msg:
        return HttpResponse(msg)
    return render(request, 'tracker/select.html', page_data)


@login_required
def setselection(request, proj):
    "leg de selecite vast"
    core.setselection(request, proj)
    return HttpResponseRedirect(f"/{proj}/meld/De selectie is gewijzigd./")


@login_required
def show_ordering(request, proj):
    "presenteer sorterings mogelijkheden"
    # if request.user.is_authenticated:  # niet nodig met die decorator?
    msg = core.logged_in_message(request, proj)
    # else:
    #     core.not_logged_in_message('de sortering voor dit scherm te mogen wijzigen', proj)
    return render(request, 'tracker/order.html', core.build_pagedata_for_ordering(request, proj, msg))


@login_required
def setordering(request, proj):
    "leg de soertering vast"
    core.setordering(request, proj)
    return HttpResponseRedirect(f"/{proj}/meld/De sortering is gewijzigd./")


@login_required
def new_action(request, proj, msg=''):
    "toon scherm voor opvoeren nieuwe actie"
    return render(request, 'tracker/actie.html',
                  core.build_pagedata_for_detail(request, proj, 'new', msg))


@login_required
def show_action(request, proj, actie, msg=''):
    "toon scherm met gegevens van bestaande actie"
    return render(request, 'tracker/actie.html',
                  core.build_pagedata_for_detail(request, proj, actie, msg))


@login_required
def add_action(request, proj):
    "voer nieuwe actie op in de database en ga naar detailscherm"
    project = my.Project.objects.get(pk=proj)
    if not core.is_user(project, request.user):  # and not is_admin(project, request.user):
        return core.no_authorization_message("acties op te voeren", proj)
    return HttpResponseRedirect(core.wijzig_detail(request, project, 'nieuw'))


@csrf_exempt
def add_action_from_doctool(request, proj):  # Attention: signature changed from root, my, request
    """doorkoppeling vanuit doctool: actie opvoeren en terugkeren
    """
    data = request.POST
    vervolg = data.get("hFrom", "")
    usernaam = data.get("hUser", "")
    actnum = data.get("tActie", "")
    if actnum:
        response = core.copy_existing_action_from_here(proj, actnum, usernaam, vervolg)
    else:
        response = core.add_new_action_on_both_sides(proj, data, usernaam, vervolg)
    return HttpResponseRedirect(response)


@login_required
def update_action(request, proj, actie):
    "wijzig actie in de database en ga naar detailscherm"
    project = my.Project.objects.get(pk=proj)
    if not core.is_user(project, request.user):  # and not is_admin(project, request.user):
        return core.no_authorization_message("acties te wijzigen", proj)
    return HttpResponseRedirect(core.wijzig_detail(request, project, actie))


@login_required
def show_meld(request, proj, actie, msg=""):
    "toon scherm voor wijzigen melding"
    return render(request, 'tracker/tekst.html',
                  core.build_pagedata_for_tekstpage(request, proj, actie, 'meld', msg))


@login_required
def show_oorz(request, proj, actie, msg=""):
    "toon scherm voor wijzigen oorzaak"
    return render(request, 'tracker/tekst.html',
                  core.build_pagedata_for_tekstpage(request, proj, actie, 'oorz', msg))


@login_required
def show_opl(request, proj, actie, msg=""):
    "toon scherm voor wijzigen oplossing"
    return render(request, 'tracker/tekst.html',
                  core.build_pagedata_for_tekstpage(request, proj, actie, 'opl', msg))


@login_required
def show_verv(request, proj, actie, msg=""):
    "toon scherm voor wijzigen vervolg"
    return render(request, 'tracker/tekst.html',
                  core.build_pagedata_for_tekstpage(request, proj, actie, 'verv', msg))


@login_required
def update_meld(request, proj, actie):
    "wijzig melding in de database en ga terug naar scherm"
    return HttpResponseRedirect(core.wijzig_tekstpage(request, proj, actie, 'meld'))


@login_required
def update_oorz(request, proj, actie):
    "wijzig oorzaak in de database en ga terug naar scherm"
    return HttpResponseRedirect(core.wijzig_tekstpage(request, proj, actie, 'oorz'))


@login_required
def update_opl(request, proj, actie):
    "wijzig oplossing in de database en ga terug naar scherm"
    return HttpResponseRedirect(core.wijzig_tekstpage(request, proj, actie, 'opl'))


@login_required
def update_verv(request, proj, actie):
    "wijzig vervolg in de database en ga terug naar scherm"
    return HttpResponseRedirect(core.wijzig_tekstpage(request, proj, actie, 'verv'))


@login_required
def show_events(request, proj, actie, msg=""):
    "toon scherm voor (wijzigen/toevoegen) events"
    return render(request, 'tracker/voortgang.html',
                  core.build_pagedata_for_events(request, proj, actie, msg=msg))


@login_required
def new_event(request, proj, actie):
    "Rzet scherm open voor toevoegen"
    return render(request, 'tracker/voortgang.html',
                  core.build_pagedata_for_events(request, proj, actie, event='nieuw'))


@login_required
def edit_event(request, proj, actie, event):
    "Rzet scherm open voor wijzigen"
    return render(request, 'tracker/voortgang.html',
                  core.build_pagedata_for_events(request, proj, actie, event=event))


@login_required
def add_event(request, proj, actie):
    "voeg event toe in de database en ga terug naar events scherm"
    return HttpResponseRedirect(core.wijzig_events(request, proj, actie, 'nieuw'))


@login_required
def update_event(request, proj, actie, event):
    "wijzig event in de database en ga terug naar events scherm"
    return HttpResponseRedirect(core.wijzig_events(request, proj, actie, event))
