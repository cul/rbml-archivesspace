import json
import requests
import csv
import secretsDev

#call secrets for authentication
baseURL = secretsDev.baseURL
user = secretsDev.user
password = secretsDev.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

print "Is set to dev if URL contains dev:", baseURL
print "This script will read list of AS IDs from input_AS_ids.csv and add the specified note. Press any key to continue, Ctrl-C to abort."
raw_input("Press Enter to continue...")

with open('input_AS_ids.csv', 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		ASID = row[0]
    # Submit a get request for the archival object and store the JSON
		archival_object_json = requests.get(baseURL+ASID,headers=headers).json()
    # Add the new repository_processing_note to the existing archival object record. NB this will overwrite the existing note.
#		archival_object_json['repository_processing_note'] = "This is the text of the newly added note. Paul O'Neill."
#		archival_object_data = json.dumps(archival_object_json)
		#print archival_object_data
    # Repost the archival object containing the new note
		#archival_object_update = requests.post(baseURL+ASID,headers=headers,data=archival_object_data).json()
    		#print archival_object_update
