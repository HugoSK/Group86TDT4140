from django.db import models
from datetime import datetime
# Create your models here.

class Slowdown(models.Model):
    date = models.DateTimeField(default=datetime.now())