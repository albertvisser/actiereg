"""Core functions for page views
"""
# import datetime as dt
import contextlib
import django.utils as dt
from django.http import HttpResponse  # , HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Q  # wordt gebruikt bij samenstellen filterstring (get_acties)
# from django.contrib import admin
import django.contrib.auth.models as aut
import tracker.models as my

UIT_DOCTOOL = "Actie opgevoerd vanuit Doctool"


def add_project(name, desc):
    "nieuw project aanmaken"
    newproj = my.Project.objects.create(name=name, description=desc)
    if my.Page.objects.count() == 0:
        add_default_pages()
    add_default_soorten(newproj)
    add_default_statussen(newproj)
    return newproj.id


def add_default_pages():
    """voer standaard pagina's op voor alle projecten
    """
    for x, y, z in [("index", 0, "lijst"),
                    ("detail", 1, "titel/status"),
                    ("meld", 2, "probleem/wens"),
                    ("oorz", 3, "oorzaak/analyse"),
                    ("opl", 4, "oplossing"),
                    ("verv", 5, "vervolgactie"),
                    ("voortg", 6, "voortgang")]:
        my.Page.objects.create(link=x, order=y, title=z)


def add_default_soorten(project):
    """voor standaard set soorten op voor een nieuw project
    """
    for x, y, z in [(0, " ", "onbekend"),
                    (1, "P", "probleem"),
                    (2, "W", "wens"),
                    (3, "V", "vraag"),
                    (4, "I", "idee"),
                    (5, "F", "diverse informatie")]:
        my.Soort.objects.create(project=project, order=x, value=y, title=z)


def add_default_statussen(project):
    """voor standaard set statussen op voor een nieuw project
    """
    for x, y, z in [(0, 0, "gemeld"),
                    (1, 1, "in behandeling"),
                    (2, 2, "oplossing controleren"),
                    (3, 3, "nog niet opgelost"),
                    (4, 4, "afgehandeld - opgelost"),
                    (5, 5, "afgehandeld - vervolg")]:
        my.Status.objects.create(project=project, order=x, value=y, title=z)


def build_pagedata_for_project(request, proj, msg):
    "bouw het scherm op dat acties bij het project toont"
    project = my.Project.objects.get(pk=proj)
    page_data = {"title": "Actielijst",
                 "page_titel": "lijst",
                 "name": project.name,
                 "root": proj,
                 "pages": my.Page.objects.all().order_by('order'),
                 "admin": is_admin(project, request.user),
                 "msg": msg,
                 'readonly': determine_readonly(project, request.user)}
    data = get_acties(project, request.user.id)
    if data:
        # page_data["order"] = order - werkt in het origineel dankzij een view die order heet
        page_data["acties"] = data
        # page_data["geen_items"] = "Geen acties die aan deze criteria voldoen"
    else:
        page_data["geen_items"] = "<p>Geen acties voor de huidige selectie en user</p>"
        if project.workers.count() == 0:
            page_data["geen_items"] += (
                "<br/><br/> \nLet op: aan dit project moeten eerst nog medewerkers"
                " en bevoegdheden voor die medewerkers worden toegevoegd")
    return page_data


def get_acties(project, userid):
    """return list of actions with selection and sort order applied
    """
    # data = my.Actie.objects.all()
    data = project.acties.all()
    if data and userid:
        seltest = project.selections.filter(user=userid)
        data = filter_data_on_nummer(data, seltest)
        data = filter_data_on_soort(data, seltest)
        data = filter_data_on_status(data, seltest)
        data = filter_data_on_user(data, seltest)
        data = filter_data_on_description(data, seltest)
        data = filter_data_on_arch(data, seltest)

        sorters = project.sortings.filter(user=userid)
        data = apply_sorters(data, sorters)
    return data


def build_pagedata_for_settings(request, proj):  # request arg unused
    "bouw het scherm op met instellingen voor het huidige project"
    project = my.Project.objects.get(pk=proj)
    proj_users = project.workers.order_by('assigned__username')
    hlp = [x.assigned for x in proj_users]
    all_users = [x for x in aut.User.objects.all().order_by('username') if x not in hlp]
    page_data = {"title": "Instellingen",
                 "name": project.name,
                 "root": proj,
                 "pages": my.Page.objects.all().order_by('order'),
                 "soorten": project.soort.order_by('order'),
                 "stats": project.status.order_by('order'),
                 "all_users": all_users,
                 "proj_users": proj_users}  # .order_by('username')
    return page_data


