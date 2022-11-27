from django.db import models
from django.contrib.auth.models import User
# from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

# class UserManager(BaseUserManager):
#     def create_user(self, username, email, password=None):
#         if username == None:
#             raise TypeError('Users should have a username.')
#         if email == None:
#             raise TypeError('Users should have a email.')
        
#         user = self.model(username=username, email=self.normalize_email(email))
#         user.set_password(password)
#         user.save() 
#         return user

#     def create_superuser(self, username, email, password=None):
#         if password == None:
#             raise TypeError('Password not be none.')
        
#         user = self.create_user(username, email, password)
#         user.is_superser = True
#         user.is_staff = True
#         user.save()
#         return user
    
# class User(AbstractBaseUser, PermissionsMixin):
#     username = models.CharField(max_length = 255, unique = True, db_index=True)
#     email = models.EmailField(max_length = 255, unique = True, db_index=True)
#     is_verified = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
#     is_staff = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add = True)
#     updated_at = models.DateTimeField(auto_now = True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     objects = UserManager()

#     def __str__(self):
#         return self.email

#     def tokens(self):
#         return ''

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=255, unique=True) # require
    detail = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, through='Membership')

    class Meta:
        ordering = ['created']

    def __str__(self) -> str:
        return self.name

class Exercise(models.Model):
    title = models.CharField(max_length=255) # require
    instruction = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    source_code = models.TextField(default='')

    class Meta:
        ordering = ['created']

    def __str__(self) -> str:
        return self.title

# many to many model 
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='members', related_query_name='member')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members', related_query_name='member')
    isStaff = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "({}, {})".format(self.user, self.team)

# userExercise
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', related_query_name='submission')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='submissions', related_query_name='submission')
    dateSubmit = models.DateTimeField(auto_now=True)
    code = models.TextField(blank=True)

    def __str__(self) -> str:
        return "({}, {})".format(self.user, self.exercise)
    
# Workbook = Exercise + Team
class Workbook(models.Model):
    openTime = models.DateTimeField()
    dueTime = models.DateTimeField(blank=True)
    isOpen = models.BooleanField(default=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='workbooks', related_query_name='workbook')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='workbooks', related_query_name='workbook')
    
    