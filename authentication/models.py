from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    def create_user(self, username, email, firstname, lastname, password=None):
        if username == None:
            raise TypeError('Users should have a username.')
        if email == None:
            raise TypeError('Users should have a email.')
        
        user = self.model(username=username, email=self.normalize_email(email), firstname=firstname, lastname=lastname)
        user.set_password(password)
        user.save() 
        return user

    def create_superuser(self, username, email, password=None):
        if password == None:
            raise TypeError('Password not be none.')
        
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length = 255, unique = True, db_index=True)
    email = models.EmailField(max_length = 255, unique = True, db_index=True)
    firstname = models.CharField(max_length=255, blank=True, default='')
    lastname = models.CharField(max_length=255, blank=True, default='')
    studentid= models.CharField(max_length=255, blank=True, default='')
    is_verified = models.BooleanField(default=False)
    # !!! carefull set is_active T
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
 