import json
import requests
import secrets
import codecs
import os.path

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

print "This script will create a text suitable for a deposit-info.txt file."
path = raw_input("Enter path to save file, e.g. /media/sf_Virtualshared/. Leave blank for default path: ")
repo = raw_input("Enter repo ID; 2=RBML, 3=Avery, 4=Starr, 5= Burke: ")
accession = raw_input("Enter accession ID: ")

#define the API call to get the accession
endpoint = '/repositories/' + repo + '/accessions/' + accession

#call the API
output = requests.get(baseURL + endpoint, headers=headers).json()

#get accession number first, so we can write it to the filename
#test for fourth field in identifier so we can parse old accession number
if 'id_3' in output:
	accessionNumber = output['id_0'] + "-" +  output['id_1'] + "-" + output['id_2'] + "-" + output['id_3']
else:
	accessionNumber = output['id_0'] + "-" +  output['id_1'] + "-" + output['id_2']

fileandpath = os.path.join(path + 'deposit-info_' + accessionNumber + '.txt')

f=codecs.open(fileandpath, 'w', 'utf-8')
f.write("Collection Name: " + output['title'] + '\n')
f.write("Date Received: " + output['accession_date'] + '\n')
f.write("Bib ID of Collection: " + output['user_defined']['integer_1'] + '\n')
f.write("Accession Number: " + accessionNumber + '\n')
if 'content_description' in output:
	f.write("Description: " + output['content_description'] + '\n')
else:
	f.write("Description: NOT ENTERED" + '\n')

if 'container_summary' in output['extents'][0]:
	f.write("Size: " + output['extents'][0]['container_summary'] + ' (' + output['extents'][0]['number'] + ' ' + output['extents'][0]['extent_type'] + ')'+ '\n')
else:
	f.write("Size: " + output['extents'][0]['number'] + ' ' + output['extents'][0]['extent_type'] + '\n')


if "[NEW]" in output['title']: 
	newadd = 'New'
if "[ADD]" in output['title']:
	newadd = 'Addition'
else:
	newadd = 'Check title for [NEW] or [ADD]'
f.write("New Collection or Addition: " + newadd + '\n')
if 'text_2' in output['user_defined']: 
	f.write("Source of Acquisition: " + output['user_defined']['text_2'] + '\n')
else:
	f.write("Source of Acquisition: NOT ENTERED" + '\n')
if 'enum_4' in output['user_defined']:
	f.write("Collecting Area: " + output['user_defined']['enum_4'] + '\n')
else:
	f.write("Collecting Area: NOT ENTERED" + '\n')
if 'access_restrictions_note' in output:
	f.write("Access statement: " + output['access_restrictions_note'] + '\n')
else:
	f.write("Access statement: NOT ENTERED" + '\n')

f.close()
print "Completed. Output sent to " + fileandpath

