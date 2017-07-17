"""register models to the admin site
"""
from django.contrib import admin
import actiereg._basic.models as my

admin.site.register(my.Status)
admin.site.register(my.Soort)
admin.site.register(my.Page)
admin.site.register(my.Actie)
admin.site.register(my.Event)
admin.site.register(my.Worker)
