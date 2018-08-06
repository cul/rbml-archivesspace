import json
import requests
import csv
import secretsDev
import time

#call secrets for authentication
baseURL = secretsDev.baseURL
user = secretsDev.user
password = secretsDev.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

#create a dict with all the user contents
#password is defined in the URL

newUser = {"jsonmodel_type": "user",
"department": "rbml",
"is_admin": False,
"username": "test person",
"name": "Test Person",
"permissions": {"/repositories/5": ["view_suppressed", "view_repository"], "/repositories/4": ["view_suppressed", "view_repository"], "_archivesspace": [], "/repositories/3": ["view_repository"], "/repositories/2": ["view_suppressed", "view_repository"]}}

#with open('input_users.csv', 'rb') as csvfile:
#    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
 #   for row in reader:
  #      uni = row[0]
        # For update: Submit a get request for the archival object and store the JSON
        # archival_object_json = requests.get(baseURL+ASID,headers=headers).json()

          #prepare for repost
   #     archival_object_data = json.dumps(archival_object_json)

          # Repost the archival object containing the new note
newUserjson = json.dumps(newUser)

#to do - abstract this to generate the URL with passwords
#to do - loop through csv with unis and usernames

createUser = requests.post(baseURL+'users?password=COWUV',headers=headers,data=newUserjson).json
print createUser
