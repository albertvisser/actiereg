Files in this directory
=======================

files.rst
    this file
.gitignore
    voor Git te negeren files
manage.py
    command line functies voor Django
readme.rst
    basic info
.rurc
    configuratiebestand voor unittests
server-config-apache/nginx
    server configuratie voorbeelden

actiereg (project directory)
............................
__init__.py
    (lege) package indicator
asgi.py
    server programma voor asgi protocol
settings_no_key.py
    site instellingen zonder secret key
    (copy to settings.py and adapt to local specifications to make it work)
urls.py
    root url dispatcher
wsgi.py
    server programma voor wsgi protocol

tracker/ (primary app directory)
........................................
__init__.py
    (lege) package indicator
admin.py
    registratie van models tbv admin site
apps.py
    registratie van app t.b.v. settings
core.py
    logica- en data laag voor de views
models.py
    data definities
urls.py
    url dispatcher voor project
views.py
    project views (presentatielaag)

tracker/templatetags/
.............................
bevat zelfgedefinieerde tags en filters voor de tracker app

__init__.py
    (lege) package indicator
extratags.py
    de eigenlijke code

tracker/templates/
...................
base.html
    basis template
base_site.html
    algemene uitbreiding van base
index.html
    startpagina
logged_out.html
    standaard pagina na uitloggen
nieuw.html
    pagina voor aanmelden nieuw project

tracker/templates/tracker/
.........................
actie.html
    pagina voor weergave actiegegevens
base_site.html
    project uitbreiding van base en algemene base_site
index.html
    pagina voor weergave lijst met acties
order.html
    pagina voor definieren sortering van de lijst
select.html
    pagina voor definieren selectie van de lijst
settings.html
    pagina voor definieren project instellingen
tekst.html
    pagina voor tonen/aanpassen gegevens actie-onderdeel
voortgang.html
    pagina voor tonen/aanpassen voortgangsmomenten

actiereg/templates/registration/
................................
login.html
    aanlog pagina

tracker/migrations
..................
administratie voor databasewijzigingen

static/
.......
admin (not tracked)
    symlink to style stuff for the admin site (django/admin/static/admin)
actiereg.css
    extra vormgevingszaken
