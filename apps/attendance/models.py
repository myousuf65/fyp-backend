from django.db import models

class CourseModel(models.Model):
    course_id = models.CharField(max_length=10)
    course_name = models.CharField(max_length=70)
    course_teacher = models.ForeignKey("authentication.TeacherModel", on_delete=models.CASCADE)  # Correct capitalization

    class Meta:
        db_table = "course"

    def __str__(self):
       return self.course_name;

class AttendanceModel(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey("authentication.StudentModel", on_delete=models.DO_NOTHING)  # Correct capitalization
    course_id = models.ForeignKey("CourseModel", on_delete=models.DO_NOTHING)
    date_of_attendance = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance"

    def __str__(self):
        return f"{self.student_id} --  {self.course_id} -- {self.date_of_attendance}"


class CourseRegistartionModel(models.Model):
    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey("CourseModel", on_delete=models.DO_NOTHING)
    student_id = models.ForeignKey("authentication.StudentModel", on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "course_registration"

    def __str__(self):
       return f"{self.course_id} --  {self.student_id}"

