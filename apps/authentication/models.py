from django.db import models


# Create your models here.
class TeacherModel(models.Model):
    teacher_id = models.CharField(max_length=10, unique=True)
    teacher_name = models.CharField(max_length=50)
    photo_path = models.CharField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "teacher"

    def __str__(self):
        return self.teacher_name;


class StudentModel(models.Model):
    student_id = models.CharField(max_length=10, unique=True)
    student_name = models.CharField(max_length=50)
    photo_path = models.CharField()
    is_deleted = models.BooleanField(default=False)
    moodle_id = models.CharField(max_length=10, unique=True, default="")

    class Meta:
        db_table = "student"

    def __str__(self):
        return self.student_name;

