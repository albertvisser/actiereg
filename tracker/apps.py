"""app registration for actiereg/tracker
"""
from django.apps import AppConfig


class TrackerConfig(AppConfig):
    "configuration specific for tracker app"
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'
