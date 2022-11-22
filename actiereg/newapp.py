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
from django.contrib.auth.models import Group, Permission
BASE = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(BASE.parent))
APPS = BASE / "apps.dat"
USAGE = __doc__
ROOT_FILES = ('__init__.py', 'models.py', 'views.py', 'urls.py', 'admin.py',
              'initial_data.json')
SYMLINK = (ROOT_FILES[1], ROOT_FILES[3])
TEMPLATE_FILES = ('index', 'actie', 'tekst', 'voortgang', 'select', 'order',
                  'settings')


class NewProj:
    """applicatiefiles kopieren en aanpassen
    """
    def __init__(self, *args):
        self.root = self.action = self.load_from = ''
        self.actiondict = {'copy': self.do_copy,
                           'activate': self.activate,
                           'undo': self.undo,
                           'all': self.do_all}
        if args:
            self.msg = self.parse_args(*args)

    def __str__(self):
        name = str(self.__class__).split()[1][1:-2]
        return f"{name}('{self.root}', '{self.action}', '{self.load_from}')"

    def do_stuff(self):
        """perform actions
        """
        if self.msg:
            print(self.msg)
            return
        print('performing actions for project "{self.root}":')
        self.actiondict[self.action]()
        print("ready.")
        if self.action in ("activate", "all", "undo"):
            print("\nRestart the server to see the changes.")

    def parse_args(self, *args):
        """parse arguments: project name, action to be taken, name of data file
        (only for loaddata)
        """
        self.root = args[0]
        self.action = args[1] if len(args) > 1 else "all"
        if self.action == "loaddata":
            if len(args) != 3:
                return "foute argumenten voor loaddata*"
            self.load_from = args[2]
        elif self.action not in ("copy", "activate", "undo", "all"):
            return "foutief tweede argument (actie)*"
        elif len(args) > 2:
            return "teveel argumenten*"
        found = False
        with APPS.open() as oldfile:
            for line in oldfile:
                if 'X;{self.root};' in line:
                    found = True
                    if self.action not in ("loaddata", "undo"):
                        return "dit project is al geactiveerd"
                if "_;{self.root};" in line:
                    found = True
                    if self.action == "undo":
                        return "dit project is nog niet geactiveerd"
                if found:
                    break
            else:  # if not found:
                return "project niet gevonden"
        # ok, rt, self.app, oms = line.strip().split(";")
        self.app = line.strip().split(';')[2]

    def do_all(self):
        """perform all-in-one
        """
        self.do_copy()
        self.activate()
        if self.load_from:
            self.loaddata()

    def do_copy(self):
        """copy programs and templates
        """
        print("creating and populating app root...")
        (BASE / self.root).mkdir()
        for name in ROOT_FILES:
            self.copyover(name)
        if self.root != "actiereg":                     # why?
            print("creating templates...")
            newdir = BASE / "templates" / self.root
            newdir.mkdir()
            for name in TEMPLATE_FILES:
                fname = newdir / "{name}.html"
                fname.write_text('{{% extends "basic/{name}.html" %}}\n')

    def activate(self):
        """database aanpassen en initiele settings data opvoeren
        """
        self.update_settings()
        # self.update_urlconf()
        sys.path.append(BASE)
        os.environ["DJANGO_SETTINGS_MODULE"] = 'actiereg.settings'
        ## import settings
        print("modifying database...")
        self.call_manage(["syncdb"])
        print("loading inital data...")
        self.call_manage(['loaddata', f'{self.root}/initial_data.json'])
        print("setting up authorisation groups...")
        group = Group.objects.create(name=f'{self.root}_admin')
        for permit in Permission.objects.filter(
                content_type__app_label=f"{self.root}"):
            group.permissions.add(permit)
        group = Group.objects.create(name=f'{self.root}_user')
        for permit in Permission.objects.filter(
                content_type__app_label=f"{self.root}").filter(
                    content_type__model__in=['actie', 'event', 'sortorder', 'selection']):
            group.permissions.add(permit)
        self.update_appreg()

    def loaddata(self):
        """load data from probreg (if present)
        """
        print("getting probreg data")
        with open("loaddata.py") as oldfile:
            with open("load_data.py", "w") as newfile:
                for line in oldfile:
                    newfile.write(line.replace("_basic", self.root))
        import loaddata as ld
        print("loading settings...", end=', ')
        ld.loadsett(self.load_from)
        print("ready.")
        print("loading data...", end=', ')
        ld.loaddata(self.load_from, self.root)

    def undo(self):
        """reverse updates
        """
        print("removing app root...")
        shutil.rmtree(str(BASE / self.root))
        if self.root != "actiereg":
            print("removing templates...")
            shutil.rmtree(str(BASE / "templates" / self.root))
        self.update_settings()
        # self.update_urlconf()
        self.update_appreg()

    def update_settings(self):
        """toevoegen aan settings.py (INSTALLED_APPS)
        """
        print("updating settings...")
        old, new = self.backup(BASE / "settings.py")
        schrijf = False
        with old.open() as oldfile:
            with new.open("w") as newfile:
                new_line = f"    'actiereg.{self.root}',\n"
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
        """toevoegen aan urls.py (urlpatterns)
        """
        print("updating urlconfs...")
        old, new = self.backup(BASE / "urls.py")
        schrijf = False
        with old.open() as oldfile:
            with new.open("w") as newfile:
                new_line = "    url(r'^{self.root}/', include('actiereg.{self.root}.urls')),\n"
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
        """update apps registration
        """
        print("updating apps registration...")
        old, new = self.backup(APPS)
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

    def copyover(self, name):
        """copy components for project

        arguments: project name, file name, apps file as a Path object
        """
        copyfrom = BASE / "_basic" / name
        copyto = BASE / self.root / name
        if name in SYMLINK:  # make symlink instead of real copy
            copyto.symlink_to(copyfrom)
            return
        with copyfrom.open() as oldfile:
            with copyto.open("w") as newfile:
                for line in oldfile:
                    if "basic" in line:
                        line = line.replace("_basic", self.root)
                    if line == 'ROOT = "basic"\n':
                        newfile.write(f'ROOT = "{self.root}"\n')
                    elif line == 'NAME = "demo"\n':
                        newfile.write(f'NAME = "{self.app}"\n')
                    else:
                        newfile.write(line)

    @staticmethod
    def backup(fn):
        """remove current file as it is to be (re)written, saving a backup if necessary

        input is a Path object
        return file and backup as Path objects
        """
        new = pathlib.Path(str(fn) + "~")
        fn.replace(new)
        return new, fn

    @staticmethod
    def call_manage(command):
        """call django command manager
        """
        subprocess.run(["python", "manage.py"] + command)


def allnew():
    """create all new projects
    """
    ret = ''
    with open(APPS) as oldfile:
        newapps = [line.split(";")[1] for line in oldfile if line.startswith('_')]
    for app in newapps:
        build = NewProj(app, 'all')
        if build.msg:
            result = ': '.join((app, build.msg))
            break
        build.do_stuff()
    return result


if __name__ == "__main__":
    if len(sys.argv) == 1:
        result = 'insufficient arguments*'
    elif sys.argv[1] == "*":
        result = allnew()
    else:
        result = NewProj(*sys.argv[1:])
    if result:
        if result.endswith('*'):
            result = '\n]n'.join((result[:-1], USAGE))
        print(result)
