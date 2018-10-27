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

#prompt to ask whether we want all, or just active, assessments
activeCheck = raw_input("Include completed assessments? Enter Y if yes (case-sensitive), leave blank if no: ")

#this is a default search that returns everything since mold appears in the conservation issues list
searchTerm = "mold"

#this is limited to the RBML repository
search = requests.get(baseURL+'/repositories/2/search?q='+searchTerm+'&type[]=assessment&page=1',headers=headers).json()
print "This script will search all assessments and list URLs and titles for collections assessed as moldy."
print "Sanity check: Number of assessments (should be equal to total of assessments number in AS) : " + str(search['total_hits'])


if activeCheck is 'Y':
	print "Including completed assessments."
#do all
	for assessment in search['results']:
	#only pull out assessments tagged with mold
	#test for conservation issues, and for active status
		if 'assessment_conservation_issues' in assessment: 
			if 'Mold' in assessment['assessment_conservation_issues'][0]:
	#			for title in assessment['assessment_records']:
	#				print title
				print "URL: " + baseURL + assessment['id'] + "|" + assessment['assessment_records'][0]
				#print assessment

else:
	print "Including only active assessments."
	for assessment in search['results']:
	#only pull out assessments tagged with mold
	#test for conservation issues, and for active status
		if 'assessment_conservation_issues' in assessment and assessment['assessment_inactive'] is False: 
			if 'Mold' in assessment['assessment_conservation_issues'][0]:
	#			for title in assessment['assessment_records']:
	#				print title
				print "URL: " + baseURL + assessment['id'] + "|" + assessment['assessment_records'][0]
				#print assessment

