Files in this directory
=======================

__init__.py
    (lege) package indicator
copyover.py
    utility programma om xml over te halen naar sqlite database
core.py
    code waar de views in de subdirectories naar verwijzen
fcgi_handler.py
    maakt het mogelijk deze site via fastcgi te draaien
files.rst
    this file
lees_probreg.py
    utility voor het utlezen van de gui/xml versie
loaddata.py
    utility programma; onderdeel van newapp
manage.py
    controle module
newapp.py
    utility programma: realiseren nieuw project
settings.py.origineel
    site instellingen
urls.py.origineel
    root url dispatcher
views.py
    root views voor django
wsgi_handler.py
    maakt het mogelijk deze site via wsgi te draaien

_basic/
.......
    views.py bevat de programmatuur voor een specifiek project
    in de vorm van aanroepen naar gelijknamige routines in core.py
    moet per project gekopieerd worden naar aparte map
    dat biedt de mogelijkheid om dat per project specifieker te maken
__init__.py
    (lege) package indicator
admin.py
    registratie van models tbv admin site
initial_data.json
    bevat initiele data voor de status soort en tit-header tabellen
models.py
    data mappings
sample_data.py
    voorbeeld gegevens
urls.py
     url dispatcher voor project
views.py
    project views

_basic/templatetags/
....................
    bevat zelfgedefinieerde tags
__init__.py
    (lege) package indicator
extratags.py
    de eigenlijke code

templates/
..........
base.html
    elementair template
base_site.html
    algemene uitbrieding van base
index.html
    startpagina
logged_out.html
    standaard pagina na uitloggen
nieuw.html
    pagina voor aanmelden nieuw project

templates/basic/
................
    bevat de templates voor een project
    bij het aanmaken van een nieuw project worden koppelingen naar deze aangemaakt
    deze voor elk project apart hebben geeft de mogelijkheid om de
    templates specifieker te maken zonder de andere projecten te raken
actie.html
    pagina voor weergave actiegegevens
base_site.html
    project uitbreiding van base en algemene base_site
index.html
    pagina voor weergave lijst met acties
order.html
    pagina voor definieren sortering van de lijst
probreg.css
    zit nu nog niks in
select.html
    pagina voor definieren selectie van de lijst
settings.html
    pagina voor definieren project instellingen
tekst.html
    pagina voor tonen/aanpassen gegevens actie-onderdeel
voortgang.html
    pagina voor tonen/aanpassen voortgangsmomenten

templates/registration/
.......................
login.html
    aanlog pagina
