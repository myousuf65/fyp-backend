from django.urls import path
from . import views


urlpatterns = [
    path('compareface/<int:sessionid>/<str:coursename>/<int:teacherid>', views.getCompareFace, name="compareface"),
    path('compareface/', views.compareFace, name="compareface"),
    path('registerface/', views.registerFace, name="registerface" ),
]
