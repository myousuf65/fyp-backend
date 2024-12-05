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

info = b2.InMemoryAccountInfo()
load_dotenv()
b2_api = b2.B2Api(info)

application_key_id = os.getenv("B2_KEY_ID")
application_key = os.getenv("B2_APPLICATION_KEY")


@ensure_csrf_cookie
def compareFace(request):
    if request.method == "GET":
        return render(request, "compare_face.html")
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
            res = DeepFace.verify(file_path, 'static/dataset/imran_khan.png')
            print(f"File saved at: {file_path}")
            print(res)

            # Return a response indicating success
            return JsonResponse({"message": res})

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
        student_name = request.POST.get("student-name")
        print(student_id, student_name)
        if image_data :
            # save to temp
            file_path = default_storage.save("static/temp_storage/register_photo.jpeg", image_data)
            # upload to backblaze
            b2_api.authorize_account("production", application_key_id, application_key)
            bucket = b2_api.get_bucket_by_name("class1")
            file_name = student_id+".jpeg"
            uploaded_file = bucket.upload_local_file(local_file=file_path, file_name=file_name)
            download_url = b2_api.get_download_url_for_fileid(uploaded_file.id_)
            response = HttpResponse();
            response.write(download_url)
            return response

