from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class user(models.Model):
    username = models.CharField(max_length=32)
    cert_dn = models.CharField(max_length=128, default="")   
    password = models.CharField(max_length=128, default="")
    is_superuser = models.BooleanField(default=False)
    join_date = models.DateField()

    def __str__(self):
        return "%s" % (self.user_name)