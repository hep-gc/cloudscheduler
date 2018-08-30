from django.db import models
from django.contrib.auth.models import User

import datetime

# Create your models here.
class user(models.Model):
    username = models.CharField(max_length=32, primary_key=True)
    cert_cn = models.CharField(max_length=128, null=True, default=None)   
    password = models.CharField(max_length=128, default="")
    is_superuser = models.BooleanField(default=False)
    join_date = models.DateField(default=datetime.date.today, null=True)
    active_group = models.CharField(max_length=128, null=True)

    def __str__(self):
        return "%s" % (self.username)
