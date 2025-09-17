from django.contrib import admin
from django.contrib.auth import get_user_model
from . import models

admin.site.register(models.Table3)
admin.site.register(models.Table2)
admin.site.register(models.Table1)
admin.site.register(models.UserLog)
