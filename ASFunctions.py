import json
import requests
import secrets
import time

#
# Compilation of ArchivesSpace API functions. 
# Usage: from another python script, add
#   import ASFunctions
#
# Then call functions like 
#   AsFunctions.GetResource(2,4277)
#

# call secrets for authentication
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password


def main():
    # Execute the file itself to test the functions below.

    print "\nGetting an archival object..."
    print GetArchivalObject(2,33772)
    print "\nGetting a resource..."
    print GetResource(2,4277)
    print "\nGetting an agent..."
    print GetAgent(2435)
    print "\nGetting accession..."
    print GetAccession(2,3876)
    print "\nGetting schema..."
    print GetSchema()

    print "\nGetting users..."
    print GetUsers()

    #print "\nGetting accessions"
    #print GetAccessions(2)
    
    print "\nGetting agents"
    print GetAgents()
    print "\nGetting resource list"
    print GetResourceIDs(3)
    print "\nGetting resources"
    print GetResourceIDs(4)



## Functions to get single objects

def GetArchivalObject(repo,asid):
    # supply repo and id
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/archival_objects/' + str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def GetResource(repo,asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/resources/' + str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def GetAgent(asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//agents/people/'+str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def GetAccession(repo,asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/accessions/' + str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def GetSchema():
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//schemas'
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output


## Functions to get multiple objects

def GetUsers():
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//users?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    records = []
    for id in ids:
        endpoint = '//users/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        output = json.dumps(records)
        return output


def GetAccessions(repo):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/accessions?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()

    records = []
    for id in ids:
        endpoint = '//repositories/'  + str(repo) + '/accessions/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        # print output
    output = json.dumps(records)
    return output

def GetResources(repo):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/resources?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()

    records = []
    for id in ids:
        endpoint = '//repositories/' + str(repo) + '/resources/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        # print output
    output = json.dumps(records)
    return output


def GetResourceIDs(repo):
    # Return only the list of IDs, not the resources themselves
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/resources?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(ids)
    return output

  

def GetAgents():
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//agents/people?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    #iterate over each returned ID, grabbing the json object
    records = []
    for id in ids:
        endpoint = '//agents/people/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        #print output
    output = json.dump(records)
    return output
   





# Authentication function; run first, returns session headers for next API call.
def ASAuthenticate(user,baseURL,password):
    auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
    print 'authenticated'
    return headers


if __name__ == '__main__':
    main()


