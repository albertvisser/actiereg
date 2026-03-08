"""Core functions for page views
"""
# import datetime as dt
import contextlib
import django.utils as dt
from django.http import HttpResponse  # , HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
# from django.db.models import Q  # wordt gebruikt bij samenstellen filterstring (get_acties)
# from django.contrib import admin
import django.contrib.auth.models as auth
import tracker.models as my

UIT_DOCTOOL = "Actie opgevoerd vanuit Doctool"


def build_pagedata_for_newproj():
    """bepaal te tonen gegevens voor "nieuw project" scherm
    """
    return {'all_users': list(auth.User.objects.all().order_by('username'))}


def add_project(name, desc, admins, users):
    "nieuw project aanmaken"
    newproj = my.Project.objects.create(name=name, description=desc)
    if my.Page.objects.count() == 0:
        add_default_pages()
    add_default_soorten(newproj)
    add_default_statussen(newproj)
    add_auth_for_project(newproj)
    add_admins(newproj, admins)
    add_users(newproj, users)
    return newproj.id


def add_default_pages():
    """voer standaard pagina's op voor alle projecten
    """
    for x, y, z in [("index", 0, "lijst"),
                    ("detail", 1, "titel/status"),
                    # ("meld", 2, "probleem/wens"),
                    # ("oorz", 3, "oorzaak/analyse"),
                    # ("opl", 4, "oplossing"),
                    # ("verv", 5, "vervolgactie"),
                    # ("voortg", 6, "voortgang")
                    ]:
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


def add_auth_for_project(project):
    """add groups to cluster user permissions
    """
    group = auth.Group.objects.create(name=f'{project.name}_admin')
    for permit in auth.Permission.objects.filter(content_type__app_label="tracker"):
        group.permissions.add(permit)
    group = auth.Group.objects.create(name=f'{project.name}_user')
    for permit in auth.Permission.objects.filter(content_type__app_label="tracker").filter(
            content_type__model__in=['actie', 'event', 'sortorder', 'selection']):
        group.permissions.add(permit)


def add_admins(project, admin_list):
    """add initial admin(s)
    """
    for entry in admin_list:
        if entry == '0':
            continue
        user = auth.User.objects.get(pk=entry)
        group = auth.Group.objects.get(name=f'{project.name}_admin')
        user.groups.add(group.id)


def add_users(project, user_list):
    """add initial admin(s)
    """
    for entry in user_list:
        if entry == '0':
            continue
        user = auth.User.objects.get(pk=entry)
        group = auth.Group.objects.get(name=f'{project.name}_user')
        user.groups.add(group.id)
        my.Worker.objects.create(project=project, assigned=user)