def set_users(request, proj):
    "leg de aangegeven gebruikers vast bij het project"
    data = request.POST
    # users = data.getlist("ProjUsers")
    # genoemde select bevat de toegekende gebruikers(namen). Bij submitten worden de bijbehorende
    # ids hieruit m.b.v. javascript overgenomen in hidden field `result` gescheiden door #$#
    test = data.get("result", '')
    users = [aut.User.objects.get(pk=x) for x in test.split("$#$")] if test else []
    project = my.Project.objects.get(pk=proj)
    current = project.workers.all()
    old_users = [x.assigned for x in current]
    for user in users:
        if user not in old_users:
            my.Worker.objects.create(project=project, assigned=user)
    for user in old_users:
        if user not in users:
            my.Worker.objects.get(project=project, assigned=user).delete()


def set_tabs(request):
    "leg de ingevulde titels vast bij het project"
    data = request.POST
    pages = my.Page.objects.all().order_by('order')
    for ix, item in enumerate(pages):
        field = "page" + str(ix + 1)
        if data[field] != item.title:
            item.title = data[field]
            item.save()


def set_types(request, proj):
    "leg de ingevulde soorten vast bij het project"
    data = request.POST
    project = my.Project.objects.get(pk=proj)
    soorten = project.soort.all().order_by('order')
    changed = []
    for ix, item in enumerate(soorten):
        field_o = "order" + str(ix + 1)
        field_t = "title" + str(ix + 1)
        field_v = "value" + str(ix + 1)
        if "del" + str(ix + 1) in data:
            item.delete()
        else:
            add_to_changed = False
            if data[field_o] != item.order:
                item.order = data[field_o]
                add_to_changed = True
            if data[field_t] != item.title:
                item.title = data[field_t]
                add_to_changed = True
            if data[field_v] != item.value:
                item.value = data[field_v]
                add_to_changed = True
            if add_to_changed:
                changed.append(item)
    my.Soort.objects.filter(pk__in=[x.id for x in changed]).delete()
    for item in changed:
        item.save()
    if data["order0"]:
        my.Soort.objects.create(project=project, order=data["order0"], title=data["title0"],
                                value=data["value0"])


def set_stats(request, proj):
    "leg de ingevulde statussen vast bij het project"
    data = request.POST
    project = my.Project.objects.get(pk=proj)
    stats = project.status.all().order_by('order')
    changed = []
    for ix, item in enumerate(stats):
        field_o = "order" + str(ix + 1)
        field_t = "title" + str(ix + 1)
        field_v = "value" + str(ix + 1)
        if "del" + str(ix + 1) in data:
            item.delete()
        else:
            add_to_changed = False
            if data[field_o] != item.order:
                item.order = data[field_o]
                add_to_changed = True
            if data[field_t] != item.title:
                item.title = data[field_t]
                add_to_changed = True
            if data[field_v] != item.value:
                item.value = data[field_v]
                add_to_changed = True
            if add_to_changed:
                changed.append(item)
    my.Status.objects.filter(pk__in=[x.id for x in changed]).delete()
    for item in changed:
        item.save()
    if data["order0"]:
        my.Status.objects.create(project=project, order=data["order0"], title=data["title0"],
                                 value=data["value0"])


def build_pagedata_for_selection(request, proj, msg):  # nog niet uitgeprobeerd
    """bouw het scherm op aan de hand van de huidige selectiegegevens
    bij de gebruiker
    """
    project = my.Project.objects.get(pk=proj)
    page_data = {"title": "Actielijst - selectie",
                 "name": project.name,
                 "root": project.id,
                 "msg": msg,
                 "pages": my.Page.objects.all().order_by('order'),
                 "soorten": project.soort.all(),
                 "stats": project.status.all(),
                 "users": [x.assigned for x in project.workers.all()],
                 "selected": {"nummer": [],
                              "enof1": 'of',
                              "gewijzigd": [],
                              "soort": [],
                              "status": [],
                              "user": [],
                              "enof2": 'of',
                              "arch": 0}}

    for sel in my.Selection.objects.filter(project=project, user=request.user.id):
        if sel.veldnm == "soort":
            page_data["selected"][sel.veldnm].append(sel.value)
        elif sel.veldnm in ("status", "user"):
            page_data["selected"][sel.veldnm].append(int(sel.value))
        elif sel.veldnm == "arch":
            page_data["selected"][sel.veldnm] += 1
        elif sel.veldnm == "nummer":
            page_data["selected"]["nummer"] = True
            if sel.extra.strip():
                page_data["selected"]["enof1"] = sel.extra.lower()
            page_data["selected"][sel.operator.lower()] = sel.value
        elif sel.veldnm in ("about", "title"):
            page_data["selected"]["zoek"] = True
            if sel.extra.strip():
                page_data["selected"]["enof2"] = sel.extra.lower()
            page_data["selected"][sel.veldnm] = sel.value
        else:
            return {}, "Unknown search argument: " + sel.veldnm
    return page_data, ''


def setselection(request, proj):  # nog verdelen tussen views en hier
    """verwerk de aanpassingen en koppel door naar tonen van de lijst met acties
    de huidige selectiegegevens voor de user worden verwijderd
    daarna worden nieuwe selectiegegevens bepaald en opgeslagen
    """
    data = request.POST
    selact = data.getlist("select")    # aangekruiste selecties: "act" "srt" "stat" "txt" of "arch"
    project = my.Project.objects.get(pk=proj)
    project.selections.filter(user=request.user.id).delete()
    # extra = "  "
    if "act" in selact:
        set_selection_for_nummer(project, request.user, data)
    if "srt" in selact:
        set_selection_for_soort(project, request.user, data)
    if "stat" in selact:
        set_selection_for_status(project, request.user, data)
    if "user" in selact:
        set_selection_for_user(project, request.user, data)
    if "txt" in selact:
        set_selection_for_description(project, request.user, data)
    if "arch" in selact:
        set_selection_for_arch(project, request.user, data)


def set_selection_for_nummer(project, user, data):
    "create selection items for project/user/actienummer"
    extra = ''
    txtgt = data.get("txtgt", "")
    if txtgt:
        my.Selection.objects.create(project=project, user=user.id, veldnm="nummer",
                                    operator="GT", extra=extra, value=txtgt)
        extra = data.get("enof", "").upper()       # "en" of "of"
    txtlt = data.get("txtlt", "")
    if txtlt:
        my.Selection.objects.create(project=project, user=user.id, veldnm="nummer",
                                    operator="LT", extra=extra, value=txtlt)


def set_selection_for_soort(project, user, data):
    "create selection items for project/user/actiesoort"
    extra = ''
    for srt in data.getlist("srtval"):    # aangekruiste soorten
        my.Selection.objects.create(project=project, user=user.id, veldnm="soort",
                                    operator="EQ", extra=extra, value=srt)
        extra = "OR"


def set_selection_for_status(project, user, data):
    "create selection items for project/user/actiestatus"
    extra = ''
    for stat in data.getlist("statval"):  # aangekruiste statussen
        my.Selection.objects.create(project=project, user=user.id, veldnm="status",
                                    operator="EQ", extra=extra, value=stat)
        extra = "OR"


def set_selection_for_user(project, user, data):
    "create selection items for project/user/behandelaar"
    extra = ''
    for seluser in data.getlist("userval"):  # geselecteerde medewerkers
        my.Selection.objects.create(project=project, user=user.id, veldnm="user",
                                    operator="EQ", extra=extra, value=seluser)
        extra = "OR"


def set_selection_for_description(project, user, data):
    "create selection items for project/user/description fields"
    txtabout = data.get("txtabout", "")
    if txtabout:
        my.Selection.objects.create(project=project, user=user.id, veldnm="about",
                                    operator="INCL", extra='', value=txtabout)
        extra = data.get("enof2", "").upper()     # "en" of "of"
    txttitle = data.get("txttitle", "")
    if txttitle:
        my.Selection.objects.create(project=project, user=user.id, veldnm="title",
                                    operator="INCL", extra=extra, value=txttitle)


def set_selection_for_arch(project, user, data):
    "create selection items for project/user/archive status"
    arch = data.getlist("archall", "")  # "arch" of "all"
    if 'arch' in arch:
        my.Selection.objects.create(project=project, user=user.id, veldnm="arch",
                                    operator="EQ", extra='', value=False)
    elif not arch:
        my.Selection.objects.create(project=project, user=user.id, veldnm="arch",
                                    operator="EQ", extra='', value=True)


