from django.db import models
from datetime import datetime
# Create your models here.
#do following command in command window after adding class:
#python manage.py makemigrations
#python manage.py migrate

class Slowdown(models.Model):
    date = models.DateTimeField(default=datetime.now())