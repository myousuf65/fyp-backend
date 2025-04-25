import requests


url  = "http://172.104.186.148/moodle/webservice/rest/server.php?wstoken=a24678df4df3db2a34ce6f4ac22d6de7&wsfunction=mod_attendance_update_user_status&moodlewsrestformat=json"

context = {'attendance_id': 37,
           'course_id': 11,
           'course_name': ' CSCI361 Cryptography and Secure Applications',
           'sessionid': 978,
           'statuses': [{'acronym': 'P','id': 149},
                        {'acronym': 'L', 'id': 151},
                        {'acronym': 'E', 'id': 152},
                        {'acronym': 'A', 'id': 150}],
           'teacherid': 33}

all_statuses = context.get("statuses")
cleaned_stat = ",".join (str(status['id']) for status in all_statuses)


id = 0;

for status in all_statuses:
    if status['acronym'] == 'P':
        id = status['id']

print(id)


# data = {
#     "sessionid"  : 978,
#     "studentid" : 4,
#     "takenbyid" : 2,
#     "statusid" : 149,
#     "statusset" : cleaned_stat
# }


# response = requests.post(url,data=data)

# print(response.json())
