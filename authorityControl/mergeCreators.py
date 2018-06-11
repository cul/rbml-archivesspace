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

# loops through csv listing target and one or two victims, by AS ID, (e.g. 73, 244, 345 | 72,78, | 523,859,845 ), creating a json object for submission for each
#filename = input('Enter filename listing targets and victims:')
#define agent type here and in refs; could add test for corporations and families if needed
endpoint = '//merge_requests/agent'
with open('input.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
        	#take target AS ID from row 0
        	t = {}
        	t = {}
        	t['ref'] = '/agents/people/' + row[0]
        	#take victim 1 AS ID from row 1
        	v1 = {}
        	v1['ref'] = '/agents/people/' + row[1]
        	victimList = [v1]
        	#test for second victim AS ID in row 2; if exists, update list
        	if row[2] != "":
        		v2 = {}
        		v2['ref'] = '/agents/people/' + row[2]
        		victimList = [v1,v2]
        	#create record	
        	record = {}
        	record['target'] = t
        	record['victims'] = victimList
        	record = json.dumps(record)
        	#print record
        	#syntax: record = '{"target" : {"ref": "/agents/people/3"}, "victims": [{ "ref": "/agents/people/102" }]}'
        	output = requests.post(baseURL + endpoint, headers=headers, data=record).json()
        	print output, record

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)