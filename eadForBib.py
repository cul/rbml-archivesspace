import sys
import json
import requests
import secrets
import time

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
params = {"password" : password}
auth = requests.post(baseURL + '/users/'+user+'/login',params=params).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}


bib = sys.argv[1]

endpoint = "/search"
type_filter = {
	"jsonmodel_type": "field_query",
	"field": "primary_type",
	"comparator": "equal",
	"value": "resource"
}
id_filter = {
	"jsonmodel_type": "field_query",
	"comparator": "equal",
	"field": "identifier",
	"value": bib
}
comp_query = {
	"jsonmodel_type": "boolean_query",
	"op": "AND",
	"subqueries": [type_filter, id_filter]	
}
aq = {
	"jsonmodel_type" : "advanced_query",
	"query" : comp_query
}
params = {
	"page" : 1,
	"page_size": 1,
	"aq" : json.dumps(aq)
}

#call the API
output = requests.get(baseURL + endpoint, params=params,headers=headers).text
output = json.loads(output)

# get the id, which is the REST URI path

resource_path = output["results"][0]["id"]

endpoint = resource_path.replace('/resources/','/resource_descriptions/') + '.xml'

#call the API
output = requests.get(baseURL + endpoint, headers=headers).text
print( output)

