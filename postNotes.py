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

#create a dict with all the notes contents
#to do : abstract and document this to make entering notes easier
noteContents = [{'content': 'This is my new note. DEREK JETER.', 'publish': True, 'jsonmodel_type': 'note_text'}]
localStatus = {'local_access_restriction_type': ['Available']}
wholeNote = {'rights_restriction': localStatus, 'subnotes': noteContents, 'jsonmodel_type': 'note_multipart', 'publish': True, 'label': ' Restrictions on Access', 'type': 'accessrestrict'}

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

          #prepare for repost
        archival_object_data = json.dumps(archival_object_json)
          # Repost the archival object containing the new note
        archival_object_update = requests.post(baseURL+ASID,headers=headers,data=archival_object_data).json()
        print archival_object_update
