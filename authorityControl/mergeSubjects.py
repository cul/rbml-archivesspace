import json
import requests
import secretsTest
import time
import csv

startTime = time.time()

#call secrets for authentication
baseURL = secretsTest.baseURL
user = secretsTest.user
password = secretsTest.password
 
#authenticate session
auth = requests.post(baseURL +
'/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

# loops through csv listing target and victims by AS ID, (e.g. 73, 244 | 72,78 | 523,859 ), creating a json object for submission for each
#filename = input('Enter filename listing targets and victims:')
endpoint = '//merge_requests/subject'
with open('inputSubjectsMerge.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='|', quotechar='"')
        for row in reader:
        	#take target AS ID from row 1
        	t = {}
        	t['ref'] = row[1].strip()
        	#take victim 1 AS ID from row 2
        	v = {}
        	v ['ref'] = row[2].strip()
        	#create record	
        	record = {}
        	record['target'] = t
        	record['victims'] = [v]
        	record = json.dumps(record)
        	#print record
        	#syntax: record = '{"target" : {"ref": "/subjects/3"}, "victims": [{ "ref": "/subjects/123" }]}'
        	output = requests.post(baseURL + endpoint, headers=headers, data=record).json()
        	print row [0], output, record

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
