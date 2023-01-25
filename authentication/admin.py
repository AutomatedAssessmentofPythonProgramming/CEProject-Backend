from django.contrib import admin
from .models import User
from django.contrib import auth

admin.site.register(User)

admin.site.unregister(auth.models.Group)