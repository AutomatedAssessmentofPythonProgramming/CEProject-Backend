from django.db import models
from authentication.models import User

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=255, unique=True) # require
    detail = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, through='Membership')
    inviteCode = models.CharField(max_length=255, unique=True)
    # number of exercise

    class Meta:
        ordering = ['created']

    def __str__(self) -> str:
        return self.name

class Exercise(models.Model):
    title = models.CharField(max_length=255) # require
    instruction = models.TextField(default='', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    source_code = models.TextField(default='', blank=True)
    config_code = models.TextField(default='', blank=True)
    unittest = models.TextField(default='', blank=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    code_name = models.CharField(max_length=255, default='user_code')
    example_code = models.TextField(default='', blank=True)

    class Meta:
        ordering = ['created']

    def __str__(self) -> str:
        return self.title

# many to many model 
# Team User
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    isStaff = models.BooleanField(default=False)
    isVerify = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "({}, {})".format(self.user, self.team)

# Submission = user + exercise + team
class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', related_query_name='submission')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='submissions', related_query_name='submission')
    dateSubmit = models.DateTimeField(auto_now=True)
    isLate = models.BooleanField(default=False)
    isDone = models.BooleanField(default=False)
    code = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['dateSubmit']

    def __str__(self) -> str:
        return "({}, {})".format(self.user, self.exercise)
    
# Workbook = Exercise + Team
class Workbook(models.Model):
    openTime = models.DateTimeField(blank=True, null=True)
    dueTime = models.DateTimeField(blank=True, null=True)
    isOpen = models.BooleanField(default=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='workbooks', related_query_name='workbook')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='workbooks', related_query_name='workbook')
    week = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['dateCreated']
    