from django.db import models

# Create your models here.
class RegistrationDb(models.Model):
    event_name = models.CharField(max_length=100)
    sname = models.CharField(max_length=30)
    semail = models.CharField(max_length=50)
    scollege = models.CharField(max_length=100)
    sdept = models.CharField(max_length=50)
    syear = models.CharField(max_length=10)
    smob = models.IntegerField()

