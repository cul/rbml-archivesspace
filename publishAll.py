import json
import requests
import secretsDev
import time

startTime = time.time()

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

#call each repo for list of all resources
rbmlResources = requests.get(baseURL + '/repositories/2/resources?all_ids=true', headers=headers).json()
averyResources = requests.get(baseURL + '/repositories/3/resources?all_ids=true', headers=headers).json()
starrResources = requests.get(baseURL + '/repositories/4/resources?all_ids=true', headers=headers).json()
burkeResources = requests.get(baseURL + '/repositories/5/resources?all_ids=true', headers=headers).json()

#publish rbmlResources
for i in range (0, len (rbmlResources)):
	resourceUri = '/repositories/2/resources/' + str(rbmlResources[i])
	print resourceUri
	resource_publish_all = requests.post(baseURL + resourceUri + '/publish',headers=headers)
	print resourceUri  + '--RBML resource and all children set to published'

#publish averyResources
for i in range (0, len (averyResources)):
        resourceUri = '/repositories/3/resources/' + str(averyResources[i])
        print resourceUri
        resource_publish_all = requests.post(baseURL + resourceUri + '/publish',headers=headers)
        print resourceUri  + '--Avery resource and all children set to published'

#publish starrResources
for i in range (0, len (starrResources)):
        resourceUri = '/repositories/4/resources/' + str(starrResources[i])
        print resourceUri
        resource_publish_all = requests.post(baseURL + resourceUri + '/publish',headers=headers)
        print resourceUri  + '-- Starr resource and all children set to published'

#publish burkeResources
for i in range (0, len (burkeResources)):
        resourceUri = '/repositories/5/resources/' + str(burkeResources[i])
        print resourceUri
        resource_publish_all = requests.post(baseURL + resourceUri + '/publish',headers=headers)
        print resourceUri  + '-- Burke resource and all children set to published'

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
