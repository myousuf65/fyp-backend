import requests


url  = "http://172.104.186.148/moodle/webservice/rest/server.php?wstoken=a24678df4df3db2a34ce6f4ac22d6de7&wsfunction=mod_attendance_get_session&moodlewsrestformat=json"

data = {
    "sessionid"  : 476
}


response = requests.post(url,data=data)

print(response.json())
