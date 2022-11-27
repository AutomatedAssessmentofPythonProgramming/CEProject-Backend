from django.contrib import admin
from .models import Team, Exercise, Membership, Submission, Workbook

# Register your models here.
admin.site.register(Team)
admin.site.register(Exercise)
admin.site.register(Membership)
# admin.site.register(Submission)
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'exercise', 'dateSubmit']
    
@admin.register(Workbook)
class WorkbookAdmin(admin.ModelAdmin):
    list_display = ['pk', 'exercise', 'team', 'isOpen', 'openTime', 'dueTime']