def build_pagedata_for_ordering(request, proj, msg):  # msg arg unused
    """bouw het scherm op aan de hand van de huidige sorteringsgegevens
    bij de gebruiker
    """
    project = my.Project.objects.get(pk=proj)
    page_data = {"title": "Actielijst: volgorde",
                 "name": project.name,
                 "root": proj,
                 "pages": my.Page.objects.all().order_by('order'),
                 "fields": [("nummer", "nummer"),
                            ("gewijzigd", "laatst gewijzigd"),
                            ("soort", "soort"),
                            ("status", "status"),
                            ("behandelaar", "behandelaar"),
                            ("title", "omschrijving")],
                 "sorters": []}
    for sorter in project.sortings.filter(user=request.user.id):
        page_data["sorters"].append(sorter)
    while len(page_data["sorters"]) < len(page_data["fields"]):
        page_data["sorters"].append(None)
    return page_data


def setordering(request, proj):
    """verwerk de aanpassingen en koppel door naar tonen van de lijst met acties
    de huidige sorteringsgegevens voor de user worden verwijderd
    daarna worden nieuwe sorteringsgegevens bepaald en opgeslagen
    """
    data = request.POST
    project = my.Project.objects.get(pk=proj)
    fields = {"nummer": "nummer",
              "laatst gewijzigd": "gewijzigd",
              "soort": "soort",
              "status": "status",
              "behandelaar": "behandelaar",
              "omschrijving": "title"}
    project.sortings.filter(user=request.user.id).delete()
    ix = 1
    while True:
        if data[f"field{ix}"]:
            my.SortOrder.objects.create(user=request.user.id, project=project, volgnr=ix,
                                        veldnm=fields[data[f"field{ix}"]],
                                        richting=data[f"order{ix}"])
        else:
            break
        ix += 1


def build_pagedata_for_detail(request, proj, actie, msg=""):
    """bouw het scherm met actiegegevens op.
    de soort user wordt meegegeven aan het scherm om indien nodig wijzigen onmogelijk te
        maken en diverse knoppen te verbergen.
    """
    ## msg = request.GET.get("msg", "")
    if not msg:
        msg = get_appropriate_login_message(request.user, proj, actie)
        if request.user.is_authenticated and actie != 'new':
            msg += "Klik op een van onderstaande termen om meer te zien."
    project = my.Project.objects.get(pk=proj)
    page_data = {"name": project.name,
                 "root": proj,
                 "pages": my.Page.objects.all().order_by('order'),
                 "soorten": project.soort.all().order_by('order'),
                 "stats": project.status.all().order_by('order'),
                 "users": [x.assigned for x in project.workers.all()],
                 "msg": msg}
    page_data["readonly"] = determine_readonly(project, request.user)
    if actie == "new":
        titel = "Nieuwe actie"
        page_titel = ""
        volgnr = 0
        aant = project.acties.count()
        nw_date = dt.timezone.now()   # dt.datetime.now()
        if aant:
            acties_dit_jaar = project.acties.filter(nummer__startswith=f'{nw_date.year}')
            if acties_dit_jaar:
                last = sorted(acties_dit_jaar)[-1]
                volgnr = int(last.nummer.split("-", 1)[1])
        volgnr += 1
        page_data["nummer"] = f"{nw_date.year}-{volgnr:04}"
        page_data["nieuw"] = request.user
        page_data["start"] = nw_date
    else:
        actie = my.Actie.objects.get(pk=actie)
        page_data["actie"] = actie
        titel = f"Actie {actie.nummer} - "
        page_titel = "Titel/Status"
    page_data["title"] = titel
    page_data["page_titel"] = page_titel
    return page_data


