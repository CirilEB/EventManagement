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
    sattendance = models.CharField(max_length=20,default="Absent")
    qr_image = models.ImageField(upload_to="student_qr",null=True,blank=True)
    certificate_image = models.ImageField(upload_to="Students_Certificates",null=True,blank=True)

class StudentDb(models.Model):
    student_name = models.CharField(max_length=50)
    student_email = models.EmailField()
    student_pass = models.CharField(max_length=20)
    student_otp = models.CharField(max_length=6,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)