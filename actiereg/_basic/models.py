"""Data item definitions
"""
from django.db import models
from django.contrib.auth.models import User

ORIENTS = (('asc', 'oplopend'), ('desc', 'aflopend'))
SORTFIELDS = [("nummer", "nummer"),
              ("gewijzigd", "laatst gewijzigd"),
              ("soort", "soort"),
              ("status", "status"),
              ("behandelaar", "behandelaar"),
              ("title", "omschrijving")]
CHOICES = (('  ', '  '),
           ('EN', 'en'),
           ('OF', 'of'))
OP_CHOICES = (('LT', 'kleiner dan'),
              ('GT', 'groter dan'),
              ('EQ', 'gelijk aan'),
              ('NE', 'ongelijk aan'),
              ('INCL', 'bevat'),
              ('EXCL', 'bevat niet'))


class Status(models.Model):
    """gemeld, in behandeling, afgehandeld e.d.
    intitiele set waarden, kan door projectadmin aangepast worden"""
    title = models.CharField(max_length=32)
    value = models.PositiveSmallIntegerField(unique=True)
    order = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return self.title


class Soort(models.Model):
    """probleem, wens e.d.
    initiele set waarden, kan door projectadmin aangepast worden"""
    title = models.CharField(max_length=32)
    value = models.CharField(max_length=1, unique=True)
    order = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return self.title


class Page(models.Model):
    """titels voor de links/onderdelen
    vaste set, naam kan door projectadmin aangepast worden"""
    title = models.CharField(max_length=32)
    link = models.CharField(max_length=8)
    order = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return self.title


class Actie(models.Model):
    """primaire gegevenstabel"""
    nummer = models.CharField(max_length=32)
    start = models.DateTimeField(auto_now_add=True)
    starter = models.ForeignKey(User, related_name="actiehouder", on_delete=models.CASCADE)
    about = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=80, blank=True)
    gewijzigd = models.DateTimeField(auto_now=True)
    lasteditor = models.ForeignKey(User, related_name="editor", on_delete=models.CASCADE)
    soort = models.ForeignKey('Soort', on_delete=models.CASCADE)
    status = models.ForeignKey('Status', on_delete=models.CASCADE)
    behandelaar = models.ForeignKey(User, related_name="actienemer", on_delete=models.CASCADE)
    arch = models.BooleanField(default=False)
    melding = models.TextField(blank=True)
    oorzaak = models.TextField(blank=True)
    oplossing = models.TextField(blank=True)
    vervolg = models.TextField(blank=True)

    def __str__(self):
        return self.nummer  # ": ".join((self.about, self.title))


class Event(models.Model):
    """historische gegevens over een actie"""
    actie = models.ForeignKey('Actie', related_name="events", on_delete=models.CASCADE)
    start = models.DateTimeField(auto_now_add=True)
    starter = models.ForeignKey(User, related_name="ev_editor", on_delete=models.CASCADE)
    text = models.TextField(blank=True)


class SortOrder(models.Model):
    """per-user verzameling sorteersleutels t.b.v. actie-overzicht"""
    user = models.PositiveSmallIntegerField()
    volgnr = models.PositiveSmallIntegerField()
    veldnm = models.CharField(max_length=16)
    richting = models.CharField(max_length=4, choices=ORIENTS)

    def __str__(self):
        return " ".join((str(self.volgnr), self.veldnm, self.richting))


class Selection(models.Model):
    """per-user verzameling selectieargumenten t.b.v. actie-overzicht"""
    user = models.PositiveSmallIntegerField()
    veldnm = models.CharField(max_length=16)
    operator = models.CharField(max_length=4, choices=OP_CHOICES)
    extra = models.CharField(max_length=2, choices=CHOICES)
    value = models.CharField(max_length=40)

    def __str__(self):
        return " ".join((self.veldnm, self.extra, self.operator, self.value))


class Worker(models.Model):
    """medewerkers voor dit project
    bevat de mogelijke waarden voor de user-velden in de actie"""
    assigned = models.ForeignKey(User, related_name="worker", on_delete=models.CASCADE)

    def __str__(self):
        return self.assigned.username
