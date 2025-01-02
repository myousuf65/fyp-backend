from deepface import DeepFace
import pandas as pd 

# result = DeepFace.find(
#     img_path="/Users/ypathan/dev/fyp/backend/static/temp_storage/register_photo.jpeg",
#     db_path="/Users/ypathan/dev/fyp/backend/static/dataset"
# )
# print("-------")
# try:
#     print(result[0]['identity'][0])
#     pass
# except KeyError:
#     print("your face is not here")
# print("-------")


test = "/Users/ypathan/dev/fyp/backend/static/dataset/yousuf_pathan.jpeg"
print(test.split("/")[-1].replace(".jpeg", ""))
