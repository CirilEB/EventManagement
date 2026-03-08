from django.db import models

# Create your models here.
class CollegeDb(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    email = models.CharField(max_length=100)
    web = models.CharField(max_length=100)
    mob = models.IntegerField()
    logo = models.ImageField(upload_to="College_Logo")
    cuname = models.CharField(max_length=50,default="")
    cpswd = models.CharField(max_length=20,default="")
    def __str__(self):
        return self.name

class EventDb(models.Model):
    euname = models.CharField(max_length=50,default="")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=20)
    dept = models.CharField(max_length=10)
    start = models.DateField()
    end = models.DateField()
    dead = models.DateField()
    mode = models.CharField(max_length=10)
    location = models.CharField(max_length=100)
    maxS = models.IntegerField()
    fee = models.IntegerField()
    certificate = models.ImageField(upload_to='certificate_templates')
    poster = models.ImageField(upload_to='posters')
    status = models.CharField(max_length=20,default="Pending")
    name_x = models.IntegerField(null=True, blank=True)
    name_y = models.IntegerField(null=True, blank=True)
    event_x = models.IntegerField(null=True, blank=True)
    event_y = models.IntegerField(null=True, blank=True)
    date_x = models.IntegerField(null=True, blank=True)
    date_y = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

