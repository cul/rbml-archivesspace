import json
import requests
import secrets
import secretsDev
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


# Set to true to test on dev.
dev = False

# Load credentials and such.
if dev == True:
    baseURL = secretsDev.baseURL
    user = secretsDev.user
    password = secretsDev.password

else:
    baseURL = secrets.baseURL
    user = secrets.user
    password = secrets.password





def main():
    # Execute the file itself to test functions.
 
    print("\nGetting a resource...")
    print(getResource(2,4277))
    print("\nGetting an agent...")
    print(getAgent(2435))
    print("\nGetting accession...")
    print(getAccession(2,3876))


    print('All good!')
    quit()


###
### Functions
###


# General function to get response from a provided endpoint string (must start with slash).
def getResponse(endpoint):
    headers = ASAuthenticate(user,baseURL,password)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output


## Functions to get single objects

def getArchObjectByRef(repo,ref):
    # supply arch obj ref_id, e.g., bed5f26c0673086345e624f9bbf1d1c5
    headers = ASAuthenticate(user,baseURL,password)
    params = {"ref_id[]":ref}
    endpoint = '/repositories/' + str(repo) + '/find_by_id/archival_objects'
    lookup = requests.get(baseURL + endpoint, headers=headers, params=params).json()
    archival_object_uri = lookup['archival_objects'][0]['ref']
    asid = archival_object_uri.split('/')[-1]
    output = getArchivalObject(repo,asid)
    return output


# This doesn't work yet :(
def getResourceByID(repo,ref):
    # supply resource ID
    headers = ASAuthenticate(user,baseURL,password)
    params = {"identifier[]":ref}
    endpoint = '/repositories/' + str(repo) + '/find_by_id/resources'
    output = requests.get(baseURL + endpoint, headers=headers, params=params).json()
    output = json.dumps(output)
    return output


def getArchivalObject(repo,asid):
    # supply repo and id
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/archival_objects/' + str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def getResource(repo,asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/resources/' + str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output


def getBibID(repo,asid):
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

def getAgent(asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//agents/people/'+str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def getAccession(repo,asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/accessions/' + str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def getSchema():
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//schemas'
    output = requests.get(baseURL + endpoint, headers=headers).json()
    output = json.dumps(output)
    return output

def getEAD(repo,asid):
    # Returns EAD XML (not JSON)
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resource_descriptions-id-xml
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/resource_descriptions/' + str(asid) + '.xml'
    #optional parameters can be appended to the end of the above url - e.g. ?include_unpublished=true&include_daos=true&numbered_cs=true&print_pdf=true&ead3=true
    output = requests.get(baseURL + endpoint, headers=headers).text
    return output


def lookupByBibID(aBibID,aCSV):
    # Lookup repo and ASID against lookup table csv.
    # Format of csv should be REPO,ASID,BIBID.
    lookupTable = open(aCSV)
    for row in csv.reader(lookupTable):
        if str(aBibID) in row[2]:
            return([row[0],row[1]])
    lookupTable.close()

def lookupBibID(repo, asid ,aCSV):
    # Lookup repo and ASID against lookup table csv.
    # Format of csv should be REPO,ASID,BIBID.
    lookupTable = open(aCSV)
    for row in csv.reader(lookupTable):
        if str(repo) in row[0] and str(asid) in row[1] :
            return(row[2])
    lookupTable.close()


def getResourceByBibID(aBibID,aCSV):
    myInfo = lookupByBibID(aBibID,aCSV)
    output = getResource(myInfo[0],myInfo[1])
    return output

def getAssessment(repo,asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/assessments/' + str(asid)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    # output = json.dumps(output)
    return output


## Functions to get multiple objects

def getUsers():
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


def getAccessions(repo):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/accessions?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()

    records = []
    for id in ids:
        endpoint = '//repositories/'  + str(repo) + '/accessions/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        # print(output)
    output = json.dumps(records)
    return output

def getResources(repo):
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resources-id
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/resources?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()

    records = []
    for id in ids:
        endpoint = '//repositories/' + str(repo) + '/resources/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        # print(output)
    output = json.dumps(records)
    return output


def getResourceIDs(repo):
    # Return only the list of IDs, not the resources themselves
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resources
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/resources?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    return ids

  

def getAgents():
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//agents/people?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    #iterate over each returned ID, grabbing the json object
    records = []
    for id in ids:
        endpoint = '//agents/people/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        #print(output)
    #output = json.dump(records)
    return records
   

def getAssessments(repo):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '//repositories/' + str(repo) + '/assessments?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    #iterate over each returned assessment, grabbing the json object
    records = []
    for id in ids:
        endpoint = '//repositories/' + str(repo) + '/assessments/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        records.append(output)
        # print(output)
    output = json.dumps(records)
    return output


# Authentication function; run first, returns session headers for next API call.
def ASAuthenticate(user,baseURL,password):
    auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
    #print('authenticated')
    return headers




if __name__ == '__main__':
    main()