def wijzig_detail(request, project, actie):
    """verwerk de aanpassingen en koppel door naar tonen van het scherm
    """
    data = request.POST

    if actie == "nieuw":
        actie = my.Actie()
        actie.project = project
        actie.nummer = data.get("nummer", "")
        actie.starter = request.user
        actie.behandelaar = request.user
        nieuw = True
        srt = my.Soort.objects.get(order=0)
        stat = my.Status.objects.get(order=0)
    else:
        actie = get_object_or_404(my.Actie, pk=actie)
        over, wat, wie = actie.about, actie.title, actie.behandelaar
        srt, stat = actie.soort, actie.status
        nieuw = False

    actie.about = data.get("about", "")
    actie.title = data.get("title", "")
    oldarch = actie.arch
    actie.arch = data.get("archstat", "False") == "True"
    actie.behandelaar = aut.User.objects.get(pk=int(data.get("user", "0")))
    actie.soort = my.Soort.objects.get(value=data.get("soort", " "))
    actie.status = my.Status.objects.get(value=int(data.get("status", "1")))
    actie.lasteditor = request.user
    actie.save()

    msg, mld = '', []
    if nieuw:
        msg = "Actie opgevoerd"
        store_event(msg, actie, request.user)
    else:
        if actie.arch != oldarch and not actie.arch:
            msg = "Actie herleefd"
            store_event(msg, actie, request.user)
        if actie.about != over:
            mld = store_gewijzigd('onderwerp', str(actie.about), mld, actie, request.user)
        if actie.title != wat:
            mld = store_gewijzigd('titel', str(actie.title), mld, actie, request.user)
        if actie.behandelaar != wie:
            mld = store_gewijzigd('behandelaar', str(actie.behandelaar), mld, actie, request.user)
    if actie.soort != srt:
        mld = store_gewijzigd('categorie', str(actie.soort), mld, actie, request.user)
    if actie.status != stat:
        mld = store_gewijzigd('status', str(actie.status), mld, actie, request.user)
    if actie.arch != oldarch and actie.arch:
        msg = "Actie gearchiveerd"
        store_event(msg, actie, request.user)
    msg = build_full_message(mld, msg)

    vervolg = data.get("vervolg", "")   # geeft aan of je naar het vervolgscherm mag
    if vervolg:
        doc = f"/{project.id}/{actie.id}/{vervolg}/mld/{msg}/"
    else:
        doc = f"/{project.id}/{actie.id}/mld/{msg}/"

    if actie.arch != oldarch:
        # indien nodig eerst naar doctool om de actie af te melden of te herleven
        doe = "arch" if actie.arch else "herl"
        follow = my.Event.objects.filter(actie=actie.id).order_by('id')[0].text
        if UIT_DOCTOOL in follow:  # follow.startswith(UIT_DOCTOOL):
            # doc = f"{follow.split()[-1].strip()}meld/{doe}/{project.id}/{actie.id}/"
            doc = f"{follow.split()[-1].strip()}/meld/{doe}/{project.id}/{actie.id}/"
    return doc


def copy_existing_action_from_here(proj, actnum, usernaam, vervolg):
    "gebruik opgegeven actienummer bij opvoeren"
    try:
        actie = my.Actie.objects.get(nummer=actnum)
    except my.Actie.DoesNotExist:
        fout = f'Actie {actnum} bestaat niet'
        if not vervolg:
            msg = fout + " bij doorkoppelen vanuit DocTool zonder terugkeeradres"
            # response = f"/{root}/{actie.id}/mld/{msg}/"
            return f"/{proj}/{actnum}/mld/{msg}/"
        else:
            return vervolg.format('0', fout)
    actie.starter = aut.User.objects.get(pk=1)
    behandelaar = actie.starter
    if usernaam:
        with contextlib.suppress(ObjectDoesNotExist):
            behandelaar = aut.User.objects.get(username=usernaam)
    actie.lasteditor = behandelaar
    actie.save()
    if not vervolg:
        msg = "Aangepast vanuit DocTool zonder terugkeeradres"
        response = f"/{proj}/{actie.id}/mld/{msg}/"
    else:
        obj = my.Event.objects.filter(actie=actie.id).order_by('id')
        text = f"{UIT_DOCTOOL} {vervolg.split('koppel')[0]}"
        if obj:
            obj[0].text += "; " + text
            obj[0].save()
        else:
            store_event(text, actie, actie.starter)
        response = vervolg.format(actie.id, actie.nummer)
    return response


def add_new_action_on_both_sides(proj, data, usernaam, vervolg):
    "maak nieuw actienummer aan en voer op"
    volgnr = 0
    aant = my.Actie.objects.count()
    nw_date = dt.timezone.now()
    if aant:
        last = my.Actie.objects.all()[aant - 1]
        jaar, volgnr = last.nummer.split("-")
        volgnr = int(volgnr) if int(jaar) == nw_date.year else 0
    volgnr += 1
    actie = my.Actie()
    actie.project = my.Project.objects.get(pk=proj)
    actie.nummer = f"{nw_date.year}-{volgnr:04}"
    actie.start = nw_date
    actie.starter = aut.User.objects.get(pk=1)
    behandelaar = actie.starter
    if usernaam:
        with contextlib.suppress(ObjectDoesNotExist):
            behandelaar = aut.User.objects.get(username=usernaam)
    actie.behandelaar = behandelaar
    actie.about = "testbevinding" if "bevinding" in vervolg else ""
    actie.title = data.get("hMeld", "")
    if "userwijz" in vervolg:
        soort = "W"
    elif "userprob" in vervolg:
        soort = "P"
    else:
        soort = " "
    actie.soort = my.Soort.objects.get(value=soort)
    actie.status = my.Status.objects.get(value='0')
    actie.lasteditor = actie.behandelaar
    actie.melding = data.get("hOpm", "")
    actie.save()
    if vervolg:
        store_event(f"{UIT_DOCTOOL} {vervolg.split('koppel')[0]}", actie, actie.starter)
    store_event(f'titel: "{actie.title}"', actie, actie.starter)
    store_event(f'categorie: "{actie.soort}"', actie, actie.starter)
    store_event(f'status: "{actie.status}"', actie, actie.starter)

    if vervolg:
        response = vervolg.format(actie.id, actie.nummer)
    else:
        msg = "Opgevoerd vanuit DocTool zonder terugkeeradres"
        response = f"/{proj}/{actie.id}/mld/{msg}/"
    return response


