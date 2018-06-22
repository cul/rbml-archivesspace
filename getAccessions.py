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

print 'To parse output, use jq as follows:'
print "This pulls out only the objects with empty related resources records"
print "jq -c '.[]' rbmlaccessions.json | grep 'related_resources':\[]'"
print "This pulls out the notes field for accessions without related resources"
print "jq -c '.[]' rbmlaccessions.json | grep \"related_resources\":\[]' | jq '.[\"general_note\"]'"
print "This pulls out the bib ID  for accessions without related resources"
print "jq -c '.[]' rbmlaccessions.json | grep 'related_resources':\[]' | jq '.[\"user_defined::integer_1\"]'"

#define the API call to get a list of all agent IDs
endpoint = '//repositories/2/accessions?all_ids=true'

#call the API
ids = requests.get(baseURL + endpoint, headers=headers).json()

#iterate over each returned ID, grabbing the json object
#if downloading accessions from non-RBML repo, change the repo number below in the endpoint
records = []
for id in ids:
    endpoint = '//repositories/2/accessions/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    records.append(output)
    # print output
f=open('rbmlaccessions.json', 'w')
json.dump(records, f)
f.close()

print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)

