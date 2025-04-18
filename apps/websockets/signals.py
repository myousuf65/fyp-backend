from channels.layers import get_channel_layer
from django.dispatch import receiver
from django.db.models.signals import post_save
from asgiref.sync import async_to_sync
from apps.attendance.models import AttendanceModel

@receiver(post_save, sender=AttendanceModel)
def attendance_marked(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    if not channel_layer:
        print("Channel layer is not configured.")
        return

    room_name = "AP"  # Make sure this matches the WebSocket room name
    try:
        attendance_queryset = AttendanceModel.objects.filter(course_id=1)
        all_attendance = [
            {
                "student_name": attendance.student_id.student_name
            }
            for attendance in attendance_queryset
        ]

        message = {
            "type": "new_attendance",  # Matches `new_attendance` in consumer
            "data": all_attendance,
        }

        print(f"Sending message to group: {room_name}, data: {message}")
        async_to_sync(channel_layer.group_send)(room_name, message)
    except Exception as e:
        print(f"Error in attendance_marked signal: {str(e)}")
