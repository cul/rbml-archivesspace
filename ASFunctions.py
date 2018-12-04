import json
import requests
import secrets
import time
import csv

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
    # Execute the file itself to test functions.
 
    print "\nGetting a resource..."
    print GetResource(2,4277)
    print "\nGetting an agent..."
    print GetAgent(2435)
    print "\nGetting accession..."
    print GetAccession(2,3876)
    print "\nGetting schema..."
    print GetSchema()

    #print GetArchivalObject(2,33773)
    #print GetResourceIDs(4)
    
    #print UseEndpoint('/repositories/2/resources/4278/models_in_graph')



# General function to use a provided endpoint string (must start with slash)
def UseEndpoint(endpoint):
    headers = ASAuthenticate(user,baseURL,password)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output


## Functions to get single objects

def GetArchObjectByRef(repo,ref):
    # supply arch obj ref_id, e.g., bed5f26c0673086345e624f9bbf1d1c5
    headers = ASAuthenticate(user,baseURL,password)
    params = {"ref_id[]":ref}
    endpoint = '/repositories/' + str(repo) + '/find_by_id/archival_objects'
    lookup = requests.get(baseURL + endpoint, headers=headers, params=params).json()
    archival_object_uri = lookup['archival_objects'][0]['ref']
    asid = archival_object_uri.split('/')[-1]
    output = GetArchivalObject(repo,asid)
    return output


# This doesn't work yet :(
def GetResourceByID(repo,ref):
    # supply resource ID
    headers = ASAuthenticate(user,baseURL,password)
    params = {"identifier[]":ref}
    endpoint = '/repositories/' + str(repo) + '/find_by_id/resources'
    output = requests.get(baseURL + endpoint, headers=headers, params=params).json()
    output = json.dumps(output)
    return output



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


def GetBibID(repo,asid):
    # return BibID from resource
    headers = ASAuthenticate(user,baseURL,password)    
    endpoint = '/repositories/' + str(repo) + '/resources/' + str(asid) 
    output = requests.get(baseURL + endpoint, headers=headers).json()
    try:
        userDef = output['user_defined']
        bibID = userDef['integer_1']
    except:
        bibID = ''
    return bibID



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

def GetEAD(repo,asid):
    # Returns EAD XML (not JSON)
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resource_descriptions-id-xml
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/resource_descriptions/' + str(asid) + '.xml'
    #optional parameters can be appended to the end of the above url - e.g. ?include_unpublished=true&include_daos=true&numbered_cs=true&print_pdf=true&ead3=true
    output = requests.get(baseURL + endpoint, headers=headers).text
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
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resources-id
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
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resources
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/resources?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    return ids

  

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
    #output = json.dump(records)
    return records
   





# Authentication function; run first, returns session headers for next API call.
def ASAuthenticate(user,baseURL,password):
    auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
    #print 'authenticated'
    return headers


if __name__ == '__main__':
    main()


