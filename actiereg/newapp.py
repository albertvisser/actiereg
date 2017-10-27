"""doel: opvoeren van een nieuw project in de "probleemregistratie"

gebruik: python newapp.py <name> [copy|activate|loaddata|undo] [xml-file]

zonder tweede argument maakt dit een platte kopie van de basisapplicatie
    (m.a.w. de opties copy + activate uit het onderstaande)

met een * als eerste argument voert dit het bovengenoemde uit voor alle
    nog niet geactiveerde applicaties in apps.dat

om een aangepaste kopie te maken kun je als tweede argument opgeven:
'copy':     kopieer programmatuur en templates (om aan te passen voorafgaand
            aan "activate")
'activate': tabellen toevoegen aan de database en de applicatie gereed melden
            zodat deze op het startscherm verschijnt
'loaddata': tabellen (settings en data) initieel vullen vanuit opgegeven
            xml-file (niet meer mogelijk na activeren)
'undo':     als er iets niet naar wens kun je een en ander ongedaan maken
            door dit als tweede argument op te geven

"""
import os
import sys
import pathlib
import subprocess
import shutil
BASE = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(BASE.parent))
APPS = BASE / "apps.dat"
USAGE = __doc__
ROOT_FILES = ('__init__.py', 'models.py', 'views.py', 'urls.py', 'admin.py',
              'initial_data.json')
TEMPLATE_FILES = ('index', 'actie', 'tekst', 'voortgang', 'select', 'order',
                  'settings')


def copyover(root, name, appname):
    """copy components for project

    arguments: project name, file name, apps file as a Path object
    """
    copyfrom = BASE / "_basic" / name
    copyto = BASE / root / name
    with copyfrom.open() as oldfile:
        with copyto.open("w") as newfile:
            for line in oldfile:
                if "basic" in line:
                    if name == "models.py":
                        line = line.replace("basic", root)
                    else:
                        line = line.replace("_basic", root)
                if line == 'ROOT = "basic"\n':
                    newfile.write('ROOT = "{}"\n'.format(root))
                elif line == 'NAME = "demo"\n':
                    newfile.write('NAME = "{}"\n'.format(str(appname)))
                else:
                    newfile.write(line)


def backup(fn):
    """remove current file as it is to be (re)written, saving a backup if necessary

    input is a Path object
    return file and backup as Path objects
    """
    new = pathlib.Path(str(fn) + "~")
    fn.replace(new)
    return new, fn


