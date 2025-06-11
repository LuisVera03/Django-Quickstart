from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Table3)
admin.site.register(models.Table2)
admin.site.register(models.Table1)