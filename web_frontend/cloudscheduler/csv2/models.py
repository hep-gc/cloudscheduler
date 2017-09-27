from django.db import models

# Create your models here.
class csv2_user(models.Model):
    username = models.CharField(max_length=32)
    cert_dn = models.CharField(max_length=128, default="")   
    password = models.CharField(max_length=128, default="")
    join_date = models.DateField()

    def __str__(self):
        return "%s" % (self.user_name)