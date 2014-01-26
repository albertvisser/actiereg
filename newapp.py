"""doel: opvoeren van een nieuw project in de "probleemregistratie"

gebruik: python newapp.py <name> [copy|activate|loaddata|undo] [xml-file]

zonder tweede argument maakt dit een platte kopie van de basisapplicatie
    (m.a.w. de opties copy + activate uit het onderstaande)

om een aangepaste kopie te maken kun je als tweede argument opgeven:
'copy':     kopieer programmatuur en templates (om aan te passen voorafgaand
            aan "activate")
'activate': tabellen toevoegen aan de database en de applicatie gereed melden
            zodat deze op het startscherm verschijnt
'loaddata': tabellen (settings en data) initieel vullen vanuit opgegeven
            xml-file
'undo':     als er iets niet naar wens gaat kun je een en ander ongedaan maken
            door dit als tweede argument op te geven

"""

import os
import sys
import shutil
sys.path.append("/home/visser/django")

basepath = "/home/visser/django/probreg"
appsfile = os.path.join(basepath,"apps.dat")
USAGE = __doc__

def copyover(root,name,appname):
    name = name if "." in name else name + ".py"
    copyfrom = os.path.join(basepath,"_basic")
    copyto = os.path.join(basepath,root)
    with open(os.path.join(copyfrom,name)) as oldfile:
        with open(os.path.join(copyto,name),"w") as newfile:
            for line in oldfile:
                newfile.write(line.replace("_basic",root).replace('"basic"','"{0}"'.format(root)).replace('"demo"','"{0}"'.format(appname)))

def backup(fn):
    if os.path.split(fn)[0] == "":
        fn = os.path.join(basepath,fn)
    new = fn + "~"
    os.rename(fn,new)
    return new,fn

def newproj(*args):
    "applicatiefiles kopieren en aanpassen"
    root = args[0]
    action = args[1] if len(args) > 1 else "all"
    if action == "loaddata":
        if len(args) != 3:
            return "foute argumenten voor loaddata\n\n" + USAGE
        else:
            load_from = args[2]
    elif action not in ("copy", "activate", "undo", "all"):
        return "foutief tweede argument\n\n" + USAGE
    elif len(args) > 2:
        return "teveel argumenten\n\n" + USAGE
    found = False
    msg = ""
    with open(appsfile) as oldfile:
        for line in oldfile:
            if 'X;{0};'.format(root) in line:
                found =  True
                if action not in ("loaddata", "undo"):
                    return "dit project is al geactiveerd"
            if "_;{0};".format(root) in line:
                found =  True
                if action == "undo":
                    return "dit project is nog niet geactiveerd"
            if found:
                break
    if not found:
        return "project niet gevonden"
    ok, rt, app, oms = line.strip().split(";")
    if rt != root:
        return "leek goed, maar toch klopt de projectnaam niet"

    if action == "undo":
        print("removing app root...")
        shutil.rmtree(os.path.join(basepath,root))
        if root != "probreg":
            print("removing templates...")
            shutil.rmtree(os.sep.join((basepath,"templates",root)))
    elif action in ("copy", "all"):
        print("creating and populating app root...")
        os.mkdir(os.path.join(basepath,root))
        newfile = open(os.sep.join((basepath,root,"__init__.py")),"w")
        newfile.close()
        for name in ('models','views','urls','admin','initial_data.json'):
            copyover(root,name,app)
        if root != "probreg":
                print("creating templates...")
                shutil.copytree(basepath + "/templates/probreg",basepath + "/templates/" + root)
    if action in ("activate", "all", "undo"):
        # toevoegen aan settings.py (INSTALLED_APPS)
        print("updating settings...")
        old,new = backup("settings.py")
        schrijf = False
        with open(old) as oldfile:
            with open(new,"w") as newfile:
                new_line = "    'probreg.{0}',\n".format(root)
                for line in oldfile:
                    if line.strip() == "INSTALLED_APPS = (":
                        schrijf = True
                    if schrijf and line.strip() == ")" and action != "undo":
                        newfile.write(new_line)
                        schrijf = False
                    if line == new_line and action == "undo":
                        schrijf = False
                    else:
                        newfile.write(line)
        # toevoegen aan urls.py (urlpatterns)
        print("updating urlpatterns...")
        old,new = backup("urls.py")
        schrijf = False
        with open(old) as oldfile:
            with open(new,"w") as newfile:
                new_line = "    (r'^{0}/', include('probreg.{0}.urls')),\n".format(root)
                for line in oldfile:
                    if line.strip().startswith('urlpatterns'):
                        schrijf = True
                    if schrijf and line.strip() == "" and action != "undo":
                        newfile.write(new_line)
                        schrijf = False
                    if line == new_line and action == "undo":
                        schrijf = False
                    else:
                        newfile.write(line)
        # database aanpassen en initiele settings data opvoeren
        if action != "undo":
            os.environ["DJANGO_SETTINGS_MODULE"] = 'probreg.settings'
            import settings
            from django.contrib.auth.models import Group, Permission
            print("modifying database...")
            os.system("python /home/visser/django/probreg/manage.py syncdb")
            print("loading inital data...")
            os.system("python manage.py loaddata {0}/initial_data.json".format(root))
            print("setting up authorisation groups...")
            grp = Group.objects.create(name='{0}_admin'.format(root))
            for perm in Permission.objects.filter(
                content_type__app_label="{0}".format(root)):
                    grp.permissions.add(perm)
            grp = Group.objects.create(name='{0}_user'.format(root))
            for perm in Permission.objects.filter(
                content_type__app_label="{0}".format(root)).filter(
                    content_type__model__in=['actie','event','sortorder','selection']):
                        grp.permissions.add(perm)

        print("updating apps registration...")
        old,new = backup(appsfile)
        with open(old) as _in:
            with open(new,"w") as _out:
                for app in _in:
                    ok,test_root,test_name,desc = app.split(";")
                    if test_root == root:
                        if action == "undo":
                            _out.write(app.replace("X;","_;"))
                        else:
                            _out.write(app.replace("_;","X;"))
                    else:
                        _out.write(app)
    if action == "loaddata":
        with open("loaddata.py") as oldfile:
            with open("load_data.py","w") as newfile:
                for line in oldfile:
                    newfile.write(line.replace("_basic",root))
        import load_data as ld
        print "loading settings...",
        ld.loadsett(load_from)
        print "ready."
        print "loading data...",
        ld.loaddata(load_from)
        print "ready."
    print("ready.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print USAGE
    else:
        ret = newproj(*sys.argv[1:])
        if ret:
            print ret
