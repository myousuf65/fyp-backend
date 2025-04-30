# Create your views here.
from datetime import datetime
import os
import pytz

import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from dotenv import load_dotenv
from flask import session

from apps.attendance.views import MOODLE_URL, FRONTEND_URL

load_dotenv()

MOODLE_URL = os.getenv('MOODLE_URL')
MOODLE_TOKEN = os.getenv('MOODLE_TOKEN')
FRONTEND_URL= os.getenv("FRONTEND_URL")



@ensure_csrf_cookie
def teacherLogin(request):
    if request.method == "GET":
        # Get any messages passed from a failed POST attempt
        message = request.GET.get('message', '')
        return render(request, 'teacherLogin.html', {'message': message})

    if request.method == "POST":
        username: str = request.POST.get("username")
        password: str = request.POST.get("password")

        getUserInfoUrl: str = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=core_user_get_users&moodlewsrestformat=json&criteria[0][key]=&criteria[0][value]="

        getUserInfoResponse = requests.get(getUserInfoUrl)

        allusers: list[dict] = getUserInfoResponse.json()['users']

        for user in allusers:
            # find that user
            if user["username"] == username:
                email: str = user["email"]
                id: int = user["id"]

                # see if the user is a teacher
                if "teacher" in email:
                    getTeacherSessionUrl: str = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=mod_attendance_get_courses_with_today_sessions&moodlewsrestformat=json"

                    getUserInfoData: dict = {
                        "userid": id
                    }
                    getTeacherSessionResponse = requests.post(getTeacherSessionUrl, data=getUserInfoData)
                    print(getTeacherSessionResponse.status_code)
                    print(getTeacherSessionResponse.json())

                    context = {
                        "courses" : getTeacherSessionResponse.json(),
                        "teacherid" : id,
                        "frontend_url" : FRONTEND_URL
                    }
                    return render(request, 'teacherLessons.html', context)
            # User found but not a teacher
        return redirect(reverse("teacherLogin") + "?message=Authentication failed: You are not registered as a teacher")
        # no user found at all
    return redirect(reverse("teacherLogin") + "?message=Authentication failed: Invalid username or password")
