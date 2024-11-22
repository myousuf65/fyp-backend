from deepface import DeepFace 
from django.shortcuts import render
from django.http import HttpResponse
import cv2


# Create your views here.
def sayHello(request):
    model_name = 'VGG-Face'
    dfs = DeepFace.verify(
        "/Users/ypathan/dev/fyp/backend/static/img1.jpeg",
        "/Users/ypathan/dev/fyp/backend/static/img2.jpeg", 
    )
    print("hello world", dfs)
    return HttpResponse("hello world");
