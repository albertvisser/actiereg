import os
import types
import datetime
import pytest
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'actiereg.settings')
django.setup()
from django.contrib.auth import models as auth

import tracker.models as my
from tracker import views

FIXDATE = datetime.datetime(2020, 1, 1)
pytestmark = pytest.mark.django_db

def test_index(monkeypatch):
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    myuser2 = auth.User.objects.create(username='myself')
    request = types.SimpleNamespace(user=myuser, GET={})
    request2 = types.SimpleNamespace(user=myuser, GET={'user': myuser2})
    request3 = types.SimpleNamespace(user=myuser, GET={'msg': 'massage'})
    monkeypatch.setattr(views.core, 'get_appropriate_login_message', lambda *x: 'login_message')
    myproject = my.Project.objects.create(name='first', description='a project')
    mypage = my.Page.objects.create(link='x/', order=1, title='z')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    mystatus2 = my.Status.objects.create(project=myproject, order=2, value=2, title='z!')
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    myactie1 = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    myactie2 = my.Actie.objects.create(project=myproject, nummer='y', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus2, behandelaar=myuser)
    myactie3 = my.Actie.objects.create(project=myproject, nummer='z', starter=myuser,
                                      lasteditor=myuser, arch=True,
                                      soort=mysoort, status=mystatus2, behandelaar=myuser)
    myproject = my.Project.objects.create(name='ahem', description='another project')
    assert views.index(request, 'message') == (
            request, 'index.html',
            {'apps': [{'root': 2, 'name': 'ahem', 'desc': 'another project',
                      'alle': 0, 'open': 0, 'active': 0},
                      {'root': 1, 'name': 'first', 'desc': 'a project',
                      'alle': 3, 'open': 2, 'active': 1}],
             'new': [], 'msg': 'message<br/><br/>login_message', 'who': myuser})
    assert views.index(request2) == (
            request2, 'index.html',
            {'apps': [{'root': 2, 'name': 'ahem', 'desc': 'another project',
                      'alle': 0, 'open': 0, 'active': 0},
                      {'root': 1, 'name': 'first', 'desc': 'a project',
                      'alle': 3, 'open': 2, 'active': 1}],
             'new': [], 'msg': 'login_message', 'who': myuser2})
    assert views.index(request3) == (
            request3, 'index.html',
            {'apps': [{'root': 2, 'name': 'ahem', 'desc': 'another project',
                      'alle': 0, 'open': 0, 'active': 0},
                      {'root': 1, 'name': 'first', 'desc': 'a project',
                      'alle': 3, 'open': 2, 'active': 1}],
             'new': [], 'msg': 'massage<br/><br/>login_message', 'who': myuser})

def test_log_out(monkeypatch, capsys):
    def mock_logout(*args):
        print('called logout()')
    monkeypatch.setattr(views, 'logout', mock_logout)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser, GET={})
    assert views.log_out(request) == (request, 'logged_out.html',
                                     {'next': '/accounts/login/?next=/'})
    assert capsys.readouterr().out == 'called logout()\n'
    request = types.SimpleNamespace(user=myuser, GET={'next': 'volgende'})
    assert views.log_out(request) == (request, 'logged_out.html',
                                      {'next': '/accounts/login/?next=volgende'})
    assert capsys.readouterr().out == 'called logout()\n'

def test_new_project(monkeypatch):
    monkeypatch.setattr(views.core, 'not_logged_in_message', lambda x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    request = types.SimpleNamespace(user=auth.AnonymousUser())
    assert views.new_project(request) == 'een project aan te kunnen maken'
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.new_project(request) == (request, 'nieuw.html', {})

def test_add_project(monkeypatch, capsys):
    def mock_add_project(*args):
        print('called core.add_project with args', args)
    monkeypatch.setattr(views.core, 'add_project', mock_add_project)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser, POST={'name': 'new', 'desc': 'project'})
    assert views.add_project(request) == '/msg/project aangemaakt/'
    assert capsys.readouterr().out == "called core.add_project with args ('new', 'project')\n"

