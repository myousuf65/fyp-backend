from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
import json
from uuid import uuid4
from apps.attendance.models import AttendanceModel, CourseRegistartionModel


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.username = str(uuid4())  # Unique username per connection
        self.room = self.scope["url_route"]["kwargs"]["room_name"]  # Room name from URL

        print("Got connection")
        self.accept()

        # Query the database normally using Django ORM
        attendance_queryset = AttendanceModel.objects.filter(course_id=1)
        all_attendance = [
            {
                "student_name": attendance.student_id.student_name
            }
            for attendance in attendance_queryset
        ]

        students_queryset = CourseRegistartionModel.objects.filter(course_id=1)

        all_students = [
            {
                "student_name": student.student_id.student_name
            }
            for student in students_queryset
        ]

        print("==========All Students: ===============")
        print(all_students)
        print("=======================================")

        print("==========All Attendance: =============")
        print(all_attendance)
        print("=======================================")

        # Add the WebSocket to the group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_add)(
            self.room,
            self.channel_name,  # Channel name is unique to each WebSocket connection
        )

        # Send a welcome message with the attendance data
        self.send(
            text_data=json.dumps(
                {
                    "message": f"Welcome {self.username}!",
                    "username": self.username,
                    "attendance": all_attendance,  # Send serialized attendance data
                    "students": all_students
                }
            )
        )

    def receive(self, text_data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            self.room,
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
        data = event['data']
        print(f"Received new attendance data: {data}")

        students_queryset = CourseRegistartionModel.objects.filter(course_id=1)

        all_students = [
            {
                "student_name": student.student_id.student_name
            }
            for student in students_queryset
        ]

        self.send(text_data=json.dumps({
            "message": f"Welcome {self.username}!",
            "username": self.username,
            "attendance": data,
            "students": all_students
        }))

    def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_discard)(self.room, self.channel_name)
