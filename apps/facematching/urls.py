from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.matchFace, name="say_hello" ),
    path('test2/', views.showHtml, name="say_html" ),
]