class NewProj:
    """applicatiefiles kopieren en aanpassen
    """
    def __init__(self, *args):
        """args: project name, action to be taken,
        name of data file (only for loaddata)
        """
        self.root = self.action = self.load_from = ''
        self.actiondict = {'copy': self.do_copy,
                           'activate': self.activate,
                           'undo': self.undo,
                           'all': self.do_all}
        if args:
            self.msg = self.parse_args(*args)

    def do_stuff(self):
        if self.msg:
            print(self.msg)
            return
        print('performing actions for project "{}":'.format(self.root))
        self.actiondict[self.action]()
        print("ready.")
        if self.action in ("activate", "all", "undo"):
            print("\nRestart the server to see the changes.")

    def parse_args(self, *args):
        self.root = args[0]
        self.action = args[1] if len(args) > 1 else "all"
        if self.action == "loaddata":
            if len(args) != 3:
                return "foute argumenten voor loaddata*"
            else:
                self.load_from = args[2]
        elif self.action not in ("copy", "activate", "undo", "all"):
            return "foutief tweede argument (actie)*"
        elif len(args) > 2:
            return "teveel argumenten*"
        found = False
        msg = ""
        with APPS.open() as oldfile:
            for line in oldfile:
                if 'X;{};'.format(self.root) in line:
                    found = True
                    if self.action not in ("loaddata", "undo"):
                        return "dit project is al geactiveerd"
                if "_;{};".format(self.root) in line:
                    found = True
                    if self.action == "undo":
                        return "dit project is nog niet geactiveerd"
                if found:
                    break
        if not found:
            return "project niet gevonden"
        ok, rt, self.app, oms = line.strip().split(";")
        ## if rt != self.root:  # ? kan helemaal niet
            ## return "leek goed, maar toch klopt de projectnaam niet"

    def __str__(self):
        name = str(self.__class__).split()[1][1:-2]
        return "{}('{}', '{}', '{}')".format(
            name, self.root, self.action, self.load_from)

    def do_copy(self):
        print("creating and populating app root...")
        (BASE / self.root).mkdir()
        ## newfile = open(os.sep.join((BASE,root,"__init__.py")),"w")
        ## newfile.close()
        for name in ROOT_FILES:
            copyover(self.root, name, self.app)
        if self.root != "actiereg":                     # why?
            print("creating templates...")
            newdir = BASE / "templates" / self.root
            newdir.mkdir()
            for name in TEMPLATE_FILES:
                fname = newdir / "{}.html".format(name)
                fname.write_text('{{% extends "basic/{}.html" %}}\n'.format(name))

    def activate(self):
        self.update_settings()
        self.update_urlconf()
        # database aanpassen en initiele settings data opvoeren
        sys.path.append(BASE)
        os.environ["DJANGO_SETTINGS_MODULE"] = 'actiereg.settings'
        import settings
        from django.contrib.auth.models import Group, Permission
        print("modifying database...")
        self.call_manage(["syncdb"])
        print("loading inital data...")
        self.call_manage(['loaddata', '{}/initial_data.json'.format(self.root)])
        print("setting up authorisation groups...")
        group = Group.objects.create(name='{}_admin'.format(self.root))
        for permit in Permission.objects.filter(
                content_type__app_label="{}".format(self.root)):
            group.permissions.add(permit)
        group = Group.objects.create(name='{}_user'.format(self.root))
        for permit in Permission.objects.filter(
                content_type__app_label="{}".format(self.root)).filter(
                content_type__model__in=['actie', 'event', 'sortorder',
                                         'selection']):
            group.permissions.add(permit)
        self.update_appreg()

    def call_manage(self, command):
        subprocess.run(["python", "manage.py"] + command)

    def loaddata(self):
        print("getting probreg data")
        with open("loaddata.py") as oldfile:
            with open("load_data.py", "w") as newfile:
                for line in oldfile:
                    newfile.write(line.replace("_basic", self.root))
        import load_data as ld
        print("loading settings...", end=', ')
        ld.loadsett(load_from)
        print("ready.")
        print("loading data...", end=', ')
        ld.loaddata(load_from, root)

    def do_all(self):
        self.do_copy()
        self.activate()
        self.loaddata()

    def undo(self):
        print("removing app root...")
        shutil.rmtree(str(BASE / root))
        if root != "actiereg":
            print("removing templates...")
            shutil.rmtree(str(BASE / "templates" / root))
        self.update_settings()
        self.update_urlconf()
        self.update_appreg()

    def update_settings(self):
        # toevoegen aan settings.py (INSTALLED_APPS)
        print("updating settings...")
        old, new = backup(BASE / "settings.py")
        schrijf = False
        with old.open() as oldfile:
            with new.open("w") as newfile:
                new_line = "    'actiereg.{}',\n".format(self.root)
                for line in oldfile:
                    if line.strip() == "INSTALLED_APPS = (":
                        schrijf = True
                    if schrijf and line.strip() == ")" and self.action != "undo":
                        newfile.write(new_line)
                        schrijf = False
                    if line == new_line and self.action == "undo":
                        schrijf = False
                    else:
                        newfile.write(line)

    def update_urlconf(self):
        # toevoegen aan urls.py (urlpatterns)
        print("updating urlconfs...")
        old, new = backup(BASE / "urls.py")
        schrijf = False
        with old.open() as oldfile:
            with new.open("w") as newfile:
                new_line = "    url(r'^{0}/', include('actiereg.{0}.urls')),\n".format(
                    self.root)
                for line in oldfile:
                    if line.strip().startswith('urlpatterns'):
                        schrijf = True
                    if schrijf and line.strip() == "" and self.action != "undo":
                        newfile.write(new_line)
                        schrijf = False
                    if line == new_line and self.action == "undo":
                        schrijf = False
                    else:
                        newfile.write(line)

    def update_appreg(self):
        print("updating apps registration...")
        old, new = backup(APPS)
        with old.open() as _in:
            with new.open("w") as _out:
                for app in _in:
                    ok, test_root, test_name, desc = app.split(";")
                    if test_root == self.root:
                        if self.action == "undo":
                            _out.write(app.replace("X;", "_;"))
                        else:
                            _out.write(app.replace("_;", "X;"))
                    else:
                        _out.write(app)

def allnew():
    """create all new projects
    """
    ret = ''
    with open(APPS) as oldfile:
        newapps = [line.split(";")[1] for line in oldfile if line.startswith('_')]
    for app in newapps:
        ret = NewProj(app)
        if ret:
            ret = ':'.join((app, ret))
            break
    return ret

if __name__ == "__main__":
    if len(sys.argv) == 1:
        ret = 'insufficient arguments*'
    elif sys.argv[1] == "*":
        ret = allnew()
    else:
        ret = NewProj(*sys.argv[1:])
    if ret:
        if ret.endswith('*'):
            ret = '\n]n'.join((ret[:-1], USAGE))
        print(ret)