def build_full_message(mld, msg):
    "make the message reflect all modifications"
    if mld and not msg:
        if len(mld) == 1:
            msg = mld[0] + " gewijzigd"
        else:
            msg = ", ".join(mld[:-1]) + f" en {mld[-1]} gewijzigd"
        msg = msg.capitalize()
    return msg


def build_pagedata_for_tekstpage(request, proj, actie, page="", msg=''):
    """toon een van de uitgebreide tekstrubrieken.
    de soort user wordt meegegeven aan het scherm om indien nodig wijzigen onmogelijk te
        maken en diverse knoppen te verbergen.
    """
    if not msg:
        msg = get_appropriate_login_message(request.user, proj, page)

    project = my.Project.objects.get(pk=proj)
    page_data = {
        "root": proj,
        "name": project.name,
        "pages": my.Page.objects.all().order_by('order'),
        "msg": msg}
    page_data["readonly"] = determine_readonly(project, request.user)
    actie = get_object_or_404(my.Actie, pk=actie)
    tab = get_object_or_404(my.Page, link=page)
    page_titel = tab.title
    next_page = my.Page.objects.get(order=tab.order + 1).link

    if page == "meld":
        page_text = actie.melding
    elif page == "oorz":
        page_text = actie.oorzaak
    elif page == "opl":
        page_text = actie.oplossing
    elif page == "verv":
        page_text = actie.vervolg

    page_data["page"] = page
    page_data["next"] = next_page
    page_data["title"] = f"Actie {actie.nummer} - "
    page_data["page_titel"] = page_titel
    page_data["page_text"] = page_text
    page_data["actie"] = actie
    return page_data


def wijzig_tekstpage(request, proj, actie, page=""):
    """verwerk de aanpassingen en koppel door naar tonen van het scherm
    """
    project = my.Project.objects.get(pk=proj)
    if not is_user(project, request.user):  # and not is_admin(project, request.user):
        return no_authorization_message('acties te wijzigen', proj)
    data = request.POST
    tekst = data.get("data", "")
    vervolg = data.get("vervolg", "")
    actie = get_object_or_404(my.Actie, pk=actie)

    if page == "meld":
        orig = actie.melding
        actie.melding = tekst
    elif page == "oorz":
        orig = actie.oorzaak
        actie.oorzaak = tekst
    elif page == "opl":
        orig = actie.oplossing
        actie.oplossing = tekst
    elif page == "verv":
        orig = actie.vervolg
        actie.vervolg = tekst
    else:
        raise ValueError('missing/wrong page')  # actie niet per ongeluk aanpassen

    actie.lasteditor = request.user
    actie.save()

    if page == "meld" and actie.melding != orig:
        msg = "Meldingtekst aangepast"
        store_event(msg, actie, request.user)
    elif page == "oorz" and actie.oorzaak != orig:
        msg = "Beschrijving oorzaak aangepast"
        store_event(msg, actie, request.user)
    elif page == "opl" and actie.oplossing != orig:
        msg = "Beschrijving oplossing aangepast"
        store_event(msg, actie, request.user)
    elif page == "verv" and actie.vervolg != orig:
        msg = "Beschrijving vervolgactie aangepast"
        store_event(msg, actie, request.user)

    page = vervolg if vervolg else page
    return f"/{proj}/{actie.id}/{page}/meld/{msg}"


