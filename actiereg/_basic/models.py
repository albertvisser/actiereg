from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

class Status(models.Model):
    """gemeld, in behandeling, afgehandeld e.d.
    intitiele set waarden, kan door projectadmin aangepast worden"""
    title = models.CharField(max_length=32)
    value = models.PositiveSmallIntegerField(unique=True)
    order = models.PositiveSmallIntegerField(unique=True)
    def __unicode__(self):
        return self.title

class Soort(models.Model):
    """probleem, wens e.d.
    intitiele set waarden, kan door projectadmin aangepast worden"""
    title = models.CharField(max_length=32)
    value = models.CharField(max_length=1,unique=True)
    order = models.PositiveSmallIntegerField(unique=True)
    def __unicode__(self):
        return self.title

class Page(models.Model):
    """titels voor de links/onderdelen
    vaste set, naam kan door projectadmin aangepast worden"""
    title = models.CharField(max_length=32)
    link = models.CharField(max_length=8)
    order = models.PositiveSmallIntegerField(unique=True)
    def __unicode__(self):
        return self.title

class Actie(models.Model):
    """primaire gegevenstabel"""
    nummer = models.CharField(max_length=32)
    start = models.DateTimeField(auto_now_add=True)
    starter = models.ForeignKey(User,related_name="actiehouder_basic")
    about = models.CharField(max_length=32,blank=True)
    title = models.CharField(max_length=80,blank=True)
    gewijzigd = models.DateTimeField(auto_now=True)
    lasteditor = models.ForeignKey(User,related_name="editor_basic")
    soort = models.ForeignKey('Soort')
    status = models.ForeignKey('Status')
    behandelaar = models.ForeignKey(User,related_name="actienemer_basic")
    arch = models.BooleanField(default=False)
    melding = models.TextField(blank=True)
    oorzaak = models.TextField(blank=True)
    oplossing = models.TextField(blank=True)
    vervolg = models.TextField(blank=True)
    def __unicode__(self):
        return self.nummer # ": ".join((self.about,self.title))

class Event(models.Model):
    """historische gegevens over een actie"""
    actie = models.ForeignKey('Actie', related_name="events")
    start = models.DateTimeField(auto_now_add=True)
    starter = models.ForeignKey(User,related_name="ev_editor_basic")
    text = models.TextField(blank=True)
    ## def __unicode__(self):
        ## return self.start

class SortOrder(models.Model):
    """per-user verzameling sorteersleutels t.b.v. actie-overzicht"""
    CHOICES = (
        ('asc','oplopend'),
        ('desc','aflopend'),
        )
    user = models.PositiveSmallIntegerField()
    volgnr = models.PositiveSmallIntegerField()
    veldnm = models.CharField(max_length=16)
    richting = models.CharField(max_length=4, choices=CHOICES)
    def __unicode__(self):
        return " ".join((str(self.nummer),self.veldnm,self.richting))

class Selection(models.Model):
    """per-user verzameling selectieargumenten t.b.v. actie-overzicht"""
    CHOICES = (
        ('  ','  '),
        ('EN','en'),
        ('OF','of'),
        )
    OP_CHOICES = (
        ('LT','kleiner dan'),
        ('GT','groter dan'),
        ('EQ','gelijk aan'),
        ('NE','ongelijk aan'),
        ('INCL','bevat'),
        ('EXCL','bevat niet'),
        )
    user = models.PositiveSmallIntegerField()
    veldnm = models.CharField(max_length=16)
    operator = models.CharField(max_length=4, choices=OP_CHOICES)
    extra = models.CharField(max_length=2, choices=CHOICES)
    value = models.CharField(max_length=40)
    def __unicode__(self):
        return " ".join((self.veldnm,self.extra,self.operator,self.value))

class Worker(models.Model):
    """medewerkers voor dit project
    bevat de mogelijke waarden voor de user-velden in de actie"""
    assigned = models.ForeignKey(User,related_name="worker_basic")
    def __unicode__(self):
        return self.assigned.username
