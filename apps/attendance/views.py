from http.client import HTTPResponse
from deepface import DeepFace
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import ensure_csrf_cookie
from deepface import DeepFace
import os
from dotenv import load_dotenv
import b2sdk.v2 as b2
from apps.authentication.models import StudentModel
from django.http import JsonResponse
import pandas as pd
import requests

info = b2.InMemoryAccountInfo()
load_dotenv()
b2_api = b2.B2Api(info)

APPLICATION_KEY_ID = os.getenv("B2_KEY_ID")
APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
DATASET_DB_PATH = os.getenv("DATASET_DB_PATH")


@ensure_csrf_cookie
def compareFace(request):
    if request.method == "GET":
        return render(request, "compare_face.html")

    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
            print("the file path is ", file_path)
            # all_student = StudentModel.objects.all();
            result = DeepFace.find(
                img_path=file_path,
                db_path=DATASET_DB_PATH,
                enforce_detection=False,
                anti_spoofing=False,
                model_name='VGG-Face',
                distance_metric='cosine',
                threshold=0.5
            )
            pd.set_option('display.max_colwidth', None)
            print("-------")

            # Check if there are matches
            if result:
                matched_faces = []
                for face in result:
                    try:
                        matched_full_path = face['identity'][0]
                        matched_faces.append(matched_full_path.split("/")[-1].replace(".jpeg", ""))
                    except KeyError:
                        print("No match for one of the faces")

                if matched_faces:
                    print(f"Matched faces: {matched_faces}")
                    return JsonResponse({
                        "message": "True",
                        "matched_person_names": matched_faces,
                    })
                else:
                    print("No matches found")
                    return JsonResponse({
                        "error": "No matching faces found"
                    })
            else:
                return JsonResponse({
                    "error": "No faces detected or no matches found"
                })

        else:
            return JsonResponse({"error": "No image found in the request"}, status=400)

    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


# @ensure_csrf_cookie
# def compareFace(request):
#     if request.method == "GET":
#         return render(request, "compare_face.html")
#     if request.method == "POST":
#         image_data = request.FILES.get("image")
#         if image_data:
#             file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
#             print("the file path is ",  file_path)
#             # all_student = StudentModel.objects.all();
#             result = DeepFace.find(
#                 img_path=file_path,
#                 db_path="/Users/ypathan/dev/fyp/backend/static/dataset",
#                 enforce_detection=True,
#                 anti_spoofing=True,
#                 model_name='VGG-Face',
#                 distance_metric='cosine',
#                 threshold=0.5
#             )
#             pd.set_option('display.max_colwidth', None)
#             print("-------")
#             try:
#                 matched_full_path: str = result[0]['identity'][0]
#                 print("your face matched with", matched_full_path)
#
#                 return JsonResponse({
#                     "message" : "True",
#                     "matched_person_name" : matched_full_path.split("/")[-1].replace(".jpeg", ""),
#                     # "matched_person_id" : s.student_id,
#                 })
#                 pass
#             except KeyError:
#                 print("your face is not here")
#                 return JsonResponse({
#                     "error" : "Your Face did not match with anyone"
#                 })
#         else:
#             return JsonResponse({"error": "No image found in the request"}, status=400)
#     else:
#         return JsonResponse({"error": "Invalid HTTP method"}, status=405)
#
#


@ensure_csrf_cookie
def registerFace(request):
    if request.method == "GET":
        return render(request, 'register_face.html')

    if request.method == "POST":
        image_data = request.FILES.get("image")
        student_id = request.POST.get("student-id")
        # Check if student_id already exists
        if StudentModel.objects.filter(student_id=student_id).exists():
            return JsonResponse({
                "message": "This student already exists"

            }, status=400)
        student_name = request.POST.get("student-name")
        print("DATA RECEIVED BY REQUEST : ", student_id, student_name)

        if image_data:
            # Save image to temporary storage
            file_path = default_storage.save("static/dataset/" + student_id + ".jpeg", image_data)
            file_name = student_id + ".jpeg"

            # Save student record in the database

            moodle_url = "http://172.104.186.148/moodle/webservice/rest/server.php?wstoken=a24678df4df3db2a34ce6f4ac22d6de7&wsfunction=core_user_create_users&moodlewsrestformat=json"

            data = {
                "users[0][username]": student_name,
                "users[0][password]": "Nokian876@moodle",
                "users[0][firstname]": student_name.split("@")[0],
                "users[0][lastname]": student_name.split("@")[1],
                "users[0][email]": student_name.split("@")[0] + "@gmail.com",
                "users[0][auth]": "manual",
                "users[0][lang]": "en",
                "users[0][timezone]": "Asia/Hong_Kong"
            }


            try:
                # Make API call to Moodle
                response = requests.post(moodle_url, data=data)

                # Printing the response
                print("MOODLE RESPONSE STATUS ", response.status_code)
                print("MOODLE RESPONSE TEXT ", response.text)

                response_data = response.json()
                STUDENT_NAME = response_data[0]["username"]
                MOODLE_ID = response_data[0]["id"]

                try:
                    student = StudentModel(student_id=student_id, moodle_id=MOODLE_ID, student_name=student_name,
                                           photo_path=file_name)
                    student.save()
                except Exception as e:
                    print(e)


                # Handle Moodle API response
                if response.status_code == 200 and "exception" not in response_data:
                    return JsonResponse({
                        "student_id": MOODLE_ID,
                        "username": STUDENT_NAME,
                        "moodle_response": response_data
                    }, status=200)
                else:
                    return JsonResponse({
                        "message": "Failed to register user in Moodle",
                        "moodle_error": response_data
                    }, status=400)
            except Exception as e:
                return JsonResponse({
                    "message": "An error occurred while calling Moodle API",
                    "error": str(e)
                }, status=500)
