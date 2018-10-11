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

#searchTerm = raw_input("Enter term to search in assessments: ")
#this is a default search that returns everything
searchTerm = "mold"
search = requests.get(baseURL+'/repositories/2/search?q='+searchTerm+'&type[]=assessment&page=1',headers=headers).json()
print "This script will search all assessments and list URLs and titles for collections assessed as moldy."
print "Sanity check: Number of assessments (should be equal to total of assessments number in AS) : " + str(search['total_hits'])
for assessment in search['results']:
#only pull out assessments tagged with mold
	if 'assessment_conservation_issues' in assessment:
		if 'Mold' in assessment['assessment_conservation_issues'][0]:
#			for title in assessment['assessment_records']:
#				print title
			print "URL: " + baseURL + assessment['id'] + "|" + assessment['assessment_records'][0]