def build_pagedata_for_events(request, proj, actie, event='', msg=''):
    """bouw de lijst op met actiehistorie (momenten).
    indien er een moment geselecteerd is, deze apart doorgeven voor in het onderste
        gedeelte van het scherm.
    de soort user wordt meegegeven aan het scherm om indien nodig wijzigen onmogelijk te
        maken en diverse knoppen te verbergen.
    """
    if not msg:
        msg = get_appropriate_login_message(request.user, proj, actie)
    msg += " Klik op een voortgangsregel om de tekst nader te bekijken."
    project = my.Project.objects.get(pk=proj)
    # actie = my.Actie.objects.select_related().get(id=actie)
    actie = my.Actie.objects.get(id=actie)

    page_data = {
        "title": f"{actie.nummer} - ",
        "page_titel": "Voortgang",
        "name": project.name,
        "root": proj,
        "msg": msg,
        "pages": my.Page.objects.all().order_by('order'),
        "actie": actie,
        "events": actie.events.order_by("-start").order_by("-id"),
        "user": request.user}
    page_data["readonly"] = determine_readonly(project, request.user)

    if event == "nieuw":
        nw_date = dt.timezone.now()  # dt.datetime.now()
        page_data["nieuw"] = True
        page_data["curr_ev"] = {"id": "nieuw", "start": nw_date}
    elif event:
        page_data["curr_ev"] = my.Event.objects.get(pk=event)
    return page_data


def wijzig_events(request, proj='', actie="", event=""):
    """verwerk de aanpassingen en koppel door naar tonen van het scherm
    """
    project = my.Project.objects.get(pk=proj)
    if not is_user(project, request.user):  # and not is_admin(root, request.user):
        return no_authorization_message('acties te wijzigen', proj)

    data = request.POST
    tekst = data.get("data", "")
    actie = get_object_or_404(my.Actie, pk=actie)

    if event == "nieuw":
        event = my.Event()
        event.actie = actie
        event.starter = request.user
        ## actie.nummer = nummer
        ## event.start = dt.timezone.now()  # dt.datetime.now()
        verb = 'toegevoegd'
    elif event:
        event = get_object_or_404(my.Event, pk=event)
        verb = 'bijgewerkt'
    else:
        raise Http404    # Response(f"{actie} {event}")

    event.text = tekst
    event.save()
    return f"/{proj}/{actie.id}/voortg/meld/De gebeurtenis is {verb}./"


def get_appropriate_login_message(user, root='', actie=''):
    "geef toepasselijke welkom boodschap afhankelijk van of de gebruiker is ingelogd"
    if root:
        root = f'{root}/'
    if actie:
        actie = f'{actie}/'
    # if request.user.is_authenticated:
    if user and user.is_authenticated:
        msg = f'U bent ingelogd als <i>{user.username}</i>. Klik <a href="/logout/'
        inuit = 'uit'
    else:
        msg = 'U bent niet ingelogd. Klik <a href="/accounts/login/'
        inuit = 'in'
    msg += f'?next=/{root}{actie}">hier</a> om {inuit} te loggen. '
    return msg


def no_authorization_message(to_do, root=''):
    "actie afbreken als gebruiker niet geautoriseerd is"
    if root:
        root = f'{root}/'
    return HttpResponse(f"U bent niet geautoriseerd om {to_do}<br>Klik "
                        f'<a href="/{root}">hier</a> om door te gaan')


def logged_in_message(request, root=''):
    "het eerste deel van get_appropriate_login_message?"
    if root:
        root = f'{root}/'
    return (f'U bent ingelogd als <i>{request.user.username}</i>. '
            f'Klik <a href="/logout/?next=/{root}select/">hier</a> om uit te loggen.'
            f'Klik <a href="/{root}">hier</a> om door te gaan')


def not_logged_in_message(to_do, root=''):
    "actie afbreken als gebruiker niet ingelogd is"
    if root:
        root = f'{root}/'
    return HttpResponse('<html><body style="background-color: lightblue">'
                        f'U moet ingelogd zijn om {to_do}.<br/><br/>'
                        f'Klik <a href="/accounts/login/?next=/{root}select/">hier</a>'
                        f' om in te loggen, <a href="/{root}">hier</a> om terug te gaan.'
                        '<body></html>')


def determine_readonly(project, user):
    "bepaal of de gebruiker wijzigingen mag aanbrengen"
    return not is_user(project, user)  # or is_admin(project, user)


def is_user(project, user):
    """geeft indicatie terug of de betreffende gebruiker acties mag wijzigen
    """
    return user in [x.assigned for x in project.workers.all()]
    # test = root + "_user"
    # for grp in user.groups.all():
    #     if grp.name == test:
    #         return True
    # return False


