from deepface import DeepFace 
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import ensure_csrf_cookie


def matchFace(request):
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            # Optionally, save the file or process it
            # For example, you can save the file using Django's default file storage
            file_path = default_storage.save("uploaded_photo.jpeg", image_data)
            print(f"File saved at: {file_path}")

            # Return a response indicating success
            return JsonResponse({"message": "Image uploaded successfully!"})

        else:
            return JsonResponse({"error": "No image found in the request"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@ensure_csrf_cookie
def showHtml(request):
    return render(request, 'test.html')

