from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class student_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname=models.CharField(max_length=25)
    department = models.CharField(max_length=100, blank=True)
    ktu_id=models.CharField(max_length=20,unique=True,null=True)
    ph_no=models.CharField(max_length=15,null=True)
    roll_no=models.IntegerField(null=True)
    dob=models.DateField(null=True)
    cgpa=models.FloatField(null=True)


      