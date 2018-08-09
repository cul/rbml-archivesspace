import json
import requests
import csv
import secretsDev
import time

#call secrets for authentication
baseURL = secretsDev.baseURL
user = secretsDev.user
password = secretsDev.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

print 'authenticated'

startTime = time.time()

#print "Is set to dev if URL contains dev:", baseURL
#raw_input("Press Enter to continue...")

with open('lc_agents.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter='|', quotechar='"')
    for row in reader:
        ASID = row[2].strip()
	authno = 'http://id.loc.gov/authorities/names/' + row[1].strip()
	try:

        # Submit a get request for the archival object and store the JSON
	        agent_json = requests.get(baseURL+ASID,headers=headers).json()
	#add authno and source to object
		agent_json['names'][0]['authority_id'] = authno
		agent_json['names'][0]['source'] = "naf"

        #prepare for repost
	        agent_data = json.dumps(agent_json)

        # Repost the agent with the authority number
        	archival_object_update = requests.post(baseURL+ASID,headers=headers,data=agent_data).json()
	        print archival_object_update, '|', row[0]
	except:
		print "Error", ASID, autho

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
