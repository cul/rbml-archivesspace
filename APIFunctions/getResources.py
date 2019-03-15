import json
import requests
import secrets
import time

startTime = time.time()

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

print 'This script will call all resources for a given repository and write it to a file names resource.json.'
repo = raw_input("Enter repo ID; 2=RBML, 3=Avery, 4=Starr, 5=Burke:")

#define the API call to get a list of all resource IDs
endpoint = '//repositories/' + repo + '/resources?all_ids=true'

#call the API
ids = requests.get(baseURL + endpoint, headers=headers).json()

#iterate over each returned ID, grabbing the json object
records = []
for id in ids:
    endpoint = '//repositories/' + repo + '/resources/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    records.append(output)
    # print output
f=open('resources.json', 'w')
json.dump(records, f)
f.close()


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
