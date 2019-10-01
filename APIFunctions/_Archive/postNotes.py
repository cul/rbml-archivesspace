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

#create a dict with all the notes contents
#to do : abstract and document this to make entering notes easier
noteContents = [{'content': 'Material is unprocessed. Please contact rbml@columbia.edu for more information.', 'publish': True, 'jsonmodel_type': 'note_text'}]
localStatus = {'local_access_restriction_type': ['AVAILABLE']}
wholeNote = {'rights_restriction': localStatus, 'subnotes': noteContents, 'jsonmodel_type': 'note_multipart', 'publish': True, 'label': ' Restrictions on Access', 'type': 'accessrestrict'}

note2Contents = [{'content': 'Collection-level record describing unprocessed material made public in summer 2018 as part of the Hidden Collections initiative.', 'publish': True, 'jsonmodel_type': 'note_text'}]
whole2Note = {'subnotes': note2Contents, 'jsonmodel_type': 'note_multipart', 'publish': True, 'label': 'Processing Information', 'type': 'processinfo'}


print wholeNote, whole2Note
print "Is set to dev if URL contains dev:", baseURL
#print "This script will read list of AS IDs from input_AS_ids.csv and add the note above. Press any key to continue, Ctrl-C to abort."
#raw_input("Press Enter to continue...")


with open('input_AS_ids.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        ASID = row[0]
        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(baseURL+ASID,headers=headers).json()

        # use this function to search inside notes list and return the index of first access subnote, so below we can insert the new one before it
        def getIndex():
            i = 0
            for i in range(len(archival_object_json['notes'])):
                if 'accessrestrict' in archival_object_json['notes'][i].values():
                    return i
                    break

        #test for null index return and arbitrarily put it third
        noteIndex = getIndex()
        if noteIndex is None:
            noteIndex = 3

        #insert new note above into the right place in the notes list, before the existing access notes
        archival_object_json['notes'].insert(noteIndex,wholeNote)

	#insert processing note after new access note
	archival_object_json['notes'].insert(noteIndex+1,whole2Note)

          #prepare for repost
        archival_object_data = json.dumps(archival_object_json)

          # Repost the archival object containing the new note
        archival_object_update = requests.post(baseURL+ASID,headers=headers,data=archival_object_data).json()
        print archival_object_update


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