def test_add_from_doctool(monkeypatch, capsys):
    def mock_add_project(*args):
        print('called core.add_project with args', args)
        return 2
    monkeypatch.setattr(views.core, 'add_project', mock_add_project)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.add_from_doctool(request, 1, 'new', 'project') == (
            f"{views.SITES['doctool']}/1/meld/Project new is aangemaakt met id 2/")
    assert capsys.readouterr().out == "called core.add_project with args ('new', 'project')\n"

def test_show_project(monkeypatch, capsys):
    monkeypatch.setattr(views.core, 'get_appropriate_login_message', lambda *x: 'login_message')
    monkeypatch.setattr(views.core, 'build_pagedata_for_project', lambda *x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    request = types.SimpleNamespace(user=auth.AnonymousUser())
    assert views.show_project(request, 'proj') == (request, 'tracker/index.html',
                                                   (request, 'proj', 'login_message'))
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.show_project(request, 'proj') == (request, 'tracker/index.html',
                                                   (request, 'proj', 'login_messageKlik op een'
                                                    ' actienummer om de details te bekijken.'))

def test_show_settings(monkeypatch, capsys):
    monkeypatch.setattr(views.core, 'no_authorization_message', lambda *x: x)
    monkeypatch.setattr(views.core, 'build_pagedata_for_settings', lambda *x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: False)
    assert views.show_settings(request, 'proj') == ('instellingen te wijzigen', 'proj')
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: True)
    assert views.show_settings(request, 'proj') == (request, 'tracker/settings.html',
                                                    (request, 'proj'))

def test_setusers(monkeypatch, capsys):
    def mock_set_users(*args):
        print('called core.set_users')
    monkeypatch.setattr(views.core, 'no_authorization_message', lambda *x: x)
    monkeypatch.setattr(views.core, 'set_users', mock_set_users)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: False)
    assert views.setusers(request, 'proj') == ('instellingen te wijzigen', 'proj')
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: True)
    assert views.setusers(request, 'proj') == '/proj/settings/'
    assert capsys.readouterr().out == "called core.set_users\n"

def test_settabs(monkeypatch, capsys):
    def mock_set_tabs(*args):
        print('called core.set_tabs')
    monkeypatch.setattr(views.core, 'no_authorization_message', lambda *x: x)
    monkeypatch.setattr(views.core, 'set_tabs', mock_set_tabs)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: False)
    assert views.settabs(request, 'proj') == ('instellingen te wijzigen', 'proj')
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: True)
    assert views.settabs(request, 'proj') == '/proj/settings/'
    assert capsys.readouterr().out == "called core.set_tabs\n"

def test_settypes(monkeypatch, capsys):
    def mock_set_types(*args):
        print('called core.set_types')
    monkeypatch.setattr(views.core, 'no_authorization_message', lambda *x: x)
    monkeypatch.setattr(views.core, 'set_types', mock_set_types)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: False)
    assert views.settypes(request, 'proj') == ('instellingen te wijzigen', 'proj')
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: True)
    assert views.settypes(request, 'proj') == '/proj/settings/'
    assert capsys.readouterr().out == "called core.set_types\n"

def test_setstats(monkeypatch, capsys):
    def mock_set_stats(*args):
        print('called core.set_stats')
    monkeypatch.setattr(views.core, 'no_authorization_message', lambda *x: x)
    monkeypatch.setattr(views.core, 'set_stats', mock_set_stats)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: False)
    assert views.setstats(request, 'proj') == ('instellingen te wijzigen', 'proj')
    monkeypatch.setattr(views.core, 'is_admin', lambda *x: True)
    assert views.setstats(request, 'proj') == '/proj/settings/'
    assert capsys.readouterr().out == "called core.set_stats\n"

def test_show_selection(monkeypatch):
    # noauth = types.SimpleNamespace(username='MyName', is_authenticated=False)
    monkeypatch.setattr(views.core, 'logged_in_message', lambda *x: 'logged in')
    # monkeypatch.setattr(views.core, 'not_logged_in_message', lambda *x: x)
    monkeypatch.setattr(views, 'HttpResponse', lambda x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    # request = types.SimpleNamespace(user=auth.AnonymousUser())
    # assert views.show_selection(request, 'proj') == (
    #         'de selectie voor dit scherm te mogen wijzigen')
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'build_pagedata_for_selection', lambda *x: (x, 'oh-oh'))
    assert views.show_selection(request, 'proj') == 'oh-oh'
    monkeypatch.setattr(views.core, 'build_pagedata_for_selection', lambda *x: (x, ''))
    assert views.show_selection(request, 'proj') == (
            request, 'tracker/select.html', (request, 'proj', 'logged in'))