def build_pagedata_for_project(request, proj, msg):
    "bouw het scherm op dat acties bij het project toont"
    project = my.Project.objects.get(pk=proj)
    page_data = {"title": "Actielijst",
                 "page_titel": "lijst",
                 "name": project.name,
                 "root": proj,
                 "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
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
    # all_users = [x for x in auth.User.objects.all().order_by('username') if x not in hlp]
    all_users, proj_admins, admin_users = [], [], []
    wanted_group = auth.Group.objects.get(name=f'{project.name}_admin')
    for user in auth.User.objects.all().order_by('username'):
        if user not in hlp:
            all_users.append(user)
        if wanted_group in user.groups.all():
            proj_admins.append(user)
        else:
            admin_users.append(user)
    page_data = {"title": "Instellingen",
                 "name": project.name,
                 "desc": project.description,
                 "root": proj,
                 "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
                 "soorten": project.soort.order_by('order'),
                 "stats": project.status.order_by('order'),
                 "all_users": all_users,
                 "proj_users": proj_users,
                 "admin_users": admin_users,
                 "proj_admins": proj_admins}
    return page_data


def set_desc(request, proj):
    "werk de opgegeven bescrijving bij in het project"
    project = my.Project.objects.get(pk=proj)
    project.description = request.POST.get('desc', '')
    # raise TypeError(f'{project.description=}')
    project.save(update_fields=['description'])


def set_users(request, proj):
    "leg de aangegeven gebruikers vast bij het project"
    data = request.POST
    # users = data.getlist("ProjUsers")
    # genoemde select bevat de toegekende gebruikers(namen). Bij submitten worden de bijbehorende
    # ids hieruit m.b.v. javascript overgenomen in hidden field `result` gescheiden door #$#
    test = data.get("result", '')
    users = [auth.User.objects.get(pk=x) for x in test.split("$#$")] if test else []
    project = my.Project.objects.get(pk=proj)
    group = auth.Group.objects.get(name=f'{project.name}_user')
    current = project.workers.all()
    old_users = [x.assigned for x in current]
    for user in users:
        if user not in old_users:
            my.Worker.objects.create(project=project, assigned=user)
            user.groups.add(group.id)
    for user in old_users:
        if user not in users:
            my.Worker.objects.get(project=project, assigned=user).delete()
            user.groups.remove(group.id)


def set_admins(request, proj):
    "leg de aangegeven admins vast bij het project"
    data = request.POST
    # users = data.getlist("ProjAdmins")
    # genoemde select bevat de toegekende gebruikers(namen). Bij submitten worden de bijbehorende
    # ids hieruit m.b.v. javascript overgenomen in hidden field `result` gescheiden door #$#
    test = data.get("result", '')
    users = [auth.User.objects.get(pk=x) for x in test.split("$#$")] if test else []
    project = my.Project.objects.get(pk=proj)
    wanted_group = auth.Group.objects.get(name=f'{project.name}_admin')
    old_admins = [x for x in auth.User.objects.all() if wanted_group in x.groups.all()]
    for user in users:
        if user not in old_admins:
            grp = auth.Group.objects.get(name=f'{project.name}_admin')
            user.groups.add(grp)
    for user in old_admins:
        if user not in users:
            grp = auth.Group.objects.get(name=f'{project.name}_admin')
            user.groups.remove(grp)


def set_tabs(request):
    "leg de ingevulde titels vast bij het project"
    data = request.POST
    pages = get_pages()  # my.Page.objects.all().order_by('order'),
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
            if int(data[field_o]) != item.order:
                item.order = int(data[field_o])
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
            if int(data[field_o]) != item.order:
                item.order = int(data[field_o])
                add_to_changed = True
            if data[field_t] != item.title:
                item.title = data[field_t]
                add_to_changed = True
            if int(data[field_v]) != item.value:
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


def build_pagedata_for_selection(request, proj, msg):
    """bouw het scherm op aan de hand van de huidige selectiegegevens
    bij de gebruiker
    """
    project = my.Project.objects.get(pk=proj)
    page_data = {"title": "Actielijst - selectie",
                 "name": project.name,
                 "root": project.id,
                 "msg": msg,
                 "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
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
            if sel.value == 'False':
                page_data["selected"][sel.veldnm] += 1
            elif sel.value == 'True':
                page_data["selected"][sel.veldnm] += 2
            else:
                raise ValueError(f'Unknown value for arch: {sel.value}')
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


def setselection(request, proj):
    """verwerk de aanpassingen en koppel door naar tonen van de lijst met acties
    de huidige selectiegegevens voor de user worden verwijderd
    daarna worden nieuwe selectiegegevens bepaald en opgeslagen
    """
    data = request.POST
    project = my.Project.objects.get(pk=proj)
    option1 = set_selection_for_nummer(project, request.user, data)
    option2 = set_selection_for_soort(project, request.user, data)
    option3 = set_selection_for_status(project, request.user, data)
    option4 = set_selection_for_user(project, request.user, data)
    option5 = set_selection_for_description(project, request.user, data)
    option6 = set_selection_for_arch(project, request.user, data)
    if any((option1, option2, option3, option4, option5, option6)):
        msg = 'De selectie is gewijzigd.'
        back = True
    else:
        msg = 'Er is niks gewijzigd'
        back = False
    return msg, back


def build_pagedata_for_search(request, proj, msg):
    "bouw het scherm op voor uitvoeren van een zoekactie"
    # msg = 'under construction'
    project = my.Project.objects.get(pk=proj)
    page_data = {"title": "Zoek op tekst",
                 "name": project.name,
                 "root": project.id,
                 "msg": msg,
                 "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
                 'search': '',
                 'results': []}
    return page_data


def build_pagedata_for_results(request, proj, msg):
    "bouw het scherm op om het resultaat te tonen"
    data = request.POST
    search = data.get('search', '')
    project = my.Project.objects.get(pk=proj)
    results = search_for(project, search)
    page_data = {"title": "Zoekresultaten",
                 "name": project.name,
                 "root": project.id,
                 "msg": msg,
                 "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
                 'search': search,
                 'results': results}
    return page_data


def search_for(project, search):
    "voer de zoekactie uit"
    results = []
    acties = my.Actie.objects.filter(project=project)
    # if acties:
    #     results.extend(acties)
    results.extend([(x, '', 'betreft', x.about) for x in acties.filter(about__contains=search)])
    results.extend([(x, '', 'omschrijving', x.title) for x in acties.filter(title__contains=search)])
    results.extend([(x, '', 'melding', x.melding) for x in acties.filter(melding__contains=search)])
    results.extend([(x, '', 'oorzaak', x.oorzaak) for x in acties.filter(oorzaak__contains=search)])
    results.extend([(x, '', 'oplossing', x.oplossing)
                    for x in acties.filter(oplossing__contains=search)])
    results.extend([(x, '', 'vervolg', x.vervolg) for x in acties.filter(vervolg__contains=search)])
    for actie in acties:
        results.extend([(actie, f'#ev{x.id}', f'event {str(x.start)[:19]}', x.text)
                        for x in actie.events.filter(text__contains=search)])
    return results


def set_selection_for_nummer(project, user, data):
    "create selection items for :project/user/actienummer"
    oldsel = my.Selection.objects.filter(project=project, user=user.id, veldnm="nummer")
    clear_all = oldsel and 'act' not in data.getlist('select')
    oldgt = oldsel.filter(operator='GT') or ''
    oldlt = oldsel.filter(operator='LT') or ''
    oldgtvalue = oldgt[0].value if oldgt else ''
    oldltvalue = oldlt[0].value if oldlt else ''
    oldextra = oldgt[0].extra if oldgt else oldlt[0].extra if oldlt else 'OF'
    extra = data.get("enof", "of").upper() if not clear_all else "of"       # "en" of "of"
    txtgt = data.get("txtgt", "") if not clear_all else ""
    txtlt = data.get("txtlt", "") if not clear_all else ""
    if all((txtgt == oldgtvalue, txtlt == oldltvalue, extra == oldextra)):
        return False  # niks gewijzigd
    if txtgt:
        if oldgt:
            oldgt.update(value=txtgt, extra=extra)
        else:
            my.Selection.objects.create(project=project, user=user.id, veldnm="nummer",
                                        operator="GT", extra=extra, value=txtgt)
    elif oldgt:
        oldgt.delete()
    if txtlt:
        if oldlt:
            oldlt.update(value=txtlt, extra=extra)
        else:
            my.Selection.objects.create(project=project, user=user.id, veldnm="nummer",
                                        operator="LT", extra=extra, value=txtlt)
    elif oldlt:
        oldlt.delete()
    return True  # any((txtgt, txtlt))


def set_selection_for_soort(project, user, data):
    "create selection items for project/user/actiesoort"
    newsel = data.getlist("srtval")    # aangekruiste soorten
    oldsel = my.Selection.objects.filter(project=project, user=user.id, veldnm="soort")
    if oldsel and 'srt' not in data.getlist('select'):
        newsel = []
    if sorted(newsel) == sorted(x.value for x in oldsel):
        return False  # niks gewijzigd
    for obj in oldsel:
        if obj.value not in newsel:
            obj.delete()
    for srt in newsel:
        if not oldsel.filter(value=srt):
            my.Selection.objects.create(project=project, user=user.id, veldnm="soort",
                                        operator="EQ", extra="OR", value=srt)
    return True


def set_selection_for_status(project, user, data):
    "create selection items for project/user/actiestatus"
    newsel = data.getlist("statval")  # aangekruiste statussen
    oldsel = my.Selection.objects.filter(project=project, user=user.id, veldnm="status")
    if oldsel and 'stat' not in data.getlist('select'):
        newsel = []
    if sorted(newsel) == sorted(x.value for x in oldsel):
        return False  # niks gewijzigd
    for obj in oldsel:
        if obj.value not in newsel:
            obj.delete()
    for stat in newsel:
        if not oldsel.filter(value=stat):
            my.Selection.objects.create(project=project, user=user.id, veldnm="status",
                                        operator="EQ", extra="OR", value=stat)
    return True


def set_selection_for_user(project, user, data):
    "create selection items for project/user/behandelaar"
    newsel = data.getlist("userval")  # geselecteerde medewerkers
    oldsel = my.Selection.objects.filter(project=project, user=user.id, veldnm="user")
    if oldsel and 'user' not in data.getlist('select'):
        newsel = []
    if sorted(newsel) == sorted(x.value for x in oldsel):
        return False  # niks gewijzigd
    for obj in oldsel:
        if obj.value not in newsel:
            obj.delete()
    for seluser in newsel:
        if not oldsel.filter(value=seluser):
            my.Selection.objects.create(project=project, user=user.id, veldnm="user",
                                        operator="EQ", extra="OR", value=seluser)
    return True


def set_selection_for_description(project, user, data):
    "create selection items for project/user/description fields"
    oldabout = my.Selection.objects.filter(project=project, user=user.id, veldnm="about")
    oldtitle = my.Selection.objects.filter(project=project, user=user.id, veldnm="title")
    clear_all = any((oldabout, oldtitle)) and 'txt' not in data.getlist('select')
    oldaboutval = oldabout[0].value if oldabout else ''
    oldtitleval = oldtitle[0].value if oldtitle else ''
    oldextra = oldabout[0].extra if oldabout else oldtitle[0].extra if oldtitle else 'OF'
    extra = data.get("enof2", "of").upper() if not clear_all else 'of'    # "en" of "of"
    txtabout = data.get("txtabout", "") if not clear_all else ''
    txttitle = data.get("txttitle", "") if not clear_all else ''
    if all((txtabout == oldaboutval, txttitle == oldtitleval, extra == oldextra)):
        return False  # niks gewijzigd
    if txtabout:
        if oldabout:
            oldabout.update(value=txtabout, extra=extra)
        else:
            my.Selection.objects.create(project=project, user=user.id, veldnm="about",
                                        operator="INCL", extra=extra, value=txtabout)
    elif oldabout:
        oldabout.delete()
    if txttitle:
        if oldtitle:
            oldtitle.update(value=txttitle, extra=extra)
        else:
            my.Selection.objects.create(project=project, user=user.id, veldnm="title",
                                        operator="INCL", extra=extra, value=txttitle)
    elif oldtitle:
        oldtitle.delete()
    return True  # any((txtabout, txttitle))


def set_selection_for_arch(project, user, data):
    "create selection items for project/user/archive status"
    arch = data.getlist("archall", "")  # "arch" of "all"
    oldarch = my.Selection.objects.filter(project=project, user=user.id, veldnm="arch")
    modified = True
    # if not oldarch:                     # van o3
    #     if 'all' in arch:               # naar n3
    #         modified = False
    #     else:
    #         value = 'True' if 'arch' in arch else 'False'        # naar n2 resp. n1
    #         my.Selection.objects.create(project=project, user=user.id, veldnm="arch",
    #                                     operator="EQ", extra='', value=value)
    # elif oldarch[0].value == 'False':   # van o1
    #     if not 'arch' in 'select':      # naar n1
    #         modified = False
    #     elif 'arch' in arch:            # naar n2
    #         oldarch.update(value='True')
    #     elif 'all' in arch:             # naar n3
    #         oldarch.delete()
    # else:  # oldarch and oldarch[0].value == 'True' - van o2
    #     if not 'arch' in 'select':      # naar n1
    #         oldarch.update(value='False')
    #     elif 'arch' in arch:            # naar n2
    #         modified = False
    #     elif 'all' in arch:             # naar n3
    #         oldarch.delete()

    if 'arch' not in data.getlist('select'):
        if not oldarch:
            my.Selection.objects.create(project=project, user=user.id, veldnm="arch",
                                        operator="EQ", extra='', value='False')
        elif oldarch[0].value == 'False':
            modified = False
        else:  # if oldarch[0].value == 'True':
            oldarch.update(value='False')
    elif 'arch' in arch:
        if not oldarch:
            my.Selection.objects.create(project=project, user=user.id, veldnm="arch",
                                        operator="EQ", extra='', value='True')
        elif oldarch[0].value == 'False':
            oldarch.update(value='True')
        else:  # if oldarch[0].value == 'True':
            modified = False
    else:  # elif 'all' in arch:
        if not oldarch:
            modified = False
        elif oldarch[0].value == 'False':
            oldarch.delete()
        else:  # if oldarch[0].value == 'True':
            oldarch.delete()

    # if 'all' in arch:
    #     # breakpoint()
    #     if oldarch:
    #         oldarch.delete()
    #         modified = True
    #     else:
    #         modified = False
    # else:
    #     value = str('arch' in arch)
    #     # breakpoint()
    #     if not oldarch:
    #         my.Selection.objects.create(project=project, user=user.id, veldnm="arch",
    #                                     operator="EQ", extra='', value=value)
    #         modified = True
    #     elif oldarch[0].value == value:
    #         modified = False
    #     else:
    #         modified = True
    #         oldarch.update(value=value)
    # raise ValueError(f'{oldarch[0].value=}, {value=}, {modified=}')
    return modified


def build_pagedata_for_ordering(request, proj, msg):
    """bouw het scherm op aan de hand van de huidige sorteringsgegevens
    bij de gebruiker
    """
    project = my.Project.objects.get(pk=proj)
    page_data = {"title": "Actielijst: volgorde",
                 "name": project.name,
                 "root": proj,
                 "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
                 "msg": msg,
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


def build_pagedata_for_detail(request, proj, actie, msg="", edit=False, event=None):
    """bouw het scherm met actiegegevens op.
    de soort user wordt meegegeven aan het scherm om indien nodig wijzigen onmogelijk te
        maken en diverse knoppen te verbergen.
    """
    ## msg = request.GET.get("msg", "")
    if msg:
        message, msg = msg, ''
    else:
        message, msg = '', get_appropriate_login_message(request.user, proj, actie)
        # if request.user.is_authenticated and actie != 'new':
        #     msg += "Klik op een van onderstaande termen om meer te zien."
    project = my.Project.objects.get(pk=proj)
    page_data = {"name": project.name,
                 "root": proj,
                 "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
                 "soorten": project.soort.all().order_by('order'),
                 "stats": project.status.all().order_by('order'),
                 "users": [x.assigned for x in project.workers.all()],
                 "edit": edit,
                 "message": message,
                 "msg": msg}
    page_data["readonly"] = determine_readonly(project, request.user)
    if actie == "new":
        titel = "Nieuwe actie"
        page_titel = ""
        volgnr = 0
        aant = project.acties.count()
        nw_date = dt.timezone.now()   # dt.datetime.now()
        if aant:
            acties_dit_jaar = project.acties.filter(nummer__startswith=f'{nw_date.year}').order_by(
                    "-nummer")
            if acties_dit_jaar:
                last = acties_dit_jaar[0]
                volgnr = int(last.nummer.split("-", 1)[1])
        volgnr += 1
        page_data['edit'] = True
        page_data["nummer"] = f"{nw_date.year}-{volgnr:04}"
        page_data["nieuw"] = request.user  # of "not assigned"?
        page_data["start"] = nw_date
    else:
        actie = my.Actie.objects.get(pk=actie)
        page_data["actie"] = actie
        titel = f"Actie {actie.nummer} - {actie.about}:"
        page_titel = "Actie details"
        page_data["events"] = [(x, is_system_event(x)) for x in actie.events.all()]
        if event:  # de waarde "nieuw" hebben we niet nodig
            # event tekst tonen in textarea onderin
            page_data['curr_ev'] = my.Event.objects.get(pk=event)
    page_data["title"] = titel
    page_data["page_titel"] = page_titel
    return page_data


def wijzig_detail(request, project, actie, event=None):
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
        srt = my.Soort.objects.get(project=project, order=0)
        stat = my.Status.objects.get(project=project, order=0)
    else:
        actie = get_object_or_404(my.Actie, pk=actie)
        over, wat, wie = actie.about, actie.title, actie.behandelaar
        srt, stat = actie.soort, actie.status
        waarom = actie.melding
        nieuw = False

    actie.about = data.get("about", "")
    actie.title = data.get("title", "")
    oldarch = actie.arch
    actie.arch = data.get("archstat", "False") == "True"
    actie.behandelaar = auth.User.objects.get(pk=int(data.get("user", "0")))
    actie.soort = my.Soort.objects.get(project=project, value=data.get("soort", " "))
    actie.status = my.Status.objects.get(project=project, value=int(data.get("status", "1")))
    actie.lasteditor = request.user
    actie.melding = data.get("data1", "")
    actie.save()

    msg, mld = '', []
    if nieuw:
        msg = "Actie opgevoerd"
        store_event(msg, actie, request.user)
        if actie.soort == srt:
            store_event(f"categorie is {srt}", actie, request.user)
        if actie.status == stat:
            store_event(f"status is {stat}", actie, request.user)
        if actie.melding:
            store_event("Meldingtekst aangepast", actie, request.user)
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
        if actie.melding != waarom:
            store_event("Meldingtekst aangepast", actie, request.user)
            mld.append("meldingtekst")
    if actie.soort != srt:
        mld = store_gewijzigd('categorie', str(actie.soort), mld, actie, request.user)
    if actie.status != stat:
        mld = store_gewijzigd('status', str(actie.status), mld, actie, request.user)
    if actie.arch != oldarch and actie.arch:
        msg = "Actie gearchiveerd"
        store_event(msg, actie, request.user)
    msg = build_full_message(mld, msg)

    # vervolg = data.get("vervolg", "")   # geeft aan of je naar het vervolgscherm mag
    # if vervolg:
    #     doc = f"/{project.id}/{actie.id}/{vervolg}/mld/{msg}/"
    # else:
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
        return vervolg.format('0', fout)
    actie.starter = auth.User.objects.get(pk=1)
    behandelaar = actie.starter
    if usernaam:
        with contextlib.suppress(ObjectDoesNotExist):
            behandelaar = auth.User.objects.get(username=usernaam)
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
    actie.starter = auth.User.objects.get(pk=1)
    behandelaar = actie.starter
    if usernaam:
        with contextlib.suppress(ObjectDoesNotExist):
            behandelaar = auth.User.objects.get(username=usernaam)
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
        "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
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
    else:  # if page == "verv":  -- geen andere mogelijkheid
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
    # tekst = data.get("data", "")
    # vervolg = data.get("vervolg", "")
    actie = get_object_or_404(my.Actie, pk=actie)

    msg = ""
    if page == "meld":
        orig = actie.melding
        actie.melding = data.get("data1", "")
        if actie.melding == orig:
            msg = "Er is niks gewijzigd"
    elif page == "oorz":
        orig = actie.oorzaak
        actie.oorzaak = data.get("data2", "")
        if actie.oorzaak == orig:
            msg = "Er is niks gewijzigd"
    elif page == "opl":
        orig = actie.oplossing
        actie.oplossing = data.get("data3", "")
        if actie.oplossing == orig:
            msg = "Er is niks gewijzigd"
    elif page == "verv":
        orig = actie.vervolg
        actie.vervolg = data.get("data4", "")
        if actie.vervolg == orig:
            msg = "Er is niks gewijzigd"
    else:
        raise ValueError('missing/wrong page')  # failsafe

    if not msg:
        actie.lasteditor = request.user
        actie.save()

        if page == "meld":
            msg = "Meldingtekst aangepast"
        elif page == "oorz":
            msg = "Beschrijving oorzaak aangepast"
        elif page == "opl":
            msg = "Beschrijving oplossing aangepast"
        else:  # if page == "verv": - nu echt enige mogelijkheid
            msg = "Beschrijving vervolgactie aangepast"
        store_event(msg, actie, request.user)

    # page = vervolg if vervolg else page
    # return f"/{proj}/{actie.id}/{page}/mld/{msg}"
    return f"/{proj}/{actie.id}/mld/{msg}"


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
        "pages": get_pages(),  # my.Page.objects.all().order_by('order'),
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
        vervolg = ''
    elif event:
        event = get_object_or_404(my.Event, pk=event)
        verb = 'bijgewerkt'
        vervolg = f'#ev{event.id}'
    else:
        raise Http404    # Response(f"{actie} {event}")

    event.text = tekst
    event.save()
    return f"/{proj}/{actie.id}/mld/De gebeurtenis is {verb}./{vervolg}"


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


def is_admin(project, user):
    """geeft indicatie terug of de betreffende gebruiker
    acties en settings mag wijzigen
    """
    for grp in user.groups.all():
        if grp.name == f'{project.name}_admin':
            return True
    return False


def filter_data_on_nummer(data, seltest):
    "apply filter on 'nummer' to the data"
    filtered = seltest.filter(veldnm="nummer")
    if len(filtered) > 0:
        if filtered[0].operator.upper() == 'GT':
            query1 = data.filter(nummer__gt=filtered[0].value)
        else:
            query1 = data.filter(nummer__lt=filtered[0].value)
        if len(filtered) > 1:
            if filtered[1].operator.upper() == 'GT':
                query2 = data.filter(nummer__gt=filtered[1].value)
            else:
                query2 = data.filter(nummer__lt=filtered[1].value)
            if filtered[1].extra.upper() in ('EN', 'AND'):
                data = query1 & query2
            else:
                data = query1 | query2
        else:
            data = query1
    return data


def filter_data_on_soort(data, seltest):
    "apply filter on 'soort' to the data"
    filtered = seltest.filter(veldnm="soort")
    sel = [my.Soort.objects.get(project=x.project, value=x.value).id for x in filtered]
    if sel:
        data = data.filter(soort__in=sel)
    return data


def filter_data_on_status(data, seltest):
    "apply filter on 'status' to the data"
    filtered = seltest.filter(veldnm="status")
    sel = [my.Status.objects.get(project=x.project, value=int(x.value)).id for x in filtered]
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
    filtered1 = seltest.filter(veldnm="about")
    filtered2 = seltest.filter(veldnm="title")
    if filtered1:
        query1 = data.filter(about__icontains=filtered1[0].value)
    if filtered2:
        query2 = data.filter(title__icontains=filtered2[0].value)
    if filtered1 and filtered2:
        if filtered2[0].extra.upper() in ('AND', 'EN'):
            data = query1 & query2
        else:
            data = query1 | query2
    elif filtered1:
        data = query1
    elif filtered2:
        data = query2
    return data


def filter_data_on_arch(data, seltest):
    "apply filter on archive status to the data"
    filtered = seltest.filter(veldnm="arch")
    if filtered:
        if filtered[0].value == 'False':
            data = data.exclude(arch=True)
        else:
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


def store_gewijzigd(msg, txt, mld, actie, user):
    """Maak nieuw standaard event (rubriek X is gewijzigd)
    """
    store_event(f'{msg} gewijzigd in "{txt}"', actie, user)
    mld.append(msg)
    return mld


def is_system_event(event):
    "determine if event text should not be editable"
    if event.text in ('Actie opgevoerd', 'Meldingtekst aangepast', 'Actie gearchiveerd',
                      'Actie herleefd'):
        return True
    if event.text.startswith(('categorie is', 'status is', 'onderwerp gewijzigd in',
                              'titel gewijzigd in', 'behandelaar gewijzigd in',
                              'categorie gewijzigd in', 'status gewijzigd in')):
        return True
    return False


def get_pages():
    "return a sorted list of all the pages to show"
    return my.Page.objects.filter(link__in=['index']).order_by('order')
