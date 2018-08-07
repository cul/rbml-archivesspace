import json
import requests
import csv
import secrets
import time
import uuid

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

#create a dictionary with all the default user creds, in this case view permissions for all four repos
#NB password is in the URL

defaultUser = {"jsonmodel_type": "user",
		"department": "rbml",
		"is_admin": False,
		#"username": "test person",
		#"name": "Test Person",
		"permissions": {"/repositories/5": ["view_suppressed", "view_repository"], "/repositories/4": ["view_suppressed", "view_repository"], "_archivesspace": [], "/repositories/3": ["view_repository"], "/repositories/2": ["view_suppressed", "view_repository"]}}

#iterate over a series of unis and names

with open('input_users.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
		uni = row[0]
		name = row[1]
		
        # append uni and name to default user object
		defaultUser['username'] = uni
		defaultUser['name'] = name
   		
        #prepare for posting
		newUserjson = json.dumps(defaultUser)

		#generate a hex string for a password
		pw = uuid.uuid4().hex.upper()[0:10]

		#post
		createUser = requests.post(baseURL+'/users?password='+pw,headers=headers,data=newUserjson).json

		#report
		print createUser, uni, name, pw