def test_setselection(monkeypatch, capsys):
    def mock_setselection(*args):
        print('called core.setselection with args', args)
    monkeypatch.setattr(views.core, 'setselection', mock_setselection)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.setselection(request, 'proj') == '/proj/meld/De selectie is gewijzigd./'
    assert capsys.readouterr().out == f"called core.setselection with args ({request}, 'proj')\n"

def test_show_ordering(monkeypatch):
    monkeypatch.setattr(views.core, 'logged_in_message', lambda *x: 'logged in')
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'build_pagedata_for_ordering', lambda *x: x)
    assert views.show_ordering(request, 'proj') == (
            request, 'tracker/order.html', (request, 'proj', 'logged in'))

def test_setordering(monkeypatch, capsys):
    def mock_setordering(*args):
        print('called core.setordering with args', args)
    monkeypatch.setattr(views.core, 'setordering', mock_setordering)
    monkeypatch.setattr(views, 'HttpResponseRedirect', lambda x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.setordering(request, 'proj') == '/proj/meld/De sortering is gewijzigd./'
    assert capsys.readouterr().out == f"called core.setordering with args ({request}, 'proj')\n"

def test_new_action(monkeypatch):
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'build_pagedata_for_detail', lambda *x: x)
    assert views.new_action(request, 'proj', 'message') == (
            request, 'tracker/actie.html', (request, 'proj', 'new', 'message'))

def test_show_action(monkeypatch):
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'build_pagedata_for_detail', lambda *x: x)
    assert views.show_action(request, 'proj', 'actie', 'message') == (
            request, 'tracker/actie.html', (request, 'proj', 'actie', 'message'))

@pytest.mark.django_db
def test_add_action(monkeypatch):
    project = my.Project.objects.create(name='first')
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_detail', lambda x, y, z: (x, y, z))
    monkeypatch.setattr(views.core, 'no_authorization_message', lambda *x: 'noauth')
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'is_user', lambda *x: False)
    assert views.add_action(request, project.id) == 'noauth'
    monkeypatch.setattr(views.core, 'is_user', lambda *x: True)
    assert views.add_action(request, project.id) == (request, project, 'nieuw')

def test_add_action_from_doctool(monkeypatch, capsys):
    def mock_add_spec(*args):
        print('called copy_existing_action_from_here with args', args)
        return 'response x'
    def mock_add_new(*args):
        print('called add_new_action_on_both_sides with args', args)
        return 'response y'
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'copy_existing_action_from_here', mock_add_spec)
    monkeypatch.setattr(views.core, 'add_new_action_on_both_sides', mock_add_new)
    proj = 'qq'
    request = types.SimpleNamespace(POST={})
    assert views.add_action_from_doctool(request, proj) == 'response y'
    assert capsys.readouterr().out == ("called add_new_action_on_both_sides with args"
                                       " ('qq', {}, '', '')\n")
    request = types.SimpleNamespace(POST={'hFrom':'next', 'hUser':'me'})
    assert views.add_action_from_doctool(request, proj) == 'response y'
    assert capsys.readouterr().out == ("called add_new_action_on_both_sides with args"
                                       f" ('qq', {request.POST}, 'me', 'next')\n")
    request = types.SimpleNamespace(POST={'hFrom':'next', 'hUser':'me', 'tActie':'x'})
    assert views.add_action_from_doctool(request, proj) == 'response x'
    assert capsys.readouterr().out == ("called copy_existing_action_from_here with args"
                                       " ('qq', 'x', 'me', 'next')\n")

@pytest.mark.django_db
def test_update_action(monkeypatch):
    project = my.Project.objects.create(name='first')
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_detail', lambda x, y, z: (x, y, z))
    monkeypatch.setattr(views.core, 'no_authorization_message', lambda *x: 'noauth')
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    monkeypatch.setattr(views.core, 'is_user', lambda *x: False)
    assert views.update_action(request, project.id, 'actie') == 'noauth'
    monkeypatch.setattr(views.core, 'is_user', lambda *x: True)
    assert views.update_action(request, project.id, 'actie') == (request, project, 'actie')

