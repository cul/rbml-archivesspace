import sys
import json
import requests
import secrets
import datetime

#call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

#authenticate session
params = {"password" : password}
auth = requests.post(baseURL + '/users/'+user+'/login',params=params).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}


now = datetime.datetime.utcnow()
then = now - datetime.timedelta(days=7)
user_mtime_bound = then.strftime("%Y-%m-%dT%H:%M:%SZ")
subqueries = [
	{
		"jsonmodel_type": "field_query",
		"field": "primary_type",
		"comparator": "equal",
		"value": "resource"
	},
	{
		"jsonmodel_type": "boolean_field_query",
		"field": "suppressed",
		"comparator": "equal",
		"value": False
	},
	{
		"jsonmodel_type": "boolean_field_query",
		"field": "publish",
		"comparator": "equal",
		"value": True
	},
	{
		"jsonmodel_type": "date_field_query",
		"field": "user_mtime",
		"comparator": "greater_than",
		"value": user_mtime_bound
	}
]

query = {
	"jsonmodel_type" : "advanced_query",
	"query" : {
		"jsonmodel_type": "boolean_query",
		"op": "AND",
		"subqueries": subqueries	
	}	
}

# this can also be specific to a repository ie /repositories/2/search
endpoint = "/search"
params = {
	"page": 1,
	"page_size": 1,
	"aq" : json.dumps(query)
}

#call the API
output = requests.get(baseURL + endpoint, params=params,headers=headers).text
output = json.loads(output)

print(json.dumps(output, indent=4))

#call the API
#output = requests.get(baseURL + endpoint, headers=headers).text
#print( output)

