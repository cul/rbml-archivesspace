import json
import requests
import csv
import secrets
import time

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

startTime = time.time()

print "This script will read AS ids from input_AS_PDF_URLS_ids.csv and add a link to a finding aid as well as add/append a finding aid note to the json and repost"
print "The two-column csv input file syntax is: /repositories/101/resources/1, http://www.change.org"
print "Is set to dev if URL contains dev:", baseURL
raw_input("Press Enter to continue...")

with open('input_AS_PDF_URLS_ids.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        ASID = row[0]
        URLtoADD = row[1]
        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(baseURL+ASID,headers=headers).json()    

        #insert URL to json object  
        archival_object_json['ead_location'] = URLtoADD

        #insert finding aid note. check for existing finding aid note, and append if exists
        if 'finding_aid_note' in archival_object_json:
            existing_note = archival_object_json['finding_aid_note']
            archival_object_json['finding_aid_note'] = existing_note + ' Link to PDF finding aid added in fall 2018'

        else:
            archival_object_json['finding_aid_note'] = 'Link to PDF finding aid added in fall 2018'

        #prepare for repost
        archival_object_data = json.dumps(archival_object_json)
        #print archival_object_data

        #Repost the archival object containing the new note
        archival_object_update = requests.post(baseURL+ASID,headers=headers,data=archival_object_data).json()
        print archival_object_update


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
