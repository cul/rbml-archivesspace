import json
import requests
import secrets
import time
import csv

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

# need to loop through csv listing target and victim groups, creating a json object for submission for each
#filename = input('Enter filename listing targets and victims:')
endpoint = '//merge_requests/agent'
with open('input.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
        	t = {}
        	t['target'] = {}
        	t['target']['ref'] = '/agents/people/' + row[0]
        	v1 = {}
        	v1['victims'] = {}
        	v1['ref'] = '/agents/people/' + row[1]
        	#put in test for v2; if row[2] is not blank, create v2 dict
        	#combine them into one dict, convert to json object
        	
        	#works: record = '{"target" : {"ref": "/agents/people/3"}, "victims": [{ "ref": "/agents/people/102" }]}'
        	#output = requests.post(baseURL + endpoint, headers=headers, data=record).json()
        	#print record, output


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)