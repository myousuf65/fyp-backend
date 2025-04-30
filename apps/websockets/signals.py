from channels.layers import get_channel_layer
from django.dispatch import receiver
from django.db.models.signals import post_save
from asgiref.sync import async_to_sync
from apps.attendance.models import AttendanceModel
import requests
from dotenv import load_dotenv
import os


load_dotenv()

MOODLE_URL = os.getenv("MOODLE_URL")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")


@receiver(post_save, sender=AttendanceModel)
def attendance_marked(sender, instance,created, **kwargs):
    channel_layer = get_channel_layer()
    if not channel_layer:
        print("Channel layer is not configured.")
        return

    # make request to moodle to fetch session info
    room_name = str(instance.session_id)
    getSessionInfoUrl = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=mod_attendance_get_session&moodlewsrestformat=json"

    getSessionInfoData:dict = {
        "sessionid": instance.session_id
    }

    response = requests.post(getSessionInfoUrl,data=getSessionInfoData)
    print(response.json())


    sessionInfoResponse = response.json()
    all_students_in_class = sessionInfoResponse['users']
    attendance_log = sessionInfoResponse['attendance_log']
    status = [
        {
            "id":   s["id"],
            "acronym" : s["acronym"],

        }
        for s in sessionInfoResponse.get("statuses")
    ]
    description = sessionInfoResponse['description']
    courseid = sessionInfoResponse['courseid']



    try:

        message = {
            "type": "new_attendance",  # Matches `new_attendance` in consumer
            "attendance_log": attendance_log ,
            "students": all_students_in_class,
            "statuses" : status,
            "description" : description,
            "courseid" : courseid,
        }

        print(f"Sending message to group: {room_name}, data: {message}")
        async_to_sync(channel_layer.group_send)(room_name, message)
    except Exception as e:
        print(f"Error in attendance_marked signal: {str(e)}")
