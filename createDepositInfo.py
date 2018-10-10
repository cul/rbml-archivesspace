import json
import requests
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

print "This script will create a text suitable for a deposit-info.txt file."
repo = raw_input("Enter repo ID; 2=RBML, 3=Avery, 4=Starr, 5= Burke:")
accession = raw_input("Enter accession ID:")

#define the API call to get a list of all agent IDs
endpoint = '/repositories/' + repo + '/accessions/' + accession

#call the API
output = requests.get(baseURL + endpoint, headers=headers).json()

print "Collection Name: " + output['title']
print "Date Received: " + output['accession_date']
print "Bib ID of Collection: " + output['user_defined']['integer_1']
#test for fourth field in identifier
if 'id_3' in output:
	print "Accession Number: " + output['id_0'] + "-" +  output['id_1'] + "-" + output['id_2'] + "-" + output['id_3'] 
else:
	print "Accession Number: " + output['id_0'] + "-" +  output['id_1'] + "-" + output['id_2']
print "Description: " + output['content_description']
print "Size: " + output['extents'][0]['container_summary']
if "[NEW]" in output['title']: 
	newadd = 'New'
if "[ADD]" in output['title']:
	newadd = 'Addition'
else:
	newadd = 'Check title for [NEW] or [ADD]'
print "New Collection or Addition: " + newadd
if 'text_2' in output['user_defined']: 
	print "Source of Acquisition: " + output['user_defined']['text_2']
else:
	print "Source of Acquisition: NOT ENTERED"
if 'enum_4' in output['user_defined']:
	print "Collecting Area: " + output['user_defined']['enum_4']
else:
        print "Collecting Area: NOT ENTERED"
print "Access statement: " + output['access_restrictions_note']
