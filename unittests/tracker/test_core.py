"""unittests for ./tracker/core.py
"""
import os
import types
import datetime
import pytest
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'actiereg.settings')
django.setup()
# from django.contrib.auth import models as auth
# from django.core.exceptions import ObjectDoesNotExist
# from django.http.response import Http404
from django.http import QueryDict
from tracker import core as testee
# import tracker.models as my
auth = testee.auth
my = testee.my

FIXDATE = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

def test_get_appropriate_login_message():
    """unittest for core.get_appropriate_login_message
    """
    noauth = types.SimpleNamespace(username='MyName', is_authenticated=False)
    assert testee.get_appropriate_login_message(noauth) == (
            'U bent niet ingelogd.'
            ' Klik <a href="/accounts/login/?next=/">hier</a> om in te loggen. ')
    user_ok = types.SimpleNamespace(username='MyName', is_authenticated=True)
    assert testee.get_appropriate_login_message(user_ok, 1, 'actie') == (
            'U bent ingelogd als <i>MyName</i>.'
            ' Klik <a href="/logout/?next=/1/actie/">hier</a> om uit te loggen. ')

def test_no_authorization_message(monkeypatch):
    """unittest for core.no_authorization_message
    """
    monkeypatch.setattr(testee, 'HttpResponse', lambda x: x)
    assert testee.no_authorization_message('iets te doen') == (
            "U bent niet geautoriseerd om iets te doen<br>"
            'Klik <a href="/">hier</a> om door te gaan')
    assert testee.no_authorization_message('iets te doen', 1) == (
            "U bent niet geautoriseerd om iets te doen<br>"
            'Klik <a href="/1/">hier</a> om door te gaan')

def test_logged_in_message():
    """unittest for core.logged_in_message
    """
    class MockRequest:
        """stub
        """
        user = types.SimpleNamespace(username='MyName')
    assert testee.logged_in_message(MockRequest()) == ('U bent ingelogd als <i>MyName</i>. '
            'Klik <a href="/logout/?next=/select/">hier</a> om uit te loggen.'
            'Klik <a href="/">hier</a> om door te gaan')
    assert testee.logged_in_message(MockRequest(), 1) == ('U bent ingelogd als <i>MyName</i>. '
            'Klik <a href="/logout/?next=/1/select/">hier</a> om uit te loggen.'
            'Klik <a href="/1/">hier</a> om door te gaan')

def test_not_logged_in_message(monkeypatch):
    """unittest for core.not_logged_in_message
    """
    monkeypatch.setattr(testee, 'HttpResponse', lambda x: x)
    assert testee.not_logged_in_message('iets te doen') == (
            '<html><body style="background-color: lightblue">U moet ingelogd zijn om iets te doen.'
            '<br/><br/>Klik <a href="/accounts/login/?next=/select/">hier</a> om in te loggen'
            ', <a href="/">hier</a> om terug te gaan.<body></html>')
    assert testee.not_logged_in_message('iets te doen', 1) == (
            '<html><body style="background-color: lightblue">U moet ingelogd zijn om iets te doen.'
            '<br/><br/>Klik <a href="/accounts/login/?next=/1/select/">hier</a> om in te loggen'
            ', <a href="/1/">hier</a> om terug te gaan.<body></html>')

def test_determine_readonly(monkeypatch):
    """unittest for core.determine_readonly
    """
    monkeypatch.setattr(testee, 'is_user', lambda *x: False)
    assert testee.determine_readonly('project', 'user')
    monkeypatch.setattr(testee, 'is_user', lambda *x: True)
    assert not testee.determine_readonly('project', 'user')

@pytest.mark.django_db
def test_is_user():
    """unittest for core.is_user
    """
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    assert not list(project.workers.all())
    assert not testee.is_user(project, user)
    worker = my.Worker.objects.create(project=project, assigned=user)
    assert len(list(project.workers.all())) == 1
    assert list(project.workers.all())[0].assigned == user
    assert testee.is_user(project, user)

@pytest.mark.django_db
def test_is_admin():
    """unittest for core.is_admin
    """
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    assert not list(user.groups.all())
    assert not testee.is_admin(project, user)
    group = auth.Group.objects.create(name=f'{project}_user')
    user.groups.add(group)
    assert len(list(user.groups.all())) == 1
    assert user.groups.all()[0] == group
    assert not testee.is_admin(project, user)
    group = auth.Group.objects.create(name=f'{project}_admin')
    user.groups.add(group)
    assert len(list(user.groups.all())) == 2
    assert user.groups.all()[1] == group
    assert testee.is_admin(project, user)

