from django.urls import path
from . import views


urlpatterns = [
    path('compareface/<int:sessionid>/<str:coursename>/<int:teacherid>', views.getCompareFace, name="compareface"),
    path('compareface/', views.compareFace, name="compareface"),
    path('compare/', views.compareFaceWithoutAttendance, name="compare"),
    path('compareportal/', views.compareFaceWithoutAttendancePortal, name="compareportal"),
    path('compareportalteacher/', views.compareFaceWithoutAttendancePortalTeacher, name="compareportalteacher"),
    path('registerface/', views.registerFace, name="registerface" ),
]
