from django.contrib import admin

from apps.attendance.models import AttendanceModel, CourseModel, CourseRegistartionModel

# Register your models here.
admin.site.register(CourseModel)
admin.site.register(AttendanceModel)
admin.site.register(CourseRegistartionModel)

