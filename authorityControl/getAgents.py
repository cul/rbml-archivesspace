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

#define the API call to get a list of all agent IDs
endpoint = '//agents/people?all_ids=true'

#call the API
ids = requests.get(baseURL + endpoint, headers=headers).json()

#iterate over each returned ID, grabbing the json object
records = []
for id in ids:
    endpoint = '//agents/people/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    records.append(output)
    #print output
f=open('agentsPeople.json', 'w')
json.dump(records, f)
f.close()

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)