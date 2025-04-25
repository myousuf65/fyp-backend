import os

import b2sdk.v2 as b2
import pandas as pd
import requests
from deepface import DeepFace
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from dotenv import load_dotenv

from apps.authentication.models import StudentModel
from test import all_statuses

info = b2.InMemoryAccountInfo()
load_dotenv()
b2_api = b2.B2Api(info)

APPLICATION_KEY_ID = os.getenv("B2_KEY_ID")
APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
DATASET_DB_PATH = os.getenv("DATASET_DB_PATH")
MOODLE_URL = os.getenv("MOODLE_URL")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")


@ensure_csrf_cookie
def compareFace(request):
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
                        matched_faces.append(matched_full_path.split("/")[-1].replace(".jpeg", "").replace(".png", ""))
                    except KeyError:
                        print("No match for one of the faces")

                if matched_faces:
                    print(f"Matched faces: {matched_faces}")
                    student  = StudentModel.objects.all().filter(student_id=int(matched_faces[0])).first()
                    print(student)

                    context = request.session.get("attendance_context", {})
                    attendance_id = context.get("attendance_id")
                    course_id = context.get("course_id")
                    teacherid = context.get("teacherid")
                    statuses = context.get("stutuses")
                    sessionid = context.get("sessionid")

                    all_statuses = ",".join(str(status) for status in context.get("statuses"))
                    present_id = 0
                    mark_attendance_url = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=mod_attendance_update_user_status&moodlewsrestformat=json"

                    for status in context.get("statuses"):
                        if status['acronym'] == 'P':
                            present_id = status['id']

                    data = {
                        "sessionid": context.get("sessionid"),
                        "studentid": student.moodle_id,
                        "takenbyid": context.get("teacherid"),
                        "statusid": present_id,
                        "statusset": all_statuses
                    }


                    mark_attendance_response = requests.post(mark_attendance_url, data=data)
                    if mark_attendance_response.json() is None:
                        return JsonResponse({
                            "message": "True",
                            "matched_person_names": matched_faces,
                        })
                    else:
                        print("MOODLE RESPONSE:" , mark_attendance_response)
                        return JsonResponse({
                            "error": "Error Marking Attendance for your in Moodle"
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



@ensure_csrf_cookie
def getCompareFace(request, sessionid, coursename, teacherid):
    if request.method == "GET":
        getSessionInfoUrl = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=mod_attendance_get_session&moodlewsrestformat=json"
        getSessionInfoData:dict = {
            "sessionid":sessionid
        }
        getSessionInfoResponse = requests.post(getSessionInfoUrl,data=getSessionInfoData)
        print(getSessionInfoResponse.json())
        status = [
            {
                "id":   s["id"],
                "acronym" : s["acronym"],

            }
            for s in getSessionInfoResponse.json().get("statuses")
        ]

        context = {
            "statuses": status,
            "attendance_id" : getSessionInfoResponse.json().get("attendanceid"),
            "course_id" : getSessionInfoResponse.json().get("courseid"),
            "sessionid" : sessionid,
            "course_name" : coursename,
            "teacherid" : teacherid
        }

        request.session['attendance_context'] = context
        return render(request, "compare_face.html", context)
    return None


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

            moodle_url = MOODLE_URL + "?wstoken=" + MOODLE_TOKEN + "&wsfunction=core_user_create_users&moodlewsrestformat=json"

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
        return None
    return None