def test_show_meld(monkeypatch):
    monkeypatch.setattr(views.core, 'build_pagedata_for_tekstpage', lambda *x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.show_meld(request, 'proj', 'actie', 'melding') == (
            request, 'tracker/tekst.html', (request, 'proj', 'actie', 'meld', 'melding'))

def test_show_oorz(monkeypatch):
    monkeypatch.setattr(views.core, 'build_pagedata_for_tekstpage', lambda *x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.show_oorz(request, 'proj', 'actie', 'melding') == (
            request, 'tracker/tekst.html', (request, 'proj', 'actie', 'oorz', 'melding'))

def test_show_opl(monkeypatch):
    monkeypatch.setattr(views.core, 'build_pagedata_for_tekstpage', lambda *x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.show_opl(request, 'proj', 'actie', 'melding') == (
            request, 'tracker/tekst.html', (request, 'proj', 'actie', 'opl', 'melding'))

def test_show_verv(monkeypatch):
    monkeypatch.setattr(views.core, 'build_pagedata_for_tekstpage', lambda *x: x)
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.show_verv(request, 'proj', 'actie', 'melding') == (
            request, 'tracker/tekst.html', (request, 'proj', 'actie', 'verv', 'melding'))

def test_update_meld(monkeypatch):
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_tekstpage', lambda x, y, z, a: (x, y, z, a))
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.update_meld(request, 'proj', 'actie') == (request, 'proj', 'actie', 'meld')

def test_update_oorz(monkeypatch):
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_tekstpage', lambda x, y, z, a: (x, y, z, a))
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.update_oorz(request, 'proj', 'actie') == (request, 'proj', 'actie', 'oorz')

def test_update_opl(monkeypatch):
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_tekstpage', lambda x, y, z, a: (x, y, z, a))
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.update_opl(request, 'proj', 'actie') == (request, 'proj', 'actie', 'opl')

def test_update_verv(monkeypatch):
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_tekstpage', lambda x, y, z, a: (x, y, z, a))
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.update_verv(request, 'proj', 'actie') == (request, 'proj', 'actie', 'verv')

def test_show_events(monkeypatch):
    monkeypatch.setattr(views.core, 'build_pagedata_for_events', lambda *x, **y: (x, y))
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.show_events(request, 'proj', 'actie') == (
            request, 'tracker/voortgang.html', ((request, 'proj', 'actie'), {'msg': ''}))

    monkeypatch.setattr(views.core, 'build_pagedata_for_events', lambda *x, **y: (x, y))
    monkeypatch.setattr(views, 'render', lambda *x: x)
    assert views.show_events(request, 'proj', 'actie', msg='melding') == (
            request, 'tracker/voortgang.html', ((request, 'proj', 'actie'), {'msg': 'melding'}))

def test_new_event(monkeypatch):
    monkeypatch.setattr(views.core, 'build_pagedata_for_events', lambda *x, **y: (x, y))
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.new_event(request, 'proj', 'actie') == (
            request, 'tracker/voortgang.html', ((request, 'proj', 'actie'), {'event': 'nieuw'}))

def test_edit_event(monkeypatch):
    monkeypatch.setattr(views.core, 'build_pagedata_for_events', lambda *x, **y: (x, y))
    monkeypatch.setattr(views, 'render', lambda *x: x)
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.edit_event(request, 'proj', 'actie', 15) == (
            request, 'tracker/voortgang.html', ((request, 'proj', 'actie'), {'event': 15}))

def test_add_event(monkeypatch):
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_events', lambda x, y, z, a: (x, y, z, a))
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.add_event(request, 'proj', 'actie') == (request, 'proj', 'actie', 'nieuw')

def test_update_event(monkeypatch):
    monkeypatch.setattr(views, 'HttpResponseRedirect' , lambda x: x)
    monkeypatch.setattr(views.core, 'wijzig_events', lambda x, y, z, a: (x, y, z, a))
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    assert views.update_event(request, 'proj', 'actie', 'event') == (request, 'proj', 'actie',
                                                                     'event')
