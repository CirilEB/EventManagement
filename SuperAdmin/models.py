from django.db import models

# Create your models here.
class DepartmentDb(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    mob = models.BigIntegerField()
    hod = models.CharField(max_length=50)
    cuname = models.CharField(max_length=50,default="")
    cpswd = models.CharField(max_length=128,default="")
    def __str__(self):
        return self.name

class EventDb(models.Model):
    conclude = models.CharField(null=True,blank=True)
    is_archived = models.BooleanField(default=False)
    euname = models.CharField(max_length=50,default="")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=20)
    start = models.DateField()
    end = models.DateField()
    dead = models.DateField()
    mode = models.CharField(max_length=10)
    location = models.CharField(max_length=100)
    maxS = models.BigIntegerField()
    fee = models.BigIntegerField()
    certificate = models.ImageField(upload_to='certificate_templates')
    poster = models.ImageField(upload_to='posters')
    status = models.CharField(max_length=20,default="Pending")

    name_x = models.BigIntegerField(null=True, blank=True)
    name_y = models.BigIntegerField(null=True, blank=True)
    event_x = models.BigIntegerField(null=True, blank=True)
    event_y = models.BigIntegerField(null=True, blank=True)
    date_x = models.BigIntegerField(null=True, blank=True)
    date_y = models.BigIntegerField(null=True, blank=True)
    qr_x = models.BigIntegerField(null=True, blank=True)
    qr_y = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

