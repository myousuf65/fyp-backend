from django.urls import path
from . import views


urlpatterns = [
    path('compareface/', views.compareFace, name="compareface" ),
    path('registerface/', views.registerFace, name="registerface" ),
]
