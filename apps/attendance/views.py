import os

import b2sdk.v2 as b2
import pandas as pd
import requests
from deepface import DeepFace
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from dotenv import load_dotenv

from apps.attendance.models import AttendanceModel
from apps.authentication.models import StudentModel, TeacherModel

info = b2.InMemoryAccountInfo()
load_dotenv()
b2_api = b2.B2Api(info)

APPLICATION_KEY_ID = os.getenv("B2_KEY_ID")
APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
DATASET_DB_PATH = os.getenv("DATASET_DB_PATH")
MOODLE_URL = os.getenv("MOODLE_URL")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")
FRONTEND_URL = os.getenv("FRONTEND_URL")
LIBRARY_URL = os.getenv("LIBRARY_URL")


@csrf_exempt
def compareFace(request):
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
            print("the file path is ", file_path)

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

                    context = request.session.get("attendance_context", {})
                    attendance_id = context.get("attendance_id")
                    course_id = context.get("course_id")
                    teacherid = context.get("teacherid")
                    statuses = context.get("statuses")
                    sessionid = context.get("sessionid")

                    present_id = 0
                    for status in statuses:
                        if status['acronym'] == 'P':
                            present_id = status['id']

                    all_statuses = ",".join(str(status) for status in context.get("statuses"))
                    mark_attendance_url = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=mod_attendance_update_user_status&moodlewsrestformat=json"

                    student = StudentModel.objects.all().filter(student_id=int(matched_faces[0])).first()
                    print("MARKING ATTENDANCE FOR: ", student)

                    data = {
                        "sessionid": sessionid,
                        "studentid": student.moodle_id,
                        "takenbyid": teacherid,
                        "statusid": present_id,
                        "statusset": all_statuses
                    }

                    mark_attendance_response = requests.post(mark_attendance_url, data=data)
                    if mark_attendance_response.json() is None:

                        attendance = AttendanceModel(
                            student_id=student,
                            course_id=course_id,
                            session_id=sessionid,
                            date_of_attendance=timezone.now()
                        )

                        attendance.save()

                        return JsonResponse({
                            "message": "True",
                            "matched_person_names": matched_faces,
                        })
                    else:
                        print("MOODLE RESPONSE:", mark_attendance_response)
                        return JsonResponse({
                            "error": "Error while marking attendance for you in Moodle"
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


@csrf_exempt
def compareFaceWithoutAttendance(request):
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
            print("the file path is ", file_path)

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
                    return JsonResponse({
                        "matched": matched_faces
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


@ensure_csrf_cookie
def getCompareFace(request, sessionid, coursename, teacherid):
    if request.method == "GET":
        getSessionInfoUrl = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=mod_attendance_get_session&moodlewsrestformat=json"
        getSessionInfoData: dict = {
            "sessionid": sessionid
        }
        getSessionInfoResponse = requests.post(getSessionInfoUrl, data=getSessionInfoData)
        print(getSessionInfoResponse.json())
        status = [
            {
                "id": s["id"],
                "acronym": s["acronym"],

            }
            for s in getSessionInfoResponse.json().get("statuses")
        ]

        context = {
            "statuses": status,
            "attendance_id": getSessionInfoResponse.json().get("attendanceid"),
            "course_id": getSessionInfoResponse.json().get("courseid"),
            "sessionid": sessionid,
            "course_name": coursename,
            "teacherid": teacherid,
        }
        print("Frontend", FRONTEND_URL)
        request.session['attendance_context'] = context
        return render(request, "compare_face.html", context)

    return None


@ensure_csrf_cookie
def registerFace(request):
    if request.method == "GET":
        return render(request, 'register_face.html')

    if request.method == "POST":
        image_data = request.FILES.get("image")
        user_id = request.POST.get("user-id")
        user_name = request.POST.get("user-name")
        user_email = request.POST.get("user-email")
        user_type = request.POST.get("user-type").lower()

        # Input validation
        if not all([image_data, user_id, user_name, user_email, user_type]):
            return JsonResponse({
                "message": "Missing required fields"
            }, status=400)

        if user_type == "teacher":
            # check in teacher table
            if TeacherModel.objects.filter(teacher_id=user_id).exists():
                return JsonResponse({
                    "message": "This teacher already exists"
                }, status=400)
        else:
            # check in student table if exist
            if StudentModel.objects.filter(student_id=user_id).exists():
                return JsonResponse({
                    "message": "This student already exists"
                }, status=400)

        print("DATA RECEIVED BY REQUEST : ", user_id, user_name)

        if image_data:
            # Save image to temporary storage
            file_path = default_storage.save("static/dataset/" + user_id + ".jpeg", image_data)
            file_name = user_id + ".jpeg"

            # Prepare Moodle API call
            moodle_url = MOODLE_URL + "?wstoken=" + MOODLE_TOKEN + "&wsfunction=core_user_create_users&moodlewsrestformat=json"

            print(moodle_url)

            # Handle name splitting more safely
            name_parts = user_name.split(" ")
            firstname = name_parts[0]
            lastname = name_parts[1] if len(name_parts) > 1 else ""

            data = {
                "users[0][username]": firstname.lower(),
                "users[0][password]": "Nokian876@" + user_id,
                "users[0][firstname]": firstname,
                "users[0][lastname]": lastname,
                "users[0][email]": user_email,
                "users[0][auth]": "manual",
                "users[0][lang]": "en",
                "users[0][timezone]": "Asia/Hong_Kong"
            }
            print(data)

            try:
                response = requests.post(moodle_url, data=data)

                # Printing the response
                print("MOODLE RESPONSE STATUS ", response.status_code)
                print("MOODLE RESPONSE TEXT ", response.text)

                response_data = response.json()

                # Check if Moodle API call was successful
                if response.status_code != 200 or "exception" in response_data:
                    return JsonResponse({
                        "message": "Failed to register user in Moodle",
                        "moodle_error": response_data
                    }, status=400)

                USERNAME = response_data[0]["username"]
                MOODLE_ID = response_data[0]["id"]

                try:
                    if user_type == "teacher":
                        teacher = TeacherModel(
                            teacher_id=user_id,
                            teacher_name=user_name,
                            teacher_email=user_email,
                            moodle_id=MOODLE_ID,
                            photo_path=file_path
                        )
                        teacher.save()

                        # Return teacher information
                        return JsonResponse({
                            "teacher_id": teacher.teacher_id,
                            "teacher_name": teacher.teacher_name,
                            "moodle_id": teacher.moodle_id,
                            "username": USERNAME,
                            "message": "Teacher registered successfully"
                        }, status=200)
                    else:
                        student = StudentModel(
                            student_id=user_id,
                            moodle_id=MOODLE_ID,
                            student_email=user_email,
                            student_name=user_name,
                            photo_path=file_name
                        )
                        student.save()

                        # Library API call for students only
                        lib_url = LIBRARY_URL + "/admin/users/create"
                        lib_payload = {
                            "username": str(USERNAME),
                            "moodle_id": str(MOODLE_ID),
                            "student_id": str(user_id),
                            "role": "USER"
                        }
                        lib_response = requests.post(lib_url, json=lib_payload)
                        print(lib_payload)
                        print(lib_response.text)

                        # Return student information
                        return JsonResponse({
                            "student_id": student.student_id,
                            "student_name": student.student_name,
                            "moodle_id": student.moodle_id,
                            "username": USERNAME,
                            "message": "Student registered successfully"
                        }, status=200)

                except Exception as e:
                    print(f"Database save error: {e}")
                    return JsonResponse({
                        "message": "Failed to save user to database",
                        "error": str(e)
                    }, status=500)

            except Exception as e:
                print(f"Moodle API error: {e}")
                return JsonResponse({
                    "message": "An error occurred while calling Moodle API",
                    "error": str(e)
                }, status=500)

        return JsonResponse({
            "message": "No image data provided"
        }, status=400)

    return JsonResponse({
        "message": "Method not allowed"
    }, status=405)


@csrf_exempt
def compareFaceWithoutAttendancePortal(request):
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
            print("the file path is ", file_path)

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
                    student = StudentModel.objects.filter(student_id=matched_faces[0]).first()

                    if student :
                        res = {
                            "id": student.student_id,
                            "name": student.student_name,
                            "moodle_id": student.moodle_id
                        }
                        print(f"Matched faces: {matched_faces}")
                        return JsonResponse(res)
                    else :
                        print("student does not exist in database")
                        return JsonResponse({
                            "error" : "student does not exist in database"
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


@csrf_exempt
def compareFaceWithoutAttendancePortalTeacher(request):
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            file_path = default_storage.save("static/temp_storage/comparable_photo.jpeg", image_data)
            print("the file path is ", file_path)

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
                    teacher = TeacherModel.objects.filter(teacher_id=matched_faces[0]).first()
                    if teacher:
                        res = {
                            "id": teacher.teacher_id,
                            "name": teacher.teacher_name,
                            "moodle_id": teacher.moodle_id
                        }
                        print(f"Matched faces: {matched_faces}")
                        return JsonResponse(res)
                    else:
                        print("teacher does not exist in database")
                        return JsonResponse({
                            "message" : "teacher does not exist in database"
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

