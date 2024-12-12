from django.db import models
from django.contrib import admin 



# Create your models here.
class Student(models.Model):
    student_id = models.CharField(max_length=10, unique = True)
    student_name = models.CharField(max_length=50)
    photo_path = models.CharField()
