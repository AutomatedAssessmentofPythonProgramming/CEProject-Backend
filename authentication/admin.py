from django.contrib import admin
from .models import User
from django.contrib import auth

# admin.site.register(User)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email']

# @admin.register(Submission)
# class SubmissionAdmin(admin.ModelAdmin):
#     list_display = ['pk', 'user', 'exercise', 'dateSubmit']

admin.site.unregister(auth.models.Group)