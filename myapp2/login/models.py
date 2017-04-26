from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
# Create your models here.
#do following command in command window after adding class:
#python manage.py makemigrations
#python manage.py migrate

class Datet(models.Model):
    name = models.CharField(max_length=128)
    datet = models.DateTimeField(default=timezone.now, blank= True)

class Slowdown(models.Model):
    name = models.CharField(max_length=128)
    datetimes = models.ManyToManyField(Datet, through='Membership')

class Membership(models.Model):
    datet = models.ForeignKey(Datet, on_delete=models.CASCADE)
    slowdown = models.ForeignKey(Slowdown, on_delete=models.CASCADE)
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class Question(models.Model):
    questionText = models.CharField(max_length=256)
    lecture = models.CharField(max_length=128)
