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
with open('input_merge_subjects.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='|', quotechar='"')
        for row in reader:
        	#take target AS ID from row 1
        	t = {}
        	t['ref'] = row[1].strip()
        	#take victim 1 AS ID from row 2
        	victimList = []
		v = {}
        	v ['ref'] = row[2].strip()
		victimList.append(v)
        	#test for additional victim AS IDs in additional rows; if exists, update list
        	if row[3] != "":
        		v2 = {}
        		v2['ref'] = row[3].strip()
        		victimList.append(v2)
		
		if row[4] != "":
			v3 = {}
			v3['ref'] = row[4].strip()
			victimList.append(v3)

		if row[5] != "":
			v4 = {}
			v4['ref'] = row[5].strip()
			victimList.append(v4)

		if row[6] != "":
			v5 = {}
			v5['ref'] = row[6].strip()
			victimList.append(v5)

		if row[7] != "":
			v6 = {}
			v6['ref'] = row[7].strip()
			victimList.append(v6)

		if row[8] != "":
			v7 = {}
			v7['ref'] = row[8].strip()
			victimList.append(v7)

		if row[9] != "":
			v8 = {}
			v8['ref'] = row[9].strip()
			victimList.append(v8)

		if row[10] != "":
			v9 = {}
			v9['ref'] = row[10].strip()
			victimList.append(v9)

        	#create record	
        	record = {}
        	record['target'] = t
        	record['victims'] = victimList
        	record = json.dumps(record)
        	#print record
        	#syntax: record = '{"target" : {"ref": "/subjects/3"}, "victims": [{ "ref": "/subjects/123" }]}'
        	output = requests.post(baseURL + endpoint, headers=headers, data=record).json()
        	print row [0], output, record

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
