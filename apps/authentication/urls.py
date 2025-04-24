from django.urls import path
from . import views


urlpatterns = [
    path('teacher/', views.teacherLogin, name="teacherLogin" ),
]