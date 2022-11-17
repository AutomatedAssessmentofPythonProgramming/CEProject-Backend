from django.db import models

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=255) # require
    detail = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)

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
