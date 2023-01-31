from django.contrib import admin
from .models import Team, Exercise, Membership, Submission, Workbook

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'detail']
admin.site.register(Exercise)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'team', 'isStaff']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'exercise', 'dateSubmit']
    
@admin.register(Workbook)
class WorkbookAdmin(admin.ModelAdmin):
    list_display = ['pk', 'exercise', 'team', 'isOpen', 'openTime', 'dueTime']
