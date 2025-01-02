from http.client import HTTPResponse
from deepface import DeepFace 
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import ensure_csrf_cookie
from deepface import DeepFace
import os 
from dotenv import load_dotenv 
import b2sdk.v2 as b2  
from .models import Student
from django.http import JsonResponse
import pandas as pd

info = b2.InMemoryAccountInfo()
load_dotenv()
b2_api = b2.B2Api(info)

APPLICATION_KEY_ID = os.getenv("B2_KEY_ID")
APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
DATASET_DB_PATH = os.getenv("DATASET_DB_PATH")

# @ensure_csrf_cookie
# def test(request):
#     result = DeepFace.find(img_path="/Users/ypathan/dev/fyp/backend/static/dataset/temp_storage/register_photo.jpeg", db_path="/Users/ypathan/dev/fyp/backend/static/dataset")
#     print("-------")
#     print(result.head())
#     print("-------")



@ensure_csrf_cookie
def compareFace(request):
    if request.method == "GET":
        return render(request, "compare_face.html")
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
            print("the file path is ",  file_path)
            # all_student = Student.objects.all();
            result = DeepFace.find(img_path=file_path, db_path="/Users/ypathan/dev/fyp/backend/static/dataset", enforce_detection=True, anti_spoofing=True, model_name='VGG-Face', distance_metric='cosine', threshold=0.5)
            pd.set_option('display.max_colwidth', None)
            print("-------")
            try:
                matched_full_path: str = result[0]['identity'][0]
                print("your face matched with", matched_full_path)
                                                 
                return JsonResponse({
                    "message" : "True",
                    "matched_person_name" : matched_full_path.split("/")[-1].replace(".jpeg", ""),
                    # "matched_person_id" : s.student_id,
                })
                pass
            except KeyError:
                print("your face is not here")
                return JsonResponse({
                    "error" : "Your Face did not match with anyone"
                })
        else:
            return JsonResponse({"error": "No image found in the request"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)



@ensure_csrf_cookie
def registerFace(request):
    if request.method == "GET":
        return render(request, 'register_face.html')
    
    if request.method == "POST":
        image_data = request.FILES.get("image")
        student_id = request.POST.get("student-id")
        
        # check if student_id already exists
        if Student.objects.filter(student_id = student_id).exists():
            return JsonResponse({
                "message" : "this student already exists"
            }, status=400)

        student_name = request.POST.get("student-name")
        print(student_id, student_name)
        if image_data :
            # save to temp
            file_path = default_storage.save("static/dataset/"+ student_id + ".jpeg", image_data)
            # upload to backblaze
            b2_api.authorize_account("production", APPLICATION_KEY_ID, APPLICATION_KEY)
            bucket = b2_api.get_bucket_by_name("class1")
            file_name = student_id+".jpeg"
            uploaded_file = bucket.upload_local_file(local_file=file_path, file_name=file_name)
            download_url = b2_api.get_download_url_for_fileid(uploaded_file.id_)
            student = Student(student_id=student_id, student_name=student_name, photo_path=download_url )
            student.save()
            # feed user data into a model and save to db
            return JsonResponse({
                "student_id" : student.student_id,
                "student_name" : student.student_name,
                "photo_path" : student.photo_path
            },status=200)

