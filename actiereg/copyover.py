"""Copy actions from ProbReg project into ActieReg project
"""
import dml
## import pprint as pp
## os.environ["DJANGO_SETTINGS_MODULE"] = 'actiereg.settings'
import settings
import _basic.models as my
from django.contrib.auth.models import User


def main(fnaam):
    """Main function
    """
    test = my.Actie()
    ## _out = open("_out".join(os.path.splitext(fnaam)),"w")
    ## data = dml.Settings()
    ## data.read()
    ## pp.pprint(data.stat)
    ## my.Status.objects.delete()
    ## for stat,gegs in data.stat:
    ##     title,order = gegs
    ##     my.Status.objects,create(value=stat,title=title,order=order)
    ## pp.pprint(data.cat)
    ## my.Soort.objects.delete()
    ## for srt,gegs in data.cat:
    ##     title,order = gegs
    ##     my.Soort.objects,create(value=cat,title=title,order=order)
    ## pp.pprint(data.kop)
    ## my.Page.objects.delete()
    ## for value,title in data.stat:
    ##     my.Page.objects,create(value=value,title=title)

    ## laatste = dml.LaatsteActie().nieuwnummer - 1
    data = [actie[0] for actie in dml.Acties(fnaam, arch="alles").lijst]
    for item in data:
        actie = dml.Actie(fnaam, item)
        about, what = actie.titel.split(": ")
        if actie.status == "":
            actie.status = " "
        nieuw = my.Actie.objects.create(nummer=actie.id,
                                        starter=User.objects.get(pk=1),
                                        about=about,
                                        title=what,
                                        lasteditor=User.objects.get(pk=1),
                                        status=my.Status.objects.get(value=actie.status),
                                        soort=my.Soort.objects.get(value=actie.soort),
                                        behandelaar=User.objects.get(pk=1),
                                        gewijzigd=actie.datum,
                                        arch=actie.arch,
                                        melding=actie.melding,
                                        oorzaak=actie.oorzaak,
                                        oplossing=actie.oplossing,
                                        vervolg=actie.vervolg)
        for start, text in actie.events:
            my.Event.objects.create(actie=nieuw,
                                    start=start,
                                    starter=User.objects.get(pk=1),
                                    text=text)

if __name__ == "__main__":
    main("probreg.xml")
