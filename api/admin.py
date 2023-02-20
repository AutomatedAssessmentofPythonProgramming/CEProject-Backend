from django.contrib import admin
from .models import Team, Exercise, Membership, Submission, Workbook

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'detail']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'created', 'updated', 'owner']

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'team', 'isStaff']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'exercise', 'dateSubmit']
    
@admin.register(Workbook)
class WorkbookAdmin(admin.ModelAdmin):
    list_display = ['pk', 'exercise', 'team', 'isOpen', 'openTime', 'dueTime']