@pytest.mark.django_db
def test_filter_data_on_nummer():
    """unittest for core.filter_data_on_nummer
    """
    # voorlopig de except SyntaxError op de eval maar even laten zitten
    # toch nog maar eens kijken of ik het niet met eval voor elkaar kan krijgen
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    actie1 = my.Actie.objects.create(project=project, nummer='0001', starter=user, lasteditor=user,
                                     soort=soort, status=status, behandelaar=user)
    actie2 = my.Actie.objects.create(project=project, nummer='0002', starter=user, lasteditor=user,
                                     soort=soort, status=status, behandelaar=user)
    actie3 = my.Actie.objects.create(project=project, nummer='0003', starter=user, lasteditor=user,
                                     soort=soort, status=status, behandelaar=user)
    actie4 = my.Actie.objects.create(project=project, nummer='0004', starter=user, lasteditor=user,
                                     soort=soort, status=status, behandelaar=user)
    data = testee.filter_data_on_nummer(my.Actie.objects.all(), my.Selection.objects.all())
    assert list(data) == [actie1, actie2, actie3, actie4]  # 4  # geen filters -> alles

    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0001',
                                operator='GT')
    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0004',
                                operator='LT', extra='en')
    data = testee.filter_data_on_nummer(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0002', '0003']

    my.Selection.objects.all().delete()
    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0002',
                                operator='LT')
    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0003',
                                operator='GT', extra='of')
    data = testee.filter_data_on_nummer(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0004']

    my.Selection.objects.all().delete()
    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0001',
                                operator='GT')
    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0004',
                                operator='LT', extra='and')
    data = testee.filter_data_on_nummer(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0002', '0003']

    my.Selection.objects.all().delete()
    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0002',
                                operator='LT')
    my.Selection.objects.create(user=user.id, project=project, veldnm="nummer", value='0003',
                                operator='GT', extra='or')
    data = testee.filter_data_on_nummer(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0004']

@pytest.mark.django_db
def test_filter_data_on_soort():
    """unittest for core.filter_data_on_soort
    """
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    soort2 = my.Soort.objects.create(project=project, title='y', order=1, value='y')
    soort3 = my.Soort.objects.create(project=project, title='z', order=2, value='z')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    my.Actie.objects.create(project=project, nummer='0001', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0002', starter=user, lasteditor=user,
                            soort=soort2, status=status, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0003', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0004', starter=user, lasteditor=user,
                            soort=soort3, status=status, behandelaar=user)
    my.Selection.objects.create(user=user.id, project=project, veldnm="qqqqq", value='x')
    data = testee.filter_data_on_soort(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0002', '0003', '0004']
    my.Selection.objects.create(user=user.id, project=project, veldnm="soort", value='x')
    data = testee.filter_data_on_soort(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003']

    my.Selection.objects.create(user=user.id, project=project, veldnm="soort", value='y')
    data = testee.filter_data_on_soort(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003', '0002']

@pytest.mark.django_db
def test_filter_data_on_status():
    """unittest for core.filter_data_on_status
    """
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    status2 = my.Status.objects.create(project=project, title='x', order=1, value=1)
    status3 = my.Status.objects.create(project=project, title='x', order=2, value=2)
    my.Actie.objects.create(project=project, nummer='0001', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0002', starter=user, lasteditor=user,
                            soort=soort, status=status2, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0003', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0004', starter=user, lasteditor=user,
                            soort=soort, status=status3, behandelaar=user)
    my.Selection.objects.create(user=user.id, project=project, veldnm="qqqqq", value=1)
    data = testee.filter_data_on_status(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0002', '0003', '0004']
    my.Selection.objects.create(user=user.id, project=project, veldnm="status", value='0')
    data = testee.filter_data_on_status(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003']

    my.Selection.objects.create(user=user.id, project=project, veldnm="status", value=1)
    data = testee.filter_data_on_status(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003', '0002']

@pytest.mark.django_db
def test_filter_data_on_user():
    """unittest for core.filter_data_on_user
    """
    user = auth.User.objects.create(username='me')
    user2 = auth.User.objects.create(username='mine')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    my.Actie.objects.create(project=project, nummer='0001', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0002', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user2)
    my.Actie.objects.create(project=project, nummer='0003', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user)
    my.Actie.objects.create(project=project, nummer='0004', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user2)
    my.Selection.objects.create(user=user.id, project=project, veldnm="qqqq", value=user.id)
    data = testee.filter_data_on_user(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0002', '0003', '0004']
    my.Selection.objects.create(user=user.id, project=project, veldnm="user", value=user.id)
    data = testee.filter_data_on_user(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003']

# 948->950
@pytest.mark.django_db
def test_filter_data_on_description():
    """unittest for core.filter_data_on_description
    """
    # voorlopig de except SyntaxError op de eval maar even laten zitten
    # toch nog maar eens kijken of ik het niet met eval voor elkaar kan krijgen
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    my.Actie.objects.create(project=project, nummer='0001', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user,
                            about='1111', title='aaaaaa')
    my.Actie.objects.create(project=project, nummer='0002', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user,
                            about='2222', title='bbbbbb')
    my.Actie.objects.create(project=project, nummer='0003', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user,
                            about='1111', title='cccccc')
    my.Actie.objects.create(project=project, nummer='0004', starter=user, lasteditor=user,
                            soort=soort, status=status, behandelaar=user,
                            about='2222', title='dddddd')
    data = testee.filter_data_on_description(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0002', '0003', '0004']
    my.Selection.objects.create(user=user.id, project=project, veldnm="about", value='')
    data = testee.filter_data_on_description(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0002', '0003', '0004']
    my.Selection.objects.all().delete()
    my.Selection.objects.create(user=user.id, project=project, veldnm="about", value='11')
    my.Selection.objects.create(user=user.id, project=project, veldnm="title", value='',
                                extra='of')
    data = testee.filter_data_on_description(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003']
    my.Selection.objects.all().delete()
    my.Selection.objects.create(user=user.id, project=project, veldnm="title", value='bb',
                                extra='of')
    data = testee.filter_data_on_description(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0002']
    my.Selection.objects.all().delete()
    my.Selection.objects.create(user=user.id, project=project, veldnm="about", value='11')
    my.Selection.objects.create(user=user.id, project=project, veldnm="title", value='bb',
                                extra='of')
    data = testee.filter_data_on_description(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0002', '0003']
    my.Selection.objects.all().delete()
    my.Selection.objects.create(user=user.id, project=project, veldnm="about", value='11')
    my.Selection.objects.create(user=user.id, project=project, veldnm="title", value='cc',
                                extra='en')
    data = testee.filter_data_on_description(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0003']

@pytest.mark.django_db
def test_filter_data_on_arch():
    """unittest for core.filter_data_on_arch
    """
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    actie = my.Actie.objects.create(project=project, nummer='0001', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user)
    actie = my.Actie.objects.create(project=project, nummer='0002', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user, arch=True)
    actie = my.Actie.objects.create(project=project, nummer='0003', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user, arch=False)
    actie = my.Actie.objects.create(project=project, nummer='0004', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user, arch=True)
    data = testee.filter_data_on_arch(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003']

    my.Selection.objects.create(user=user.id, project=project, veldnm="arch")
    data = testee.filter_data_on_arch(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0002', '0004']

    # kan eigenlijk niet?
    my.Selection.objects.create(user=user.id, project=project, veldnm="arch")
    data = testee.filter_data_on_arch(my.Actie.objects.all(), my.Selection.objects.all())
    assert [x.nummer for x in data] == ['0001', '0002', '0003', '0004']

@pytest.mark.django_db
def test_apply_sorters():
    """unittest for core.apply_sorters
    """
    user = auth.User.objects.create(username='me')
    user2 = auth.User.objects.create(username='also me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    actie = my.Actie.objects.create(project=project, nummer='0001', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user,
                                    about='aa', title='22')
    actie = my.Actie.objects.create(project=project, nummer='0002', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user2, arch=True,
                                    about='bb', title='11')
    actie = my.Actie.objects.create(project=project, nummer='0003', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user, arch=False,
                                    about='aa', title='11')
    actie = my.Actie.objects.create(project=project, nummer='0004', starter=user, lasteditor=user,
                                    soort=soort, status=status, behandelaar=user2, arch=True,
                                    about='bb', title='02')

    my.SortOrder.objects.create(user=user.id, project=project, volgnr=1, veldnm='title',
                                richting='asc')
    data = testee.apply_sorters(my.Actie.objects.all(), my.SortOrder.objects.all())
    assert [x.nummer for x in data] == ['0003', '0001', '0004', '0002']

    my.SortOrder.objects.all().delete()
    my.SortOrder.objects.create(user=user.id, project=project, volgnr=1, veldnm='title',
                                richting='desc')
    data = testee.apply_sorters(my.Actie.objects.all(), my.SortOrder.objects.all())
    assert [x.nummer for x in data] == ['0002', '0004', '0001', '0003']

    my.SortOrder.objects.all().delete()
    my.SortOrder.objects.create(user=user.id, project=project, volgnr=1, veldnm='behandelaar',
                                richting='asc')
    my.SortOrder.objects.create(user=user.id, project=project, volgnr=2, veldnm='nummer',
                                richting='desc')
    data = testee.apply_sorters(my.Actie.objects.all(), my.SortOrder.objects.all())
    assert [x.nummer for x in data] == ['0004', '0002', '0003', '0001']

    my.SortOrder.objects.all().delete()
    my.SortOrder.objects.create(user=user.id, project=project, volgnr=1, veldnm='behandelaar',
                                richting='desc')
    my.SortOrder.objects.create(user=user.id, project=project, volgnr=2, veldnm='nummer',
                                richting='asc')
    data = testee.apply_sorters(my.Actie.objects.all(), my.SortOrder.objects.all())
    assert [x.nummer for x in data] == ['0001', '0003', '0002', '0004']

@pytest.mark.django_db
def test_store_event():
    """unittest for core.store_event
    """
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    actie = my.Actie.objects.create(project=project, starter=user, lasteditor=user, soort=soort,
                                    status=status, behandelaar=user)
    assert not list(actie.events.all())
    testee.store_event('hallo', actie, user)
    assert len(list(actie.events.all())) == 1
    event = list(actie.events.all())[0]
    assert event.actie == actie
    assert event.starter == user
    assert event.text == 'hallo'

@pytest.mark.django_db
def test_store_gewijzigd():
    """unittest for core.store_gewijzigd
    """
    user = auth.User.objects.create(username='me')
    project = my.Project.objects.create(name='first')
    soort = my.Soort.objects.create(project=project, title='x', order=0, value='x')
    status = my.Status.objects.create(project=project, title='x', order=0, value=0)
    actie = my.Actie.objects.create(project=project, starter=user, lasteditor=user, soort=soort,
                                    status=status, behandelaar=user)
    assert not list(actie.events.all())
    assert testee.store_gewijzigd('rubriek', 'waarde', [], actie, user) == ['rubriek']
    assert len(list(actie.events.all())) == 1
    event = list(actie.events.all())[0]
    assert event.actie == actie
    assert event.starter == user
    assert event.text == 'rubriek gewijzigd in "waarde"'

@pytest.mark.django_db
def test_build_pagedata_for_newproj():
    """unittest for core.build_pagedata_for_newproj
    """
    user1 = auth.User.objects.create(username='me')
    user2 = auth.User.objects.create(username='also me')
    user3 = auth.User.objects.create(username='me too')
    assert testee.build_pagedata_for_newproj() == {'all_users': [user2, user1, user3]}

@pytest.mark.django_db
def test_add_project(monkeypatch, capsys):
    """unittest for core.add_project
    """
    def mock_add_default_pages():
        """stub
        """
        print('called add_default_pages()')
    def mock_add_default_soorten(proj):
        """stub
        """
        print(f'called add_default_soorten() for project {proj}')
    def mock_add_default_statussen(proj):
        """stub
        """
        print(f'called add_default_statussen() for project {proj}')
    def mock_add_auth_for_project(proj):
        """stub
        """
        print(f'called add_auth_for_project() for project {proj}')
    def mock_add_admins(proj, admins):
        """stub
        """
        print(f'called add_admins() for project {proj} with arg {admins}')
    monkeypatch.setattr(testee, 'add_default_pages', mock_add_default_pages)
    monkeypatch.setattr(testee, 'add_default_soorten', mock_add_default_soorten)
    monkeypatch.setattr(testee, 'add_default_statussen', mock_add_default_statussen)
    monkeypatch.setattr(testee, 'add_auth_for_project', mock_add_auth_for_project)
    monkeypatch.setattr(testee, 'add_admins', mock_add_admins)
    start_id = my.Project.objects.create(name='dummy').id
    assert my.Page.objects.count() == 0
    new_id = start_id + 1
    assert testee.add_project('name', 'desc', []) == new_id
    proj = my.Project.objects.get(pk=new_id)
    assert proj.name, proj.desc == ('name', 'desc')
    assert capsys.readouterr().out == ('called add_default_pages()\n'
                                       'called add_default_soorten() for project name\n'
                                       'called add_default_statussen() for project name\n'
                                       'called add_auth_for_project() for project name\n'
                                       'called add_admins() for project name with arg []\n')
    new_id += 1
    my.Page.objects.create(link='x', order=0, title='y')
    assert testee.add_project('name2', 'desc2', ['1']) == new_id
    dproj = my.Project.objects.get(pk=new_id)
    assert proj.name, proj.desc == ('name2', 'desc2')
    assert capsys.readouterr().out == ('called add_default_soorten() for project name2\n'
                                       'called add_default_statussen() for project name2\n'
                                       'called add_auth_for_project() for project name2\n'
                                       "called add_admins() for project name2 with arg ['1']\n")

@pytest.mark.django_db
def test_add_default_pages():
    """unittest for core.add_default_pages
    """
    assert not list(my.Page.objects.all())
    expected = [("index", 0, "lijst"),
                ("detail", 1, "titel/status"),
                ("meld", 2, "probleem/wens"),
                ("oorz", 3, "oorzaak/analyse"),
                ("opl", 4, "oplossing"),
                ("verv", 5, "vervolgactie"),
                ("voortg", 6, "voortgang")]
    testee.add_default_pages()
    count = 0
    for item in my.Page.objects.all():
        assert (item.link, item.order, item.title) == expected[count]
        count += 1
    assert count == len(expected)

@pytest.mark.django_db
def test_add_default_soorten():
    """unittest for core.add_default_soorten
    """
    project = my.Project.objects.create(name='first')
    assert not list(project.soort.all())
    expected = [(0, " ", "onbekend"),
                (1, "P", "probleem"),
                (2, "W", "wens"),
                (3, "V", "vraag"),
                (4, "I", "idee"),
                (5, "F", "diverse informatie")]
    testee.add_default_soorten(project)
    count = 0
    for item in project.soort.all():
        assert (item.order, item.value, item.title) == expected[count]
        count += 1
    assert count == len(expected)  # 6

@pytest.mark.django_db
def test_add_default_statussen():
    """unittest for core.add_default_statussen
    """
    project = my.Project.objects.create(name='first')
    assert not list(project.status.all())
    expected = [(0, 0, "gemeld"),
                (1, 1, "in behandeling"),
                (2, 2, "oplossing controleren"),
                (3, 3, "nog niet opgelost"),
                (4, 4, "afgehandeld - opgelost"),
                (5, 5, "afgehandeld - vervolg")]
    testee.add_default_statussen(project)
    count = 0
    for item in project.status.all():
        assert (item.order, item.value, item.title) == expected[count]
        count += 1
    assert count == len(expected)

@pytest.mark.django_db
def test_add_auth_for_project():
    """unittest for core.add_auth_for_project
    """
    project = my.Project.objects.create(name='first')
    testee.add_auth_for_project(project)
    grp1 = auth.Group.objects.get(name='first_admin')
    assert len(grp1.permissions.all()) == 36
    grp2 = auth.Group.objects.get(name='first_user')
    assert len(grp2.permissions.all()) == 16

@pytest.mark.django_db
def test_add_admins():
    """unittest for core.add_admins
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mygroup = auth.Group.objects.create(name='first_admin')
    assert len(myuser.groups.all()) == 0
    testee.add_admins(myproject, ['0', mygroup.id])
    assert len(myuser.groups.all()) == 1
    assert myuser.groups.all()[0] == mygroup
    assert myuser.groups.all()[0].name == 'first_admin'

@pytest.mark.django_db
def test_build_pagedata_for_project(monkeypatch):
    """unittest for core.build_pagedata_for_project
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mypage = my.Page.objects.create(link='x/', order=1, title='z')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    monkeypatch.setattr(testee, 'determine_readonly', lambda *x: True)
    request = types.SimpleNamespace(user=myuser)
    data = testee.build_pagedata_for_project(request, myproject.id, 'message')
    assert (data['admin'], data['msg'], data['name']) == (False, 'message', 'first')
    assert (data['page_titel'], list(data['pages']), data['readonly']) == ('lijst', [mypage], True)
    assert (data['root'], data['title']) == (1, 'Actielijst')
    assert data['geen_items'] == ('<p>Geen acties voor de huidige selectie en '
                                  'user</p><br/><br/> \n'
                                  'Let op: aan dit project moeten eerst nog medewerkers en '
                                  'bevoegdheden voor die medewerkers worden toegevoegd')

    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    data = testee.build_pagedata_for_project(request, myproject.id, 'message')
    assert (data['admin'], data['msg'], data['name']) == (False, 'message', 'first')
    assert (data['page_titel'], list(data['pages']), data['readonly']) == ('lijst', [mypage], True)
    assert (data['root'], data['title']) == (1, 'Actielijst')
    assert data['geen_items'] == ('<p>Geen acties voor de huidige selectie en user</p>')

    myactie = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    monkeypatch.setattr(testee, 'get_acties', lambda *x: [myactie])
    data = testee.build_pagedata_for_project(request, myproject.id, 'message')
    assert (data['admin'], data['msg'], data['name']) == (False, 'message', 'first')
    assert (data['page_titel'], list(data['pages']), data['readonly']) == ('lijst', [mypage], True)
    assert (data['root'], data['title'], list(data['acties'])) == (1, 'Actielijst', [myactie])

@pytest.mark.django_db
def test_get_acties(monkeypatch, capsys):
    """unittest for core.get_acties
    """
    def mock_filter_data_on_nummer(data, y):
        """stub
        """
        # print('called testee.filter_data_on_nummer() with args', list(data), list(y))
        print(f'called testee.filter_data_on_nummer() with args {list(data)} {list(y)}')
        return data
    def mock_filter_data_on_soort(data, y):
        """stub
        """
        print('called testee.filter_data_on_soort() with args', list(data), list(y))
        return data
    def mock_filter_data_on_status(data, y):
        """stub
        """
        print('called testee.filter_data_on_status() with args', list(data), list(y))
        return data
    def mock_filter_data_on_user(data, y):
        """stub
        """
        print('called testee.filter_data_on_user() with args', list(data), list(y))
        return data
    def mock_filter_data_on_description(data, y):
        """stub
        """
        print('called testee.filter_data_on_description() with args', list(data), list(y))
        return data
    def mock_filter_data_on_arch(data, y):
        """stub
        """
        print('called testee.filter_data_on_arch() with args', list(data), list(y))
        return data
    def mock_apply_sorters(data, y):
        """stub
        """
        print('called testee.apply_sorters() with args', list(data), list(y))
        return data
    monkeypatch.setattr(testee, 'filter_data_on_nummer', mock_filter_data_on_nummer)
    monkeypatch.setattr(testee, 'filter_data_on_soort', mock_filter_data_on_soort)
    monkeypatch.setattr(testee, 'filter_data_on_status', mock_filter_data_on_status)
    monkeypatch.setattr(testee, 'filter_data_on_user', mock_filter_data_on_user)
    monkeypatch.setattr(testee, 'filter_data_on_description', mock_filter_data_on_description)
    monkeypatch.setattr(testee, 'filter_data_on_arch', mock_filter_data_on_arch)
    monkeypatch.setattr(testee, 'apply_sorters', mock_apply_sorters)
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    assert not list(testee.get_acties(myproject, myuser.id))

    myselect = my.Selection.objects.create(user=myuser.id, project=myproject)
    mysorter = my.SortOrder.objects.create(user=myuser.id, project=myproject, volgnr=0)
    myactie = my.Actie.objects.create(project=myproject, nummer='1', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)

    assert list(testee.get_acties(myproject, '')) == [myactie]
    assert list(testee.get_acties(myproject, myuser.id)) == [myactie]
    assert capsys.readouterr().out == (
            'called testee.filter_data_on_nummer() with args [<Actie: 1>] [<Selection:    >]\n'
            'called testee.filter_data_on_soort() with args [<Actie: 1>] [<Selection:    >]\n'
            'called testee.filter_data_on_status() with args [<Actie: 1>] [<Selection:    >]\n'
            'called testee.filter_data_on_user() with args [<Actie: 1>] [<Selection:    >]\n'
            'called testee.filter_data_on_description() with args [<Actie: 1>] [<Selection:    >]\n'
            'called testee.filter_data_on_arch() with args [<Actie: 1>] [<Selection:    >]\n'
            'called testee.apply_sorters() with args [<Actie: 1>] [<SortOrder: 0  >]\n')

@pytest.mark.django_db
def test_build_pagedata_for_settings():
    """unittest for core.build_pagedata_for_settings
    """
    myuser = auth.User.objects.create(username='me')
    myuser2 = auth.User.objects.create(username='another_me')
    myuser3 = auth.User.objects.create(username='also_me')
    myuser4 = auth.User.objects.create(username='anonymous')
    myproject = my.Project.objects.create(name='first')
    mypage = my.Page.objects.create(link='x/', order=1, title='z')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    myworker2 = my.Worker.objects.create(project=myproject, assigned=myuser4)
    mygroup = auth.Group.objects.create(name='first_admin')
    myuser3.groups.add(mygroup)
    request = types.SimpleNamespace(user=myuser)
    data = testee.build_pagedata_for_settings(request, myproject.id)
    assert (data['title'], data['name'], data['root']) == ('Instellingen', 'first', 1)
    assert list(data['pages']) == [mypage]
    assert list(data['soorten']) == [mysoort]
    assert list(data['stats']) == [mystatus]
    assert list(data['all_users']) == [myuser3, myuser2]
    assert list(data['proj_users']) == [myworker2, myworker]
    assert list(data['admin_users']) == [myuser4, myuser2, myuser]
    assert list(data['proj_admins']) == [myuser3]

@pytest.mark.django_db
def test_set_users():
    """unittest for core.set_users
    """
    myuser = auth.User.objects.create(username='me')
    myuser2 = auth.User.objects.create(username='another')
    myproject = my.Project.objects.create(name='first')
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    assert [x.assigned.username for x in myproject.workers.all()] == ['me']
    request = types.SimpleNamespace(user=myuser, POST={})
    testee.set_users(request, myproject.id)
    assert len(myproject.workers.all()) == 0
    request = types.SimpleNamespace(user=myuser, POST={'result': f'{myuser.id}$#${myuser2.id}'})
    testee.set_users(request, myproject.id)
    assert [x.assigned.username for x in myproject.workers.all()] == ['me', 'another']
    # nog een keer voor full branch coverage
    request = types.SimpleNamespace(user=myuser, POST={'result': f'{myuser.id}$#${myuser2.id}'})
    testee.set_users(request, myproject.id)
    assert [x.assigned.username for x in myproject.workers.all()] == ['me', 'another']

@pytest.mark.django_db
def test_set_admins():
    """unittest for core.set_users
    """
    myuser = auth.User.objects.create(username='me')
    myuser2 = auth.User.objects.create(username='another')
    myproject = my.Project.objects.create(name='first')
    mygroup = auth.Group.objects.create(name='first_admin')
    myuser2.groups.add(mygroup)
    request = types.SimpleNamespace(user=myuser, POST={})
    testee.set_admins(request, myproject.id)
    assert not list(myuser2.groups.all())

    myuser2.groups.add(mygroup)
    request = types.SimpleNamespace(user=myuser, POST={'result': f'{myuser.id}$#${myuser2.id}'})
    testee.set_admins(request, myproject.id)
    assert list(myuser.groups.all()) == [mygroup]
    assert list(myuser2.groups.all()) == [mygroup]

@pytest.mark.django_db
def test_set_tabs(monkeypatch, capsys):
    """unittest for core.set_tabs
    """
    old_save = my.Page.save
    def mock_save(*args, **kwargs):
        print('called Page.save with args', args, kwargs)
        old_save(*args, **kwargs)
    monkeypatch.setattr(my.Page, 'save', mock_save)
    myuser = auth.User.objects.create(username='me')
    my.Page.objects.create(title='Page1', order=0)
    my.Page.objects.create(title='Page2', order=1)
    assert capsys.readouterr().out == ("called Page.save with args (<Page: Page1>,)"
                                       " {'force_insert': True, 'using': 'default'}\n"
                                       "called Page.save with args (<Page: Page2>,)"
                                       " {'force_insert': True, 'using': 'default'}\n")
    request = types.SimpleNamespace(user=myuser, POST={'page1': 'Eerste', 'page2': 'Tweede'})
    testee.set_tabs(request)
    assert [x.title for x in my.Page.objects.all().order_by('order')] == ['Eerste', 'Tweede']
    assert capsys.readouterr().out == ("called Page.save with args (<Page: Eerste>,) {}\n"
                                       "called Page.save with args (<Page: Tweede>,) {}\n")
    # nog een keer voor full branch coverage
    request = types.SimpleNamespace(user=myuser, POST={'page1': 'Eerste', 'page2': 'Tweede'})
    testee.set_tabs(request)
    assert [x.title for x in my.Page.objects.all().order_by('order')] == ['Eerste', 'Tweede']
    assert capsys.readouterr().out == ""

@pytest.mark.django_db
def test_set_types():
    """unittest for core.set_types
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mysoort2 = my.Soort.objects.create(project=myproject, order=1, value='a', title='b')
    mysoort3 = my.Soort.objects.create(project=myproject, order=2, value='q', title='r')
    request = types.SimpleNamespace(user=myuser, POST={'order1': '0', 'value1': 'y', 'title1': 'z',
                                                       'order2': '1', 'value2': 'a', 'title2': 'b',
                                                       'del2': 'true',
                                                       'order3': '1', 'value3': 'v', 'title3': 'w',
                                                       'order0': '2', 'value0': 'k', 'title0': 'l',
                                                       })
    data = myproject.soort.all().order_by('order')
    assert [x.value for x in data] == ['y', 'a', 'q']
    assert [x.title for x in data] == ['z', 'b', 'r']
    testee.set_types(request, myproject.id)
    data = myproject.soort.all().order_by('order')
    assert [x.value for x in data] == ['y', 'v', 'k']
    assert [x.title for x in data] == ['z', 'w', 'l']
    myproject.soort.all().delete()
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='', title='onbekend')
    mysoort2 = my.Soort.objects.create(project=myproject, order=1, value='P', title='probleem')
    mysoort3 = my.Soort.objects.create(project=myproject, order=2, value='W', title='wens')
    mysoort3 = my.Soort.objects.create(project=myproject, order=3, value='V', title='vraag')
    mysoort3 = my.Soort.objects.create(project=myproject, order=4, value='I', title='idee')
    mysoort3 = my.Soort.objects.create(project=myproject, order=5, value='F', title='info')
    request = types.SimpleNamespace(user=myuser, POST={
        'order1': '0', 'value1': '', 'title1': 'onbekend',
        'order2': '1', 'value2': 'P', 'title2': 'probleem',
        'order3': '2', 'value3': 'W', 'title3': 'wens',
        'order4': '5', 'value4': 'V', 'title4': 'vraag',
        'order5': '3', 'value5': 'I', 'title5': 'idee',
        'order6': '4', 'value6': 'F', 'title6': 'info',
        'order0': '', 'value0': '', 'title0': '', })
    testee.set_types(request, myproject.id)
    data = myproject.soort.all().order_by('order')
    assert [x.value for x in data] == ['', 'P', 'W', 'I', 'F', 'V']
    assert [x.title for x in data] == ['onbekend', 'probleem', 'wens', 'idee', 'info', 'vraag']

@pytest.mark.django_db
def test_set_stats():
    """unittest for core.set_stats
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mysoort = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    mysoort2 = my.Status.objects.create(project=myproject, order=1, value=1, title='b')
    mysoort3 = my.Status.objects.create(project=myproject, order=2, value=2, title='r')
    request = types.SimpleNamespace(user=myuser, POST={'order1': '0', 'value1': '0', 'title1': 'z',
                                                       'order2': '1', 'value2': '1', 'title2': 'b',
                                                       'del2': 'true',
                                                       'order3': '1', 'value3': '3', 'title3': 'w',
                                                       'order0': '2', 'value0': '4', 'title0': 'l',
                                                       })
    data = myproject.status.all().order_by('order')
    assert [x.value for x in data] == [0, 1, 2]
    assert [x.title for x in data] == ['z', 'b', 'r']
    testee.set_stats(request, myproject.id)
    data = myproject.status.all().order_by('order')
    assert [x.value for x in data] == [0, 3, 4]
    assert [x.title for x in data] == ['z', 'w', 'l']
    myproject.status.all().delete()
    mysoort = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    mysoort2 = my.Status.objects.create(project=myproject, order=1, value=1, title='b')
    mysoort3 = my.Status.objects.create(project=myproject, order=2, value=2, title='r')
    request = types.SimpleNamespace(user=myuser, POST={'order1': '2', 'value1': '0', 'title1': 'z',
                                                       'order2': '0', 'value2': '1', 'title2': 'b',
                                                       'order3': '1', 'value3': '3', 'title3': 'w',
                                                       'order0': '', 'value0': '', 'title0': '',
                                                       })
    testee.set_stats(request, myproject.id)
    data = myproject.status.all().order_by('order')
    assert [x.value for x in data] == [1, 3, 0]
    assert [x.title for x in data] == ['b', 'w', 'z']
    # tbv full branch coverage
    myproject.status.all().delete()
    mysoort = my.Status.objects.create(project=myproject, order=0, value='0', title='z')
    mysoort2 = my.Status.objects.create(project=myproject, order=1, value='1', title='b')
    mysoort3 = my.Status.objects.create(project=myproject, order=2, value='2', title='r')
    request = types.SimpleNamespace(user=myuser, POST={'order1': '0', 'value1': '0', 'title1': 'z',
                                                       'order2': '1', 'value2': '1', 'title2': 'b',
                                                       'order3': '2', 'value3': '3', 'title3': 'w',
                                                       'order0': '', 'value0': '', 'title0': '',
                                                       })
    testee.set_stats(request, myproject.id)
    data = myproject.status.all().order_by('order')
    assert [x.value for x in data] == [0, 1, 3]
    assert [x.title for x in data] == ['z', 'b', 'w']

@pytest.mark.django_db
def test_build_pagedata_for_selection():
    """unittest for core.build_pagedata_for_selection
    """
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    myproject = my.Project.objects.create(name='first')
    mypage = my.Page.objects.create(link='x/', order=1, title='z')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    mysel = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='xxx',
                                        operator='', extra='', value='')
    assert testee.build_pagedata_for_selection(request, myproject.id, 'message') == (
            {}, 'Unknown search argument: xxx')
    mysel.delete()
    mysel1 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='soort',
                                         operator='', extra='', value='P')
    mysel2 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='status',
                                         operator='', extra='', value='0')
    mysel3 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='user',
                                         operator='', extra='', value='1')
    mysel3 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='arch',
                                         operator='', extra='', value='1')
    mysel4 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='nummer',
                                         operator='GT', extra='EN', value='2010')
    mysel4 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='nummer',
                                         operator='LT', extra='', value='2020')
    mysel5 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='about',
                                         operator='', extra='OR', value='xxx')
    mysel5 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='about',
                                         operator='', extra='', value='yyy')
    mysel6 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='title',
                                         operator='', extra='OR', value='aaa')
    mysel6 = my.Selection.objects.create(user=myuser.id, project=myproject, veldnm='title',
                                         operator='', extra='', value='bbb')
    data, msg = testee.build_pagedata_for_selection(request, myproject.id, 'message')
    assert (data['msg'], data['name'], list(data['pages'])) == ('message', 'first', [mypage])
    assert (data['root'], list(data['soorten']), list(data['stats'])) == (1, [mysoort], [mystatus])
    assert (data['title'], list(data['users'])) == ('Actielijst - selectie', [myuser])
    assert data['selected'] == {'about': 'yyy', 'arch': 1, 'enof1': 'en', 'enof2': 'or',
                                'gewijzigd': [], 'gt': '2010', 'lt': '2020', 'nummer': True,
                                'soort': ['P'], 'status': [0], 'title': 'bbb', 'user': [1],
                                'zoek': True}

@pytest.mark.django_db
def test_setselection(monkeypatch, capsys):
    """unittest for core.setselection
    """
    def mock_set_selection_for_nummer(*args):
        """stub
        """
        print('called testee.set_selection_for_nummer()')
    def mock_set_selection_for_soort(*args):
        """stub
        """
        print('called testee.set_selection_for_soort()')
    def mock_set_selection_for_status(*args):
        """stub
        """
        print('called testee.set_selection_for_status()')
    def mock_set_selection_for_user(*args):
        """stub
        """
        print('called testee.set_selection_for_user()')
    def mock_set_selection_for_description(*args):
        """stub
        """
        print('called testee.set_selection_for_description()')
    def mock_set_selection_for_arch(*args):
        """stub
        """
        print('called testee.set_selection_for_arch()')
    monkeypatch.setattr(testee, 'set_selection_for_nummer', mock_set_selection_for_nummer)
    monkeypatch.setattr(testee, 'set_selection_for_soort', mock_set_selection_for_soort)
    monkeypatch.setattr(testee, 'set_selection_for_status', mock_set_selection_for_status)
    monkeypatch.setattr(testee, 'set_selection_for_user', mock_set_selection_for_user)
    monkeypatch.setattr(testee, 'set_selection_for_description', mock_set_selection_for_description)
    monkeypatch.setattr(testee, 'set_selection_for_arch', mock_set_selection_for_arch)

    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    myselection = my.Selection.objects.create(user=myuser.id, project=myproject)
    postdict = QueryDict(mutable=True)
    postdict.setlist('select', [])
    request = types.SimpleNamespace(user=myuser, POST=postdict)
    testee.setselection(request, myproject.id)
    assert len(myproject.selections.filter(user=request.user.id)) == 0
    assert capsys.readouterr().out == ''
    postdict.setlist('select', ['act', 'srt', 'stat', 'user', 'txt', 'arch'])
    request = types.SimpleNamespace(user=myuser, POST=postdict)
    testee.setselection(request, myproject.id)
    assert len(myproject.selections.filter(user=request.user.id)) == 0
    assert capsys.readouterr().out == ('called testee.set_selection_for_nummer()\n'
                                       'called testee.set_selection_for_soort()\n'
                                       'called testee.set_selection_for_status()\n'
                                       'called testee.set_selection_for_user()\n'
                                       'called testee.set_selection_for_description()\n'
                                       'called testee.set_selection_for_arch()\n')

@pytest.mark.django_db
def test_set_selection_for_nummer():
    """unittest for core.set_selection_for_nummer
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    data = {'txtgt': '100', 'enof': 'en', 'txtlt': '1000'}
    testee.set_selection_for_nummer(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['GT', 'LT'])  # 2
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('nummer', 'GT',
                                                                                '', '100')
    assert (data[1].veldnm, data[1].operator, data[1].extra, data[1].value) == ('nummer', 'LT',
                                                                                'EN', '1000')
    data.delete()
    data = {'txtgt': '100', 'enof': 'of', 'txtlt': '1000'}
    testee.set_selection_for_nummer(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['GT', 'LT'])  # 2
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('nummer', 'GT',
                                                                                '', '100')
    assert (data[1].veldnm, data[1].operator, data[1].extra, data[1].value) == ('nummer', 'LT',
                                                                                'OF', '1000')
    data.delete()
    data = {'txtgt': '100', 'enof': 'en'}
    testee.set_selection_for_nummer(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['GT'])  # 1
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('nummer', 'GT',
                                                                                '', '100')
    data.delete()
    data = {'enof': 'of', 'txtlt': '1000'}
    testee.set_selection_for_nummer(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['LT'])  # 1
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('nummer', 'LT',
                                                                                '', '1000')

@pytest.mark.django_db
def test_set_selection_for_soort():
    """unittest for core.set_selection_for_soort
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    data = QueryDict(mutable=True)
    selitems = ['1', '2']
    data.setlist('srtval', selitems)
    testee.set_selection_for_soort(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(selitems)  # 2
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('soort', 'EQ',
                                                                                '', '1')
    assert (data[1].veldnm, data[1].operator, data[1].extra, data[1].value) == ('soort', 'EQ',
                                                                                'OR', '2')

@pytest.mark.django_db
def test_set_selection_for_status():
    """unittest for core.set_selection_for_status
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    data = QueryDict(mutable=True)
    selitems = ['1', '2']
    data.setlist('statval', selitems)
    testee.set_selection_for_status(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(selitems)  # 2
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('status', 'EQ',
                                                                                '', '1')
    assert (data[1].veldnm, data[1].operator, data[1].extra, data[1].value) == ('status', 'EQ',
                                                                                'OR', '2')

@pytest.mark.django_db
def test_set_selection_for_user():
    """unittest for core.set_selection_for_user
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    data = QueryDict(mutable=True)
    selitems = ['1', '2']
    data.setlist('userval', selitems)
    testee.set_selection_for_user(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(selitems)  # 2
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('user', 'EQ',
                                                                                '', '1')
    assert (data[1].veldnm, data[1].operator, data[1].extra, data[1].value) == ('user', 'EQ',
                                                                                'OR', '2')

@pytest.mark.django_db
def test_set_selection_for_description():
    """unittest for core.set_selection_for_description
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    data = {'txtabout': '100', 'enof2': 'en', 'txttitle': '1000'}
    testee.set_selection_for_description(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['about', 'title'])  # 2
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('about', 'INCL',
                                                                                '', '100')
    assert (data[1].veldnm, data[1].operator, data[1].extra, data[1].value) == ('title', 'INCL',
                                                                                'EN', '1000')
    data.delete()
    data = {'txtabout': '100', 'enof2': 'or', 'txttitle': '1000'}
    testee.set_selection_for_description(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['about', 'title'])  # 2
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('about', 'INCL',
                                                                                '', '100')
    assert (data[1].veldnm, data[1].operator, data[1].extra, data[1].value) == ('title', 'INCL',
                                                                                'OR', '1000')
    data.delete()
    data = {'txtabout': '100', 'enof2': 'en'}
    testee.set_selection_for_description(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['about']) # 1
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('about', 'INCL',
                                                                                '', '100')
    data.delete()
    data = {'enof2': 'of', 'txttitle': '1000'}
    testee.set_selection_for_description(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == len(['title'])  # 1
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('title', 'INCL',
                                                                                '', '1000')
    data.delete()

@pytest.mark.django_db
def test_set_selection_for_arch():
    """unittest for core.set_selection_for_arch
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    data = QueryDict(mutable=True)
    data.setlist('archall', ['arch'])
    testee.set_selection_for_arch(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == 1
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('arch', 'EQ',
                                                                                '', 'False')
    data = QueryDict(mutable=True)
    # data.setlist('archall', [''])
    myproject.selections.filter(user=myuser.id).delete()
    testee.set_selection_for_arch(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == 1
    assert (data[0].veldnm, data[0].operator, data[0].extra, data[0].value) == ('arch', 'EQ',
                                                                                '', 'True')
    data = QueryDict(mutable=True)
    data.setlist('archall', ['all'])
    myproject.selections.filter(user=myuser.id).delete()
    testee.set_selection_for_arch(myproject, myuser, data)
    data = myproject.selections.filter(user=myuser.id)
    assert len(data) == 0

@pytest.mark.django_db
def test_build_pagedata_for_ordering():
    """unittest for core.build_pagedata_for_ordering
    """
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    myproject = my.Project.objects.create(name='first')
    mypage = my.Page.objects.create(link='x/', order=1, title='z')
    myorder1 = my.SortOrder.objects.create(user=myuser.id, project=myproject, volgnr=0,
                                           veldnm='nummer', richting='desc')
    myorder2 = my.SortOrder.objects.create(user=myuser.id, project=myproject, volgnr=1,
                                           veldnm='gewijzigd')
    data = testee.build_pagedata_for_ordering(request, myproject.id, 'message')
    assert (data["title"], data["name"]) == ("Actielijst: volgorde", 'first')
    assert data["root"], list(data["pages"]) == (myproject.id, [mypage])
    assert data["fields"] == [("nummer", "nummer"), ("gewijzigd", "laatst gewijzigd"),
                              ("soort", "soort"), ("status", "status"),
                              ("behandelaar", "behandelaar"), ("title", "omschrijving")]
    assert data["sorters"] == [myorder1, myorder2, None, None, None, None]

@pytest.mark.django_db
def test_setordering():
    """unittest for core.setordering
    """
    myuser = auth.User.objects.create(username='me')
    request = types.SimpleNamespace(user=myuser)
    myproject = my.Project.objects.create(name='first')
    request = types.SimpleNamespace(user=myuser,
                                    POST={'field1': 'nummer', 'order1': 'asc',
                                          'field2': 'laatst gewijzigd', 'order2': 'desc',
                                          'field3': ''})
    testee.setordering(request, myproject.id)
    data = myproject.sortings.filter(user=myuser.id)
    assert len(data) == len(('field1', 'field2'))
    assert (data[0].volgnr, data[0].veldnm, data[0].richting) == (1, 'nummer', 'asc')
    assert (data[1].volgnr, data[1].veldnm, data[1].richting) == (2, 'gewijzigd', 'desc')

@pytest.mark.django_db
def test_build_pagedata_for_detail(monkeypatch):
    """unittest for core.build_pagedata_for_detail
    """
    class MockDatetime(datetime.datetime):
        """stub
        """
        @classmethod
        def now(cls, tz=None):
            """stub
            """
            return FIXDATE
    class MockRequest:
        """stub
        """
        user = types.SimpleNamespace(username='NoAuth', is_authenticated=False)
    myname = types.SimpleNamespace(username='MyName', is_authenticated=True)
    class MockRequest2:
        """stub
        """
        user = myname
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mypage = my.Page.objects.create(link='x/', order=1, title='z')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    myactie = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    monkeypatch.setattr(testee, 'get_appropriate_login_message', lambda *x: 'login_message')
    monkeypatch.setattr(testee, 'determine_readonly', lambda *x: True)
    # monkeypatch.setattr(testee.dt, 'datetime', MockDatetime)
    monkeypatch.setattr(testee.dt, 'timezone', MockDatetime)

    data = testee.build_pagedata_for_detail(MockRequest(), myproject.id, myactie.id)
    assert (data['actie'], data['msg'], data['name']) == (myactie, 'login_message', 'first')
    assert (data['page_titel'], list(data['pages'])) == ('Titel/Status', [mypage])
    assert (data['readonly'], data['root'], list(data['soorten'])) == (True, 1, [mysoort])
    assert (list(data['stats']), data['title']) == ([mystatus], 'Actie x - ')
    assert list(data['users']) == [myuser]

    data = testee.build_pagedata_for_detail(MockRequest2(), myproject.id, myactie.id)
    assert (data['actie'], data['name']) == (myactie, 'first')
    assert data['msg'] == 'login_messageKlik op een van onderstaande termen om meer te zien.'
    assert (data['page_titel'], list(data['pages'])) == ('Titel/Status', [mypage])
    assert (data['readonly'], data['root'], list(data['soorten'])) == (True, 1, [mysoort])
    assert (list(data['stats']), data['title']) == ([mystatus], 'Actie x - ')
    assert list(data['users']) == [myuser]

    data = testee.build_pagedata_for_detail(MockRequest2(), myproject.id, 'new')
    assert (data['msg'], data['name'], data['nummer']) == ('login_message', 'first', '2020-0001')
    assert (data['page_titel'], list(data['pages'])) == ('', [mypage])
    assert (data['readonly'], data['root'], list(data['soorten'])) == (True, 1, [mysoort])
    assert (list(data['stats']), data['title']) == ([mystatus], 'Nieuwe actie')
    assert (list(data['users']), data['nieuw'], data['start']) == ([myuser], myname, FIXDATE)

    myactie2 = my.Actie.objects.create(project=myproject, nummer='2020-0002', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    data = testee.build_pagedata_for_detail(MockRequest2(), myproject.id, 'new', 'a message')
    assert (data['msg'], data['name'], data['nummer']) == ('a message', 'first', '2020-0003')
    assert (data['page_titel'], list(data['pages'])) == ('', [mypage])
    assert (data['readonly'], data['root'], list(data['soorten'])) == (True, 1, [mysoort])
    assert (list(data['stats']), data['title']) == ([mystatus], 'Nieuwe actie')
    assert (list(data['users']), data['nieuw'], data['start']) == ([myuser], myname, FIXDATE)

    # t.b.v. full branch coverage: nog geen acties aanwezig bij project
    myproject = my.Project.objects.create(name='second')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    data = testee.build_pagedata_for_detail(MockRequest2(), myproject.id, 'new')
    assert (data['msg'], data['name'], data['nummer']) == ('login_message', 'second', '2020-0001')
    assert (data['page_titel'], list(data['pages'])) == ('', [mypage])
    assert (data['readonly'], data['root'], list(data['soorten'])) == (True, 2, [mysoort])
    assert (list(data['stats']), data['title']) == ([mystatus], 'Nieuwe actie')
    assert (list(data['users']), data['nieuw'], data['start']) == ([myuser], myname, FIXDATE)

@pytest.mark.django_db
def test_wijzig_detail():
    """unittest for core.wijzig_detail
    """
    myuser = auth.User.objects.create(username='me')
    myuser2 = auth.User.objects.create(username='myname')
    myproject = my.Project.objects.create(name='first')
    mypage = my.Page.objects.create(link='x/', order=1, title='z')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='old')
    mysoort2 = my.Soort.objects.create(project=myproject, order=1, value='P', title='new')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='old')
    mystatus2 = my.Status.objects.create(project=myproject, order=1, value=1, title='new')
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    myactie = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    assert not list(myactie.events.all())

    request = types.SimpleNamespace(POST={'nummer': 'x', 'about': 'a', 'title': 't', 'user': "2",
                                          'soort': 'P', 'status': '1', 'vervolg': 'xxx'},
                                    user=myuser2)
    assert testee.wijzig_detail(request, myproject, myactie.id) == ('/1/1/xxx/mld/Onderwerp, titel,'
                                                                  ' behandelaar,'
                                                                  ' categorie en status gewijzigd/')
    myactie_n = my.Actie.objects.get(pk=myactie.id)
    assert (myactie_n.about, myactie_n.title, myactie_n.behandelaar) == ('a', 't', myuser2)
    assert (myactie_n.soort, myactie_n.status, myactie_n.lasteditor) == (mysoort2, mystatus2, myuser2)
    assert not myactie_n.arch
    # assert len(list(myactie.events.all())) == len(['a', 't', 'myname', 'new', 'oms'])  # 5
    assert [x.text for x in myactie.events.all()] == ['onderwerp gewijzigd in "a"',
                                                      'titel gewijzigd in "t"',
                                                      'behandelaar gewijzigd in "myname"',
                                                      'categorie gewijzigd in "new"',
                                                      'status gewijzigd in "new"']

    request = types.SimpleNamespace(POST={'nummer': 'y', 'about': 'a', 'title': 't', 'user': "1",
                                          'soort': 'P', 'status': '1', 'archstat': 'False'},
                                    user=myuser)
    assert testee.wijzig_detail(request, myproject, 'nieuw') == '/1/2/mld/Actie opgevoerd/'
    # assert len(myproject.acties.all()) == 2
    myactie2 = myproject.acties.all()[1]
    with pytest.raises(IndexError):
        myproject.acties.all()[2]
    assert (myactie2.nummer, myactie2.starter) == ('y', myuser)
    assert (myactie2.about, myactie2.title, myactie2.behandelaar) == ('a', 't', myuser)
    assert (myactie2.soort, myactie2.status, myactie2.lasteditor) == (mysoort2, mystatus2, myuser)
    assert not myactie2.arch
    # assert len(list(myactie2.events.all())) == 3
    assert [x.text for x in myactie2.events.all()] == ['Actie opgevoerd',
                                                       'categorie gewijzigd in "new"',
                                                       'status gewijzigd in "new"']

    request = types.SimpleNamespace(POST={'nummer': 'y', 'about': 'a', 'title': 't', 'user': "1",
                                          'soort': 'P', 'status': '1', 'archstat': 'True'},
                                    user=myuser)
    assert testee.wijzig_detail(request, myproject, myactie2.id) == '/1/2/mld/Actie gearchiveerd/'
    # assert len(myproject.acties.all()) == 2
    myactie2 = myproject.acties.all()[1]
    with pytest.raises(IndexError):
        myproject.acties.all()[2]
    assert myactie2.arch
    assert [x.text for x in myactie2.events.all()] == ['Actie opgevoerd',
                                                       'categorie gewijzigd in "new"',
                                                       'status gewijzigd in "new"',
                                                       'Actie gearchiveerd']

    myactie3 = my.Actie.objects.create(project=myproject, nummer='z', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    myevent = my.Event.objects.create(actie=myactie3, starter=myuser,
                                      text=testee.UIT_DOCTOOL + ' http://doctl.org/9')
    request = types.SimpleNamespace(POST={'nummer': 'z', 'about': 'a', 'title': 't', 'user': "1",
                                          'soort': 'P', 'status': '1', 'archstat': 'True'},
                                    user=myuser)
    assert testee.wijzig_detail(request, myproject, myactie3.id) == 'http://doctl.org/9/meld/arch/1/3/'
    myactie3_n = my.Actie.objects.get(pk=myactie3.id)
    assert myactie3_n.arch
    # assert len(list(myactie3.events.all())) == 6
    with pytest.raises(IndexError):
        myactie3.events.all()[6]
    assert list(myactie3.events.all())[-1].text == 'Actie gearchiveerd'

    request = types.SimpleNamespace(POST={'nummer': 'z', 'about': 'a', 'title': 't', 'user': "1",
                                          'soort': 'P', 'status': '1', 'archstat': 'False'},
                                    user=myuser)
    assert testee.wijzig_detail(request, myproject, myactie3.id) == 'http://doctl.org/9/meld/herl/1/3/'
    myactie3_nn = my.Actie.objects.get(pk=myactie3.id)
    assert not myactie3_nn.arch
    # assert len(list(myactie3.events.all())) == 7
    with pytest.raises(IndexError):
        myactie3.events.all()[7]
    assert list(myactie3.events.all())[-1].text == 'Actie herleefd'

@pytest.mark.django_db
def test_copy_existing_action_from_here(monkeypatch, capsys):
    """unittest for core.copy_existing_action_from_here
    """
    myproject = my.Project.objects.create(name='first')
    myuser = auth.User.objects.create(username='me')
    assert testee.copy_existing_action_from_here(myproject.id, 1, myuser.username, '') == (
            f'/{myproject.id}/1/mld/'
            'Actie 1 bestaat niet bij doorkoppelen vanuit DocTool zonder terugkeeradres/')
    assert testee.copy_existing_action_from_here(myproject.id, 1, myuser.username,
                                               '/doctool/new/{}/{}') == ('/doctool/new/0/'
                                                                         'Actie 1 bestaat niet')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myactie = my.Actie.objects.create(project=myproject, nummer='1', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    assert testee.copy_existing_action_from_here(myproject.id, myactie.id, 'mwah', '') == (
            f'/{myproject.id}/{myactie.id}/mld/Aangepast vanuit DocTool zonder terugkeeradres/')
    myactie_v2 = my.Actie.objects.get(pk=myactie.id)
    assert myactie_v2.behandelaar == myuser
    assert myactie_v2.lasteditor == myuser
    newuser = auth.User.objects.create(username='mwah')
    assert testee.copy_existing_action_from_here(
            myproject.id, myactie.id, '', '/doctool/koppel/{}/{}/') == (
                    f'/doctool/koppel/{myactie.id}/{myactie.nummer}/')
    myactie_v3 = my.Actie.objects.get(pk=myactie.id)
    assert myactie_v3.behandelaar == myuser
    assert myactie_v3.lasteditor == myuser
    events = myactie_v3.events.all()
    assert len(events) == len([events[0]])
    assert (events[0].text, events[0].starter) == (f'{testee.UIT_DOCTOOL} /doctool/', myuser)
    # nu nog een dat er al wel events waren
    events[0].text = 'text1'
    events[0].save()
    myevent2 = my.Event.objects.create(actie=myactie_v3, starter=myuser, text='text2')
    events = myactie_v3.events.all()  # even controleren
    assert len(events) == len([events[0], myevent2])
    assert (events[0].text, events[1].text) == ('text1', 'text2')
    # en de test hiervoor
    assert testee.copy_existing_action_from_here(
            myproject.id, myactie.id, 'mwah', '/doctool/koppel/{}/{}/') == (
                    f'/doctool/koppel/{myactie.id}/{myactie.nummer}/')
    myactie_v4 = my.Actie.objects.get(pk=myactie.id)
    assert myactie_v4.behandelaar == myuser
    assert myactie_v4.lasteditor == newuser
    events = myactie_v4.events.all()
    assert len(events) == len([events[0], events[1]])
    assert (events[0].text, events[0].starter) == (f'text1; {testee.UIT_DOCTOOL} /doctool/', myuser)

@pytest.mark.django_db
def test_add_new_action_on_both_sides(monkeypatch, capsys):
    """unittest for core.add_new_action_on_both_sides
    """
    def mock_store(*args):
        """stub
        """
        print('called store_event with args', *args)
    monkeypatch.setattr(testee, 'store_event', mock_store)
    monkeypatch.setattr(testee.dt.timezone, 'now', lambda *x: FIXDATE)
    myproject = my.Project.objects.create(name='first')
    mysoort = my.Soort.objects.create(project=myproject, order=0, value=' ', title='onbekend')
    mysoortW = my.Soort.objects.create(project=myproject, order=1, value='W', title='wijziging')
    mysoortP = my.Soort.objects.create(project=myproject, order=2, value='P', title='probleem')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='opgevoerd')
    actie_aant = len(myproject.acties.all())
    myuser = auth.User.objects.create(username='me')
    assert testee.add_new_action_on_both_sides(myproject.id, {}, '', '') == (
            f'/{myproject.id}/1/mld/Opgevoerd vanuit DocTool zonder terugkeeradres/')
    acties = myproject.acties.all()
    actie_aant += 1
    assert len(acties) == actie_aant
    new_actie = acties[actie_aant - 1]
    assert (new_actie.nummer, new_actie.start, new_actie.starter) == ('2020-0001', FIXDATE, myuser)
    assert (new_actie.behandelaar, new_actie.about, new_actie.title) == (myuser, '', '')
    assert (new_actie.soort, new_actie.status, new_actie.lasteditor) == (mysoort, mystatus, myuser)
    assert new_actie.melding == ''
    assert capsys.readouterr().out == ('called store_event with args titel: "" 2020-0001 me\n'
                                       'called store_event with args categorie: "onbekend"'
                                       ' 2020-0001 me\n'
                                       'called store_event with args status: "opgevoerd"'
                                       ' 2020-0001 me\n')

    assert testee.add_new_action_on_both_sides(myproject.id, {'hMeld': 'request', 'hOpm': 'this'},
                                             'you', '/doctool/userwijz/koppel/{}/{}/') == (
                                                     '/doctool/userwijz/koppel/2/2020-0002/')
    acties = myproject.acties.all()
    actie_aant += 1
    assert len(acties) == actie_aant
    new_actie = acties[actie_aant - 1]
    assert (new_actie.nummer, new_actie.start, new_actie.starter) == ('2020-0002', FIXDATE, myuser)
    assert (new_actie.behandelaar, new_actie.about, new_actie.title) == (myuser, '', 'request')
    assert (new_actie.soort, new_actie.status, new_actie.lasteditor) == (mysoortW, mystatus, myuser)
    assert new_actie.melding == 'this'
    assert capsys.readouterr().out == ('called store_event with args Actie opgevoerd vanuit Doctool'
                                       ' /doctool/userwijz/ 2020-0002 me\n'
                                       'called store_event with args titel: "request" 2020-0002 me\n'
                                       'called store_event with args categorie: "wijziging"'
                                       ' 2020-0002 me\n'
                                       'called store_event with args status: "opgevoerd"'
                                       ' 2020-0002 me\n')

    myuser2 = auth.User.objects.create(username='you')
    assert testee.add_new_action_on_both_sides(myproject.id, {'hMeld': 'issue', 'hOpm': 'this'},
                                             'you', '/doctool/userprob/koppel/{}/{}/') == (
                                                     '/doctool/userprob/koppel/3/2020-0003/')
    acties = myproject.acties.all()
    actie_aant += 1
    assert len(acties) == actie_aant
    new_actie = acties[actie_aant - 1]
    assert (new_actie.nummer, new_actie.start, new_actie.starter) == ('2020-0003', FIXDATE, myuser)
    assert (new_actie.behandelaar, new_actie.about, new_actie.title) == (myuser2, '', 'issue')
    assert (new_actie.soort, new_actie.status, new_actie.lasteditor) == (mysoortP, mystatus, myuser2)
    assert new_actie.melding == 'this'
    assert capsys.readouterr().out == ('called store_event with args Actie opgevoerd vanuit Doctool'
                                       ' /doctool/userprob/ 2020-0003 me\n'
                                       'called store_event with args titel: "issue" 2020-0003 me\n'
                                       'called store_event with args categorie: "probleem"'
                                       ' 2020-0003 me\n'
                                       'called store_event with args status: "opgevoerd"'
                                       ' 2020-0003 me\n')

    assert testee.add_new_action_on_both_sides(myproject.id, {'hMeld': 'found some', 'hOpm': 'this'},
                                             'you', '/doctool/bevinding/koppel/{}/{}/') == (
                                                     '/doctool/bevinding/koppel/4/2020-0004/')
    acties = myproject.acties.all()
    actie_aant += 1
    assert len(acties) == actie_aant
    new_actie = acties[actie_aant - 1]
    assert (new_actie.nummer, new_actie.start, new_actie.starter) == ('2020-0004', FIXDATE, myuser)
    assert (new_actie.behandelaar, new_actie.about, new_actie.title) == (myuser2, 'testbevinding',
                                                                         'found some')
    assert (new_actie.soort, new_actie.status, new_actie.lasteditor) == (mysoort, mystatus, myuser2)
    assert new_actie.melding == 'this'
    assert capsys.readouterr().out == ('called store_event with args Actie opgevoerd vanuit Doctool'
                                       ' /doctool/bevinding/ 2020-0004 me\n'
                                       'called store_event with args titel: "found some"'
                                       ' 2020-0004 me\n'
                                       'called store_event with args categorie: "onbekend"'
                                       ' 2020-0004 me\n'
                                       'called store_event with args status: "opgevoerd"'
                                       ' 2020-0004 me\n')

def test_build_full_message():
    """unittest for core.build_full_message
    """
    assert testee.build_full_message([], 'melding') == 'melding'
    assert testee.build_full_message(['hallo'], 'melding') == 'melding'
    assert testee.build_full_message(['hallo'], '') == 'Hallo gewijzigd'
    assert testee.build_full_message(['hallo', 'goodbye', 'welkom'], 'melding') == 'melding'
    assert testee.build_full_message(['hallo', 'goodbye', 'welkom'], '') == (
            'Hallo, goodbye en welkom gewijzigd')

@pytest.mark.django_db
def test_build_pagedata_for_tekstpage(monkeypatch, capsys):
    """unittest for core.build_pagedata_for_tekstpage
    """
    class MockRequest:
        """stub
        """
        user = types.SimpleNamespace(username='NoAuth', is_authenticated=False)
    myname = types.SimpleNamespace(username='MyName', is_authenticated=True)
    class MockRequest2:
        """stub
        """
        user = myname
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mypages = [my.Page.objects.create(link='meld', order=0, title='melding'),
               my.Page.objects.create(link='oorz', order=1, title='oorzaak'),
               my.Page.objects.create(link='opl', order=2, title='oplossing'),
               my.Page.objects.create(link='verv', order=3, title='vervolg'),
               my.Page.objects.create(link='voortg', order=4, title='voortgang')]
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myactie = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser,
                                      melding='dit', oorzaak='dat', oplossing='iets',
                                      vervolg='en verder...')
    monkeypatch.setattr(testee, 'get_appropriate_login_message', lambda *x: 'login_message')
    monkeypatch.setattr(testee, 'determine_readonly', lambda *x: True)
    # with pytest.raises(django.http.response.Http404) as exc:
    with pytest.raises(testee.Http404) as exc:
        data = testee.build_pagedata_for_tekstpage(MockRequest(), myproject.id, myactie.id + 1)
        assert str(exc.value) == 'No Actie matches the given query'
    # with pytest.raises(django.http.response.Http404) as exc:
    with pytest.raises(testee.Http404) as exc:
        data = testee.build_pagedata_for_tekstpage(MockRequest(), myproject.id, myactie.id)
        assert str(exc.value) == 'No Page matches the given query'
    data = testee.build_pagedata_for_tekstpage(MockRequest(), myproject.id, myactie.id, 'meld')
    assert (data['msg'], data['root'], data['name']) == ('login_message', myproject.id, 'first')
    assert (list(data['pages']), data['readonly'], data['page']) == (mypages, True, 'meld')
    assert (data['next'], data['title'], data['page_titel']) == ('oorz', 'Actie x - ', 'melding')
    assert (data['page_text'], data['actie']) == ('dit', myactie)
    data = testee.build_pagedata_for_tekstpage(MockRequest(), myproject.id, myactie.id, 'oorz')
    assert (data['msg'], data['root'], data['name']) == ('login_message', myproject.id, 'first')
    assert (list(data['pages']), data['readonly'], data['page']) == (mypages, True, 'oorz')
    assert (data['next'], data['title'], data['page_titel']) == ('opl', 'Actie x - ', 'oorzaak')
    assert (data['page_text'], data['actie']) == ('dat', myactie)
    data = testee.build_pagedata_for_tekstpage(MockRequest(), myproject.id, myactie.id, 'opl', 'x')
    assert (data['msg'], data['root'], data['name']) == ('x', myproject.id, 'first')
    assert (list(data['pages']), data['readonly'], data['page']) == (mypages, True, 'opl')
    assert (data['next'], data['title'], data['page_titel']) == ('verv', 'Actie x - ', 'oplossing')
    assert (data['page_text'], data['actie']) == ('iets', myactie)
    data = testee.build_pagedata_for_tekstpage(MockRequest(), myproject.id, myactie.id, 'verv')
    assert (data['msg'], data['root'], data['name']) == ('login_message', myproject.id, 'first')
    assert (list(data['pages']), data['readonly'], data['page']) == (mypages, True, 'verv')
    assert (data['next'], data['title'], data['page_titel']) == ('voortg', 'Actie x - ', 'vervolg')
    assert (data['page_text'], data['actie']) == ('en verder...', myactie)

@pytest.mark.django_db
def test_wijzig_tekstpage(monkeypatch):
    """unittest for core.wijzig_tekstpage
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mypages = [my.Page.objects.create(link='meld', order=0, title='melding'),
               my.Page.objects.create(link='oorz', order=1, title='oorzaak'),
               my.Page.objects.create(link='opl', order=2, title='oplossing'),
               my.Page.objects.create(link='verv', order=3, title='vervolg'),
               my.Page.objects.create(link='voortg', order=4, title='voortgang')]
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myactie = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser,
                                      melding='dit', oorzaak='dat', oplossing='iets',
                                      vervolg='en verder...')
    assert not list(myactie.events.all())

    # eerst zonder dat user aan het project zit
    request = types.SimpleNamespace(POST={'data': 'pagina tekst'}, user=myuser)
    monkeypatch.setattr(testee, 'no_authorization_message', lambda x, y: f'{x} ({y})')
    result = testee.wijzig_tekstpage(request, myproject.id, myactie.id)
    assert result == 'acties te wijzigen (1)'

    # user aan het project koppelen, maar nog geen page meegeven
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    with pytest.raises(ValueError) as exc:
        assert testee.wijzig_tekstpage(request, myproject.id, myactie.id) == ''
        assert str(exc.value) == 'missing/wrong page'

    assert not list(myactie.events.all())
    assert testee.wijzig_tekstpage(request, myproject.id, myactie.id, 'meld') == (
            '/1/1/meld/meld/Meldingtekst aangepast')
    myactie_n = my.Actie.objects.get(pk=myactie.id)
    assert (myactie_n.melding, myactie_n.lasteditor) == ('pagina tekst', myuser)
    eventcount = 1
    assert len(list(myactie.events.all())) == eventcount
    assert list(myactie.events.all())[-1].text == 'Meldingtekst aangepast'

    assert testee.wijzig_tekstpage(request, myproject.id, myactie.id, 'oorz') == (
            '/1/1/oorz/meld/Beschrijving oorzaak aangepast')
    myactie_n2 = my.Actie.objects.get(pk=myactie.id)
    assert (myactie_n2.oorzaak, myactie_n2.lasteditor) == ('pagina tekst', myuser)
    eventcount += 1
    assert len(list(myactie.events.all())) == eventcount  # 2
    assert list(myactie.events.all())[-1].text == 'Beschrijving oorzaak aangepast'

    assert testee.wijzig_tekstpage(request, myproject.id, myactie.id, 'opl') == (
            '/1/1/opl/meld/Beschrijving oplossing aangepast')
    myactie_n3 = my.Actie.objects.get(pk=myactie.id)
    assert (myactie_n3.oplossing, myactie_n3.lasteditor) == ('pagina tekst', myuser)
    eventcount += 1
    assert len(list(myactie.events.all())) == eventcount  # 3
    assert list(myactie.events.all())[-1].text == 'Beschrijving oplossing aangepast'

    myuser2 = auth.User.objects.create(username='also me')
    myworker2 = my.Worker.objects.create(project=myproject, assigned=myuser2)
    request = types.SimpleNamespace(POST={'data': 'pagina tekst', 'vervolg': 'xxx'},
                                    user=myuser2)
    assert testee.wijzig_tekstpage(request, myproject.id, myactie.id, 'verv') == (
            '/1/1/xxx/meld/Beschrijving vervolgactie aangepast')
    myactie_n4 = my.Actie.objects.get(pk=myactie.id)
    assert (myactie_n4.vervolg, myactie_n4.lasteditor) == ('pagina tekst', myuser2)
    eventcount += 1
    assert len(list(myactie.events.all())) == eventcount  # 4
    assert list(myactie.events.all())[-1].text == 'Beschrijving vervolgactie aangepast'

@pytest.mark.django_db
def test_build_pagedata_for_events(monkeypatch):
    """unittest for core.build_pagedata_for_events
    """
    class MockDatetime(datetime.datetime):
        """stub
        """
        @classmethod
        def now(cls, tz=None):
            """stub
            """
            return FIXDATE
    myname = types.SimpleNamespace(username='MyName', is_authenticated=True)
    class MockRequest:
        """stub
        """
        user = myname
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mypages = [my.Page.objects.create(link='meld', order=0, title='melding'),
               my.Page.objects.create(link='oorz', order=1, title='oorzaak'),
               my.Page.objects.create(link='opl', order=2, title='oplossing'),
               my.Page.objects.create(link='verv', order=3, title='vervolg'),
               my.Page.objects.create(link='voortg', order=4, title='voortgang')]
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myactie = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                      lasteditor=myuser,
                                      soort=mysoort, status=mystatus, behandelaar=myuser)
    myevent1 = my.Event.objects.create(actie=myactie, starter=myuser, text='text1')
    myevent2 = my.Event.objects.create(actie=myactie, starter=myuser, text='text2')
    myevent3 = my.Event.objects.create(actie=myactie, starter=myuser, text='text3')
    myevents = [myevent3, myevent2, myevent1]
    monkeypatch.setattr(testee, 'get_appropriate_login_message', lambda *x: 'login_message')
    monkeypatch.setattr(testee, 'determine_readonly', lambda *x: True)
    monkeypatch.setattr(testee.dt, 'timezone', MockDatetime)
    data = testee.build_pagedata_for_events(MockRequest(), myproject.id, myactie.id, msg='xx')
    assert (data['title'], data['page_titel'], data['name']) == ('x - ', 'Voortgang', 'first')
    assert (data['root'], data['msg']) == (myproject.id, 'xx Klik op een '
                                           'voortgangsregel om de tekst nader te bekijken.')
    assert (list(data['pages']), data['actie']) == (mypages, myactie)
    assert (list(data['events']), data['user'], data['readonly']) == (myevents, myname, True)

    data = testee.build_pagedata_for_events(MockRequest(), myproject.id, myactie.id, myevent2.id)
    assert (data['title'], data['page_titel'], data['name']) == ('x - ', 'Voortgang', 'first')
    assert (data['root'], data['msg']) == (myproject.id, 'login_message Klik op een '
                                           'voortgangsregel om de tekst nader te bekijken.')
    assert (list(data['pages']), data['actie']) == (mypages, myactie)
    assert (list(data['events']), data['user'], data['readonly']) == (myevents, myname, True)
    assert data['curr_ev'] == myevent2

    data = testee.build_pagedata_for_events(MockRequest(), myproject.id, myactie.id, 'nieuw')
    assert (data['title'], data['page_titel'], data['name']) == ('x - ', 'Voortgang', 'first')
    assert (data['root'], data['msg']) == (myproject.id, 'login_message Klik op een '
                                           'voortgangsregel om de tekst nader te bekijken.')
    assert (list(data['pages']), data['actie']) == (mypages, myactie)
    assert (list(data['events']), data['user'], data['readonly']) == (myevents, myname, True)
    assert (data['nieuw'], data['curr_ev']) == (True, {'id': 'nieuw', 'start': FIXDATE})

@pytest.mark.django_db
def test_wijzig_events(monkeypatch):
    """unittest for core.wijzig_events
    """
    myuser = auth.User.objects.create(username='me')
    myproject = my.Project.objects.create(name='first')
    mypages = [my.Page.objects.create(link='meld', order=0, title='melding'),
               my.Page.objects.create(link='oorz', order=1, title='oorzaak'),
               my.Page.objects.create(link='opl', order=2, title='oplossing'),
               my.Page.objects.create(link='verv', order=3, title='vervolg'),
               my.Page.objects.create(link='voortg', order=4, title='voortgang')]
    mysoort = my.Soort.objects.create(project=myproject, order=0, value='y', title='z')
    mystatus = my.Status.objects.create(project=myproject, order=0, value=0, title='z')
    myactie = my.Actie.objects.create(project=myproject, nummer='x', starter=myuser,
                                             lasteditor=myuser,
                                             soort=mysoort, status=mystatus, behandelaar=myuser,
                                             melding='dit', oorzaak='dat', oplossing='iets',
                                             vervolg='en verder...')
    assert not list(myactie.events.all())

    # eerst zonder dat user aan het project zit
    request = types.SimpleNamespace(POST={'data': 'pagina tekst'}, user=myuser)
    monkeypatch.setattr(testee, 'no_authorization_message', lambda x, y: f'{x} ({y})')
    result = testee.wijzig_events(request, myproject.id, myactie.id)
    assert result == 'acties te wijzigen (1)'

    # user aan het project koppelen en verder testen
    myworker = my.Worker.objects.create(project=myproject, assigned=myuser)
    with pytest.raises(testee.ObjectDoesNotExist):
        result = testee.wijzig_events(request, myproject.id + 1)
    with pytest.raises(testee.Http404):
        result = testee.wijzig_events(request, myproject.id, myactie.id + 1)
    with pytest.raises(testee.Http404):
        result = testee.wijzig_events(request, myproject.id, myactie.id, 1)
    with pytest.raises(testee.Http404):
        assert testee.wijzig_events(request, myproject.id, myactie.id, '')
    assert testee.wijzig_events(request, myproject.id, myactie.id, 'nieuw') == (
            f'/{myproject.id}/{myactie.id}/voortg/meld/De gebeurtenis is toegevoegd./')
    myevent = list(myactie.events.all())[0]
    assert testee.wijzig_events(request, myproject.id, myactie.id, myevent.id) == (
            f'/{myproject.id}/{myactie.id}/voortg/meld/De gebeurtenis is bijgewerkt./')
