import json
import requests
import csv
import secrets

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

# loop through list of bib IDs
with open('input_bib_ids.csv', 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		bibID = row[0]

	#GET request to search on bibID, limited to resources. 
	#remember to set repository in string - 2 is RBML, default here

		search = requests.get(baseURL+'/repositories/2/search?q='+str(bibID)+'&type[]=resource&page=1',headers=headers).json()
	# test to make sure only one result is returned and that the bib ID is the identifier; if not, throw error and go to next search
		if (search['total_hits'] == 1) and (search['results'][0]['identifier'] ==  str(bibID)):
	    	#if the bib ID is confirmed, grab the ref ID 
	    	#this can definitely be improved; searching only for identifier in the search above would help
	    		archival_object_uri = search['results'][0]['uri']
			print archival_object_uri, " equals ", bibID

		else:
			if search['total_hits'] == 0:
				print "Bib ID", bibID, "not found."

			else: 
				print "Bib ID", bibID, "not unique, ",  search['total_hits'], "hits were found."

