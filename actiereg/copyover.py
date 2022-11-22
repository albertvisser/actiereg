"""Copy actions from ProbReg project into ActieReg project
"""
import sys
sys.path.append('~/projects/probreg')
import probreg.dml_xml as dml
import actiereg._basic.models as my
from django.contrib.auth.models import User


def main(fnaam):
    """Main function
    """
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
