from django.contrib import admin
from IOU_APP1.models import *
from django.apps import apps

for model in apps.get_app_config('IOU_APP1').models.values():
    admin.site.register(model)