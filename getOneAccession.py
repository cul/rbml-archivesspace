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

repo = raw_input("Enter repo ID; 2=RBML, 3=Avery, 4=Starr, 5= Burke:")
accession = raw_input("Enter accession ID:")

#define the API call to get a list of all agent IDs
endpoint = '/repositories/' + repo + '/accessions/' + accession

#call the API
output = requests.get(baseURL + endpoint, headers=headers).json()
print json.dumps(output)

