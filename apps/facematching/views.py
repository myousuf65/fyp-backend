from deepface import DeepFace 
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import ensure_csrf_cookie
from deepface import DeepFace

def matchFace(request):
    if request.method == "POST":
        image_data = request.FILES.get("image")
        if image_data:
            # Optionally, save the file or process it
            # For example, you can save the file using Django's default file storage
            
            file_path = default_storage.save("static/temp_storage/uploaded_photo.jpeg", image_data)
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
def showHtml(request):
    return render(request, 'test.html')

