     1 from django.db import models
     2 from django.forms import ModelForm
     3 from django.contrib.auth.models import User
     4
     5 class Status(models.Model):
     6     """gemeld, in behandeling, afgehandeld e.d.
     7     intitiele set waarden, kan door projectadmin aangepast worden"""
     8     title = models.CharField(max_length=32)
     9     value = models.PositiveSmallIntegerField(unique=True)
    10     order = models.PositiveSmallIntegerField(unique=True)
    11     def __unicode__(self):
    12         return self.title
    13
    14 class Soort(models.Model):
    15     """probleem, wens e.d.
    16     intitiele set waarden, kan door projectadmin aangepast worden"""
    17     title = models.CharField(max_length=32)
    18     value = models.CharField(max_length=1,unique=True)
    19     order = models.PositiveSmallIntegerField(unique=True)
    20     def __unicode__(self):
    21         return self.title
    22
    23 class Page(models.Model):
    24     """titels voor de links/onderdelen
    25     vaste set, naam kan door projectadmin aangepast worden"""
    26     title = models.CharField(max_length=32)
    27     link = models.CharField(max_length=8)
    28     order = models.PositiveSmallIntegerField(unique=True)
    29     def __unicode__(self):
    30         return self.title
    31
    32 class Actie(models.Model):
    33     """primaire gegevenstabel"""
    34     nummer = models.CharField(max_length=32)
    35     start = models.DateTimeField(auto_now_add=True)
    36     starter = models.ForeignKey(User,related_name="actiehouder_basic")
    37     about = models.CharField(max_length=32,blank=True)
    38     title = models.CharField(max_length=80,blank=True)
    39     gewijzigd = models.DateTimeField(auto_now=True)
    40     lasteditor = models.ForeignKey(User,related_name="editor_basic")
    41     soort = models.ForeignKey('Soort')
    42     status = models.ForeignKey('Status')
    43     behandelaar = models.ForeignKey(User,related_name="actienemer_basic")
    44     arch = models.BooleanField(default=False)
    45     melding = models.TextField(blank=True)
    46     oorzaak = models.TextField(blank=True)
    47     oplossing = models.TextField(blank=True)
    48     vervolg = models.TextField(blank=True)
    49     def __unicode__(self):
    50         return self.nummer # ": ".join((self.about,self.title))
    51
    52 class Event(models.Model):
    53     """historische gegevens over een actie"""
    54     actie = models.ForeignKey('Actie', related_name="events")
    55     start = models.DateTimeField(auto_now_add=True)
    56     starter = models.ForeignKey(User,related_name="ev_editor_basic")
    57     text = models.TextField(blank=True)
    58     ## def __unicode__(self):
    59         ## return self.start
    60
    61 class SortOrder(models.Model):
    62     """per-user verzameling sorteersleutels t.b.v. actie-overzicht"""
    63     CHOICES = (
    64         ('asc','oplopend'),
    65         ('desc','aflopend'),
    66         )
    67     user = models.PositiveSmallIntegerField()
    68     volgnr = models.PositiveSmallIntegerField()
    69     veldnm = models.CharField(max_length=16)
    70     richting = models.CharField(max_length=4, choices=CHOICES)
    71     def __unicode__(self):
    72         return " ".join((str(self.nummer),self.veldnm,self.richting))
    73
    74 class Selection(models.Model):
    75     """per-user verzameling selectieargumenten t.b.v. actie-overzicht"""
    76     CHOICES = (
    77         ('  ','  '),
    78         ('EN','en'),
    79         ('OF','of'),
    80         )
    81     OP_CHOICES = (
    82         ('LT','kleiner dan'),
    83         ('GT','groter dan'),
    84         ('EQ','gelijk aan'),
    85         ('NE','ongelijk aan'),
    86         ('INCL','bevat'),
    87         ('EXCL','bevat niet'),
    88         )
    89     user = models.PositiveSmallIntegerField()
    90     veldnm = models.CharField(max_length=16)
    91     operator = models.CharField(max_length=4, choices=OP_CHOICES)
    92     extra = models.CharField(max_length=2, choices=CHOICES)
    93     value = models.CharField(max_length=40)
    94     def __unicode__(self):
    95         return " ".join((self.veldnm,self.extra,self.operator,self.value))
    96
    97 class Worker(models.Model):
    98     """medewerkers voor dit project
    99     bevat de mogelijke waarden voor de user-velden in de actie"""
   100     assigned = models.ForeignKey(User,related_name="worker_basic")
   101     def __unicode__(self):
   102         return self.assigned.username
