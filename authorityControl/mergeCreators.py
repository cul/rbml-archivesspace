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
auth = requests.post(baseURL +
'/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

#define the API call to get a list of all agent IDs
#endpoint = '//agents/people?all_ids=true'
#call the API
#ids = requests.get(baseURL + endpoint, headers=headers).json()

id_target = input('Enter target (lc-containing) agent id: ')
id_victim = input('Enter victim (to be destroyed) agent id: ')

#use user-entered ID to get object

target_endpoint = '//agents/people/'+str(id_target)
target_output = requests.get(baseURL + target_endpoint, headers=headers).json()

victim_endpoint = '//agents/people/'+str(id_victim)
victim_output = requests.get(baseURL + victim_endpoint, headers=headers).json()

print target_output
print victim_output

#endpoint = '//merge_requests/agent'

#mash together the target and victim records from above
#record =

#output = requests.post(baseURL + endpoint, headers=headers, data=record).json()
#print output


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)