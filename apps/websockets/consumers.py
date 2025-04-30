import os

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
import json
from uuid import uuid4
from apps.attendance.models import AttendanceModel, CourseRegistartionModel
from dotenv import load_dotenv
import requests

load_dotenv()

MOODLE_URL = os.getenv("MOODLE_URL")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")



class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.username = str(uuid4())  # Unique username per connection
        self.sessionid = self.scope["url_route"]["kwargs"]["session_id"]  # Room name from URL

        print("Got connection")
        self.accept()

        getSessionInfoUrl = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&wsfunction=mod_attendance_get_session&moodlewsrestformat=json"

        getSessionInfoData:dict = {
            "sessionid": self.sessionid
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


        print("==========All Students In Class: ===============")
        print(all_students_in_class)
        print("================================================")

        print("==========All Attendance: =============")
        print(attendance_log)
        print("=======================================")

        # Add the WebSocket to the group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_add)(
            self.sessionid,
            self.channel_name,  # Channel name is unique to each WebSocket connection
        )

        # Send a welcome message with the attendance data
        self.send(
            text_data=json.dumps(
                {
                    "message": f"Welcome {self.username}!",
                    "username": self.username,
                    "attendance": attendance_log,  # Send serialized attendance data
                    "students": all_students_in_class,
                    "statuses" : status,
                    "courseid" : courseid,
                    "description" : description
                }
            )
        )

    def receive(self, text_data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            self.sessionid,
            {
                "type": "chat_message",
                "message": text_data,
                "username": self.username,
                "channel_name": self.channel_name,
            },
        )

    def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        self.send(
            text_data=json.dumps({"message": message, "username": username})
        )

    def new_attendance(self, event):
        """Handle updated attendance and broadcast to WebSocket."""
        self.send(
            text_data=json.dumps(
                {
                    "message": f"Update {self.username}!",
                    "username": self.username,
                    "attendance": event["attendance_log"],
                    "students": event["students"],
                    "statuses": event["statuses"],
                    "courseid": event["courseid"],
                    "description": event["description"],
                }
            )
        )

    def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_discard)(self.sessionid, self.channel_name)