def is_admin(project, user):  # TODO moet eigenlijk zijn: heeft admin rechten voor dit project
    """geeft indicatie terug of de betreffende gebruiker
    acties en settings mag wijzigen
    """
    return user.is_staff   # vooralsnog even algemene admin i.p.v. project admin
    # test = root + "_admin"
    # for grp in user.groups.all():
    #     if grp.name == test:
    #         return True     # , test, grp.name  -- why the rest?
    # return False    # , test, str(user.groups.all()) - why the rest?


def filter_data_on_nummer(data, seltest):
    "apply filter on 'nummer' to the data"
    filtered = seltest.filter(veldnm="nummer")
    if filtered:
        filter = ""
        for f in filtered:
            if f.extra.upper() in ("EN", 'AND'):
                filter += " & "
            elif f.extra.upper() in ("OF", 'OR'):
                filter += " | "
            filter += f'Q(nummer__{f.operator.lower()}="{f.value}")'
        with contextlib.suppress(SyntaxError):
            data = eval(f'data.filter({filter})')
    return data


def filter_data_on_soort(data, seltest):
    "apply filter on 'soort' to the data"
    filtered = seltest.filter(veldnm="soort")
    sel = [my.Soort.objects.get(value=x.value).id for x in filtered]
    if sel:
        data = data.filter(soort__in=sel)
    return data


def filter_data_on_status(data, seltest):
    "apply filter on 'status' to the data"
    filtered = seltest.filter(veldnm="status")
    sel = [my.Status.objects.get(value=int(x.value)).id for x in filtered]
    if sel:
        data = data.filter(status__in=sel)
    return data


def filter_data_on_user(data, seltest):
    "apply filter on 'behandelaar' to the data"
    filtered = seltest.filter(veldnm="user")
    sel = [int(x.value) for x in filtered]
    if sel:
        data = data.filter(behandelaar__in=sel)
    return data


def filter_data_on_description(data, seltest):
    "apply filter on descriptive fields to the data"
    filtered = seltest.filter(veldnm="about")
    filter = ''
    if filtered:
        test = filtered[0].value
        if test:
            filter = f'Q(about__icontains="{test}")'
    filtered = seltest.filter(veldnm="title")
    if filtered:
        test = filtered[0].value
        if test:
            if filter:
                if filtered[0].extra.upper() in ("EN", "AND"):
                    filter += " & "
                elif filtered[0].extra.upper() in ("OF", "OR"):
                    filter += " | "
            filter += f'Q(title__icontains="{test}")'
    if filter:
        with contextlib.suppress(SyntaxError):
            data = eval(f'data.filter({filter})')
    return data


def filter_data_on_arch(data, seltest):
    "apply filter on archive status to the data"
    filtered = seltest.filter(veldnm="arch")
    if not filtered:
        data = data.exclude(arch=True)
    elif len(filtered) == 1:
        data = data.filter(arch=True)
    return data


def apply_sorters(data, sorters):
    "sort the provided data"
    order = []
    for sorter in sorters:
        if sorter.veldnm == "title":
            if sorter.richting == "asc":
                order.extend(("about", "title"))
            else:
                order.extend(("-about", "-title"))
        elif sorter.veldnm == "behandelaar":
            ordr = sorter.veldnm + "__username"
            ordr = ordr if sorter.richting == "asc" else "-" + ordr
            order.append(ordr)
        else:
            ordr = sorter.veldnm if sorter.richting == "asc" else "-" + sorter.veldnm
            order.append(ordr)
    data = data.order_by(*order)
    return data


def store_event(msg, actie, user):
    """Maak nieuw vrije tekst event en sla deze op in de lijst
    """
    my.Event.objects.create(actie=actie, starter=user, text=msg)


# kan waarschijnlijk weg: event.start heeft auto_now_add=True en kan daardoor niet gewijzigd worden
# def store_event_with_date(msg, actie, date, user):
#     """Maak nieuw vrije tekst event en sla deze op in de lijst
#     """
#     my.Event.objects.create(actie=actie, start=date, starter=user, text=msg)


def store_gewijzigd(msg, txt, mld, actie, user):
    """Maak nieuw standaard event (rubriek X is gewijzigd)
    """
    store_event(f'{msg} gewijzigd in "{txt}"', actie, user)
    mld.append(msg)
    return mld
