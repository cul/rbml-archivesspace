import json
import requests
import secretsTest
import time

startTime = time.time()

#call secrets for authentication
baseURL = secretsTest.baseURL
user = secretsTest.user
password = secretsTest.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

#define the API call to get a list of all subject IDs
endpoint = '//subjects?all_ids=true'

#call the API
ids = requests.get(baseURL + endpoint, headers=headers).json()

#iterate over each returned ID, grabbing the json object
records = []
for id in ids:
    endpoint = '//subjects/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    records.append(output)
f=open('subjects.json', 'w')
json.dump(records, f)
f.close()

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
