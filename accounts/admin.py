from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import CustomUser,Profile
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Permission)
admin.site.register(ContentType)
admin.site.register(Session)
