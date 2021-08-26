import json
import requests
import csv
import sys
import os
from configparser import ConfigParser


#
# Compilation of ArchivesSpace API functions.
# See README for config.ini setup.

# Usage: from another python script, add
#   import ASFunctions as asf
#
# Then call functions like
#   asf.getResource(2,4277)
#
#


global baseURL
global user
global password
global session_token
global config


my_name = __file__

# This makes sure the script can be run from any working directory and still find related files.
my_path = os.path.dirname(__file__)

config_path = os.path.join(my_path, "config.ini")


try:
    # See if there is an initial session token in environment to use.
    session_token = os.environ["session"]
except:
    session_token = ""


# Set server to Prod as default. Override in parent script with
# ASFunctions.setServer('Test') or ASFunctions.setServer('Dev').
try:
    # Read default config values
    config = ConfigParser()
    config.read(config_path)

    baseURL = config["PROD"]["baseURL"]
    user = config["PROD"]["user"]
    password = config["PROD"]["password"]
    # List of used AS repo codes
    valid_repos = json.loads(config["REPOS"]["validRepos"])

    # Get proxy url if there is one.
    if "httpsProxy" in config["PROXIES"]:
        https_proxy = config["PROXIES"]["httpsProxy"]
    else:
        https_proxy = None
except Exception as e:
    print("Error: There was a problem reading the config.ini file." + str(e))
    sys.exit(1)


def main():
    # Test functions here.
    from pprint import pprint

    setServer("Test")
    x = json.loads(getResource(2, 5907))
    pprint(x)
    setServer("Prod")
    x = json.loads(getResource(2, 5907))

    pprint(x)

    quit()

    pprint(json.loads(getArchivalObjectByRef(2, "f600a2fa87f5def358831bd367753f2a")))

    quit()

    print(
        getResponse(
            "repositories/2/find_by_id/archival_objects?ref_id[]=fd30ef92c90442fe861683b81dd1b4e8"
        )
    )

    print(getArchivalObject(2, "560142"))
    # print(getEAD(2, 5907))
    # print(unpublishArchivalObject2(2, 456421))

    # print(getResource2(2, 5907))
    quit()


########### TEST ##########


def deleteArchivalObject(repo, asid):
    # TODO: Test
    headers = ASAuthenticate(user, baseURL, password)
    print(headers)
    endpoint = "/repositories/" + str(repo) + "/archival_objects/" + str(asid)
    deletion = requests.delete(baseURL + endpoint, headers=headers)
    return deletion


def getArchivalObjectByRef2(repo, ref):
    # TODO! Reconcile if needed.(?)
    # supply arch obj ref_id, e.g., bed5f26c0673086345e624f9bbf1d1c5
    headers = ASAuthenticate(user, baseURL, password)
    params = {"ref_id[]": ref}
    endpoint = "/repositories/" + str(repo) + "/find_by_id/archival_objects"
    lookup = getIt(baseURL + endpoint, headers=headers, params=params)
    return lookup
    # archival_object_uri = lookup["archival_objects"][0]["ref"]
    # asid = archival_object_uri.split("/")[-1]
    # output = getArchivalObject(repo, asid)
    # return output


###########################
# TEST


#######################################
# Authentication and global handlers  #
#######################################

# Returns session headers for next API call, either using existing session token or generating one.


def ASAuthenticate(user, baseURL, password):
    global session_token
    if session_token != "":
        # there is already a token in env
        headers = {
            "X-ArchivesSpace-Session": session_token,
            "Content_Type": "application/json",
        }
    else:
        # generate a new token and save to env
        try:
            # get auth response including session token from API
            if https_proxy:
                auth = requests.post(
                    baseURL + "/users/" + user + "/login?password=" + password,
                    proxies={"https": https_proxy},
                ).json()
                msg = "(Authenticated using proxy " + https_proxy + ")"
            else:
                auth = requests.post(
                    baseURL + "/users/" + user + "/login?password=" + password
                ).json()
                msg = "(Authenticated)"

            if "error" in auth:
                print("AUTHENTICATION ERROR: " + auth["error"])
                sys.exit(1)
            else:
                print(msg)
            session_token = auth["session"]
            os.environ["session"] = session_token
        except Exception as e:
            print("Error: There was a problem authenticating to the API!" + str(e))
            sys.exit(1)
        headers = {
            "X-ArchivesSpace-Session": session_token,
            "Content_Type": "application/json",
        }
    return headers


# Generic fn to do GET with or without proxy, as defined by config.
def getIt(uri_str, headers, params=None, output="json"):
    if https_proxy:
        response = requests.get(
            uri_str, headers=headers, params=params, proxies={"https": https_proxy}
        )
    else:
        response = requests.get(uri_str, headers=headers, params=params)
    if output == "json":
        return response.json()
    elif output == "text":
        return response.text
    else:
        print("ERROR: Output type " + output + " not recognized!")


# Generic fn to do POST with or without proxy, as defined by config.


def postIt(uri_str, headers, data):
    if https_proxy:
        return requests.post(
            uri_str, headers=headers, data=data, proxies={"https": https_proxy}
        ).json()
    else:
        return requests.post(uri_str, headers=headers, data=data).json()


#################
### FUNCTIONS ###
#################


# Set server to 'Prod' (default) | 'Test' | 'Dev'
def setServer(server):
    global baseURL
    global user
    global password
    global config
    global session_token
    session_token = ""  # start with fresh auth token
    if server == "Dev":
        baseURL = config["DEV"]["baseURL"]
        user = config["DEV"]["user"]
        password = config["DEV"]["password"]
    elif server == "Test":
        baseURL = config["TEST"]["baseURL"]
        user = config["TEST"]["user"]
        password = config["TEST"]["password"]
    else:
        baseURL = config["PROD"]["baseURL"]
        user = config["PROD"]["user"]
        password = config["PROD"]["password"]


# General function to get response from a provided endpoint string (must start with slash).
def getResponse(endpoint):
    headers = ASAuthenticate(user, baseURL, password)
    output = getIt(baseURL + endpoint, headers=headers)
    output = json.dumps(output)
    return output


#####################################
# Functions to get single objects   #
#####################################


def getArchivalObject(repo, asid):
    # supply repo and id
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/archival_objects/" + str(asid)
    output = getIt(baseURL + endpoint, headers=headers)
    output = json.dumps(output)
    return output


def getArchivalObjectByRef(repo, ref):
    # supply arch obj ref_id, e.g., bed5f26c0673086345e624f9bbf1d1c5
    headers = ASAuthenticate(user, baseURL, password)
    params = {"ref_id[]": ref}
    endpoint = "/repositories/" + str(repo) + "/find_by_id/archival_objects"
    lookup = getIt(baseURL + endpoint, headers=headers, params=params)
    archival_object_uri = lookup["archival_objects"][0]["ref"]
    asid = archival_object_uri.split("/")[-1]
    output = getArchivalObject(repo, asid)
    return output


def getCollectionManagement(repo, asid):
    # supply repo and id
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/collection_management/" + str(asid)
    output = getIt(baseURL + endpoint, headers=headers)
    output = json.dumps(output)
    return output


def getEnumeration(asid):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/config/enumerations/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


def getEnumerationValue(asid):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/config/enumeration_values/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


def getResource(repo, asid):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/resources/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


def getResourceByID(bibid, repos=valid_repos):
    # Find resource across all valid repos using field 'identifier'=<bibid>.
    for r in repos:
        res = getResourceByRepoID(r, bibid)
        if res:
            return res


def getResourceByRepoID(repo, bibid):
    # Find and return resource based on repo and field 'identifier'=<bibid>.
    # Intended for use by getResourceByID.
    aquery = {
        "query": {
            "op": "AND",
            "subqueries": [
                {
                    "field": "primary_type",
                    "value": "resource",
                    "comparator": "equals",
                    "jsonmodel_type": "field_query",
                },
                {
                    "field": "identifier",
                    "value": str(bibid),
                    "comparator": "equals",
                    "jsonmodel_type": "field_query",
                },
            ],
            "jsonmodel_type": "boolean_query",
        },
        "jsonmodel_type": "advanced_query",
    }
    res = getSearchResults(repo, json.dumps(aquery))
    if len(res) == 1:
        return json.dumps(res[0])


def getDigitalObject(repo, asid):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/digital_objects/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


def getDigitalObjectByRef(repo, ref):
    headers = ASAuthenticate(user, baseURL, password)
    params = {"resolve[]": "digital_objects", "digital_object_id[]": ref}
    endpoint = "/repositories/" + str(repo) + "/find_by_id/digital_objects"
    output = getIt(baseURL + endpoint, headers=headers, params=params)
    output = json.dumps(output)
    return output


def getDigitalObjectFromParent(repo, ref):
    # use an aspace id string like '59ad1b96a7786e6ab3e2a9aa2223dfcf', as found in EAD export of a parent archival object, to identify the digital object within and extract it.
    x = getArchivalObjectByRef(repo, ref)
    the_parent = json.loads(x)
    the_dao_refs = [
        inst["digital_object"]
        for inst in the_parent["instances"]
        if "digital_object" in inst
    ]

    results = []
    for dao_ref in the_dao_refs:
        uri = dao_ref["ref"]
        asid = str(uri.split("/")[-1])
        the_dao = getDigitalObject(repo, asid)
        results.append(the_dao)
    return results[0]  # is there ever more than one dao?


def getBibID(repo, asid):
    # return BibID from resource
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/resources/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    try:
        userDef = output["user_defined"]
        bibID = userDef["integer_1"]
    except:
        bibID = ""
    return bibID


def getAgent(asid, agent_type="people"):
    # types: people, families, corporate_entities
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//agents/" + agent_type + "/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


def getAccession(repo, asid):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/accessions/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


def getSchema():
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//schemas"
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


def getEAD(repo, asid):
    # Returns EAD XML (not JSON)
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resource_descriptions-id-xml
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = (
        "/repositories/"
        + str(repo)
        + "/resource_descriptions/"
        + str(asid)
        + ".xml"
        + "?include_unpublished=true&include_daos=true"
    )
    # optional parameters can be appended to the end of the above url - e.g. ?include_unpublished=true&include_daos=true&numbered_cs=true&print_pdf=true&ead3=true
    # output = requests.get(baseURL + endpoint, headers=headers).text
    output = getIt(baseURL + endpoint, headers=headers, output="text")
    return output


def lookupByBibID(aBibID, aCSV):
    # Lookup repo and ASID against lookup table csv.
    # Format of csv should be REPO,ASID,BIBID.
    lookupTable = open(aCSV)
    for row in csv.reader(lookupTable):
        if str(aBibID) in row[2]:
            return [row[0], row[1]]
    lookupTable.close()


def lookupBibID(repo, asid, aCSV):
    # Lookup repo and ASID against lookup table csv.
    # Format of csv should be REPO,ASID,BIBID.
    lookupTable = open(aCSV)
    for row in csv.reader(lookupTable):
        if str(repo) in row[0] and str(asid) in row[1]:
            return row[2]
    lookupTable.close()


def getResourceByBibID(aBibID, aCSV):
    myInfo = lookupByBibID(aBibID, aCSV)
    output = getResource(myInfo[0], myInfo[1])
    return output


def getAssessment(repo, asid):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/assessments/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    # output = json.dumps(output)
    return output


def getSubject(id):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/subjects/" + str(id)
    output = getIt(baseURL + endpoint, headers)
    # output = json.dumps(output)
    return output


def getTopContainer(repo, asid):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/top_containers/" + str(asid)
    output = getIt(baseURL + endpoint, headers)
    output = json.dumps(output)
    return output


#####################################
# Functions to get multiple objects #
#####################################


def getAccessions(repo):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//repositories/" + str(repo) + "/accessions?all_ids=true"
    ids = getIt(baseURL + endpoint, headers)

    records = []
    for id in ids:
        endpoint = "//repositories/" + str(repo) + "/accessions/" + str(id)
        output = getIt(baseURL + endpoint, headers)
        records.append(output)
        # print(output)
    output = json.dumps(records)
    return output


def getAgents(agent_type="people"):
    # types: people, families, corporate_entities
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//agents/" + agent_type + "?all_ids=true"
    ids = getIt(baseURL + endpoint, headers)
    # iterate over each returned ID, grabbing the json object
    records = []
    for id in ids:
        endpoint = "//agents/people/" + str(id)
        output = getIt(baseURL + endpoint, headers)
        records.append(output)
        # print(output)
    # output = json.dump(records)
    return records


def getArchivalObjectChildren(repo, asid):
    # Get a list of asids of children of an archival object.
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = (
        "/repositories/" + str(repo) + "/archival_objects/" + str(asid) + "/children"
    )
    response = getIt(baseURL + endpoint, headers)
    my_ids = [x["uri"].split("/")[-1] for x in response]
    return my_ids


def getAssessments(repo):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//repositories/" + str(repo) + "/assessments?all_ids=true"
    ids = getIt(baseURL + endpoint, headers)
    # iterate over each returned assessment, grabbing the json object
    records = []
    for id in ids:
        endpoint = "//repositories/" + str(repo) + "/assessments/" + str(id)
        output = getIt(baseURL + endpoint, headers)
        records.append(output)
        # print(output)
    output = json.dumps(records)
    return output


def getByDate(
    repo,
    date,
    date_type="ctime",
    comparator="equal",
    filter=None,
    fields=["id", "create_time", "title"],
):
    # Returns records with create_time <, =, or > than given date.
    # OPTIONAL FIELDS:
    #   comparators: equal (default), greater_than, lesser_than (not 'less_than'!)
    #   filters: None (default), archival_objects, resources, accessions,
    #      collection_managment, top_containers
    #   fields: Can be any field at top level of returned json object;
    #      these will form the output dict of each returned record.
    #   date_type: ctime or mtime (date created or date modified)

    # Select ctime or mtime based on param
    date_field = "create_time" if date_type == "ctime" else "system_mtime"
    aqparams = (
        '{"query":{"field":"'
        + date_field
        + '","value":"'
        + date
        + '","comparator":"'
        + comparator
        + '","jsonmodel_type":"date_field_query"},"jsonmodel_type":"advanced_query"}'
    )

    records = getSearchResults(repo, aqparams)

    # Filtering based on record type (archival_objects, resources, etc.)
    if filter == None:
        records_out = records
    else:
        records_out = [rec for rec in records if filter in rec["id"]]

    print("Number of matching records = " + str(len(records_out)))

    # Compile a dictionary for each record, based on which fields are requested (see defaults in def).
    output = []
    for r in records_out:
        rec_dict = {}
        for f in fields:
            # If field is not in a record (e.g., 'publish' is not in all types) the value will be empty.
            if f in r:
                rec_dict[f] = r[f]
            else:
                rec_dict[f] = ""
        output.append(rec_dict)

    return output


def getResources(repo):
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resources-id
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//repositories/" + str(repo) + "/resources?all_ids=true"
    ids = getIt(baseURL + endpoint, headers)

    records = []
    for id in ids:
        endpoint = "//repositories/" + str(repo) + "/resources/" + str(id)
        output = getIt(baseURL + endpoint, headers)
        records.append(output)
        # print(output)
    output = json.dumps(records)
    return output


def getResourceIDs(repo):
    # Return only the list of IDs, not the resources themselves
    # https://archivesspace.github.io/archivesspace/api/#get-repositories-repo_id-resources
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//repositories/" + str(repo) + "/resources?all_ids=true"
    ids = getIt(baseURL + endpoint, headers)
    return ids


def getSubjects():
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//subjects?all_ids=true"
    ids = getIt(baseURL + endpoint, headers)
    records = []
    for id in ids:
        endpoint = "//subjects/" + str(id)
        output = getIt(baseURL + endpoint, headers)
        records.append(output)
    return records


def getSearchResults(repo, query_params):
    # General function to process an advanced query and return unfiltered results. Intended to be called by other functions where the query string may be built by user input and the results parsed, e.g, getByCreateDate.
    # Supply repo id and advanced query string of the form:
    #     x = getSearchResults(2, '{"query":{"field":"create_time",
    #           "value":"2019-08-13","comparator":"equal",
    #           "jsonmodel_type":"date_field_query"},
    #           "jsonmodel_type":"advanced_query"}')
    #
    # See http://lyralists.lyrasis.org/pipermail/archivesspace_users_group/2015-May/001654.html for advanced query info.

    records = []

    page_size = 100  # default
    pageno = 1  # default
    headers = ASAuthenticate(user, baseURL, password)

    endpoint = (
        "//repositories/"
        + str(repo)
        + "/search?page="
        + str(pageno)
        + "&page_size="
        + str(page_size)
        + "&aq="
        + query_params
    )
    response_init = getIt(baseURL + endpoint, headers)

    hit_count = response_init["total_hits"]
    # Check to see if hits exceed default page_size; if so, increase page_size to match hits and do API call again.

    print("Number of search hits: " + str(hit_count))

    if hit_count > page_size:

        # Check to see if count exceeds page size limit (250); if so, need to iterate through pages.
        if hit_count < 250:
            page_size = hit_count + 1  # add one, just for fun
            endpoint = (
                "//repositories/"
                + str(repo)
                + "/search?page="
                + str(pageno)
                + "&page_size="
                + str(page_size)
                + "&aq="
                + query_params
            )
            response = getIt(baseURL + endpoint, headers)
            records = response["results"]

        else:
            response_list = []
            # Hit count >= 250; need to paginate!
            page_size = 250
            # use divmod to get number of pages needed
            dm = divmod(hit_count, page_size)
            page_cnt = dm[0] if dm[1] == 0 else dm[0] + 1

            # print('page_cnt=' + str(page_cnt))

            for i in range(page_cnt):
                pageno = i + 1
                print("Fetching page " + str(pageno) + " of " + str(page_cnt))
                # run for each page
                endpoint = (
                    "//repositories/"
                    + str(repo)
                    + "/search?page="
                    + str(pageno)
                    + "&page_size="
                    + str(page_size)
                    + "&aq="
                    + query_params
                )
                response = getIt(baseURL + endpoint, headers)
                records.extend(response["results"])

    else:
        response = response_init
        records = response["results"]

    return records


def getUnpublished(repo, filter=None, fields=["id", "create_time", "title"]):
    # Returns unpublished records for a given repo. Any list of top-level fields can be selected to return in output.

    aqparams = '{"query":{"field":"publish","value":false,"jsonmodel_type":"boolean_field_query"},"jsonmodel_type":"advanced_query"}'
    records = getSearchResults(repo, aqparams)
    # Filtering based on record type (archival_objects, resources, etc.)
    if filter == None:
        records_out = records
    else:
        records_out = [rec for rec in records if filter in rec["id"]]
    print("Number of matching records = " + str(len(records_out)))
    # Compile a dictionary for each record, based on which fields are requested (see defaults in def).
    output = []
    for r in records_out:
        rec_dict = {}
        for f in fields:
            # If field is not in a record (e.g., 'publish' is not in all types) the value will be empty.
            if f in r:
                rec_dict[f] = r[f]
            else:
                rec_dict[f] = ""
        output.append(rec_dict)
    return output


def getCollectionManagements(
    repo, filter=None, fields=["id", "parent_id", "title", "system_mtime"]
):
    # Returns list of collection management records for a given repo. Filter by parent type, i.e., resource | accession (default all). Any arbitrary set of top-level fields can be returned.

    aqparams = '{"query":{"field":"primary_type", "value":"collection_management", "jsonmodel_type":"field_query"},"jsonmodel_type":"advanced_query"}'
    records = getSearchResults(repo, aqparams)
    # Filtering based on parent type (resource, accession)
    if filter == None:
        records_out = records
    else:
        records_out = [rec for rec in records if filter in rec["parent_type"]]
    print("Number of matching records = " + str(len(records_out)))
    # Compile a dictionary for each record, based on which fields are requested (see defaults in def).
    output = []
    for r in records_out:
        rec_dict = {}
        for f in fields:
            # If field is not in a record the value will be empty.
            if f in r:
                rec_dict[f] = r[f]
            else:
                rec_dict[f] = ""
        output.append(rec_dict)
    return output


def getUsers():
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "//users?all_ids=true"
    ids = getIt(baseURL + endpoint, headers)
    records = []
    for id in ids:
        endpoint = "//users/" + str(id)
        output = getIt(baseURL + endpoint, headers)
        records.append(output)
        output = json.dumps(records)
        return output


def daosRecurse(repo, asid):
    # Recursive function; only use in call from find_daos()!
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = (
        "/repositories/" + str(repo) + "/archival_objects/" + str(asid) + "/children"
    )
    x = getIt(baseURL + endpoint, headers)

    # Look for daos as children of archival object
    for a_child in x:
        # Debug: print(a_child['uri'])
        the_dao_refs = [
            inst["digital_object"]["ref"]
            for inst in a_child["instances"]
            if "digital_object" in inst
        ]
        if len(the_dao_refs) > 0:
            the_id = the_dao_refs[0].split("/")[-1]
            # Debug: print('Found a dao: ' + str(the_id))
            the_daos.append(the_id)
    # Only process children recursively if there are no daos (i.e. we are not at the file level yet).
    if len(the_daos) == 0:
        # Debug: print('going down one level...')
        next_gen = [a_child["uri"].split("/")[-1] for a_child in x]
        for an_id in next_gen:
            daosRecurse(repo, an_id)


def findDigitalObjectDescendants(repo, asid):
    # For any archival object, return a list of DAOs that are associated with children or descendants.
    # Note: calls a recursive function, can take some time for large trees.
    global the_daos
    the_daos = []
    daosRecurse(repo, asid)
    return the_daos


###################################
# Functions to post data          #
###################################


def postArchivalObject(repo, asid, record):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/archival_objects/" + str(asid)
    post = postIt(baseURL + endpoint, headers, record)
    # post = requests.post(baseURL + endpoint,
    #                      headers=headers, data=record).json()
    post = json.dumps(post)
    return post


def postAgent(asid, record, agent_type="people"):
    # types: people, families, corporate_entities
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/agents/" + agent_type + "/" + str(asid)
    post = postIt(baseURL + endpoint, headers, record)
    # post = requests.post(baseURL + endpoint,
    #                      headers=headers, data=record).json()
    post = json.dumps(post)
    return post


def postDigitalObject(repo, asid, record):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/digital_objects/" + str(asid)
    post = postIt(baseURL + endpoint, headers, record)
    # post = requests.post(baseURL + endpoint,
    #                      headers=headers, data=record).json()
    post = json.dumps(post)
    return post


def postEnumeration(asid, record):
    # TODO: This perhaps does not work?
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/config/enumerations/" + str(asid)
    post = postIt(baseURL + endpoint, headers, record)
    # post = requests.post(baseURL + endpoint,
    #                      headers=headers, data=record).json()
    post = json.dumps(post)
    return post


def postEnumerationValue(asid, record):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/config/enumeration_values/" + str(asid)
    post = postIt(baseURL + endpoint, headers, record)
    # post = requests.post(baseURL + endpoint,
    #                      headers=headers, data=record).json()
    post = json.dumps(post)
    return post


def postResource(repo, asid, record):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/resources/" + str(asid)
    post = postIt(baseURL + endpoint, headers, record)
    # post = requests.post(baseURL + endpoint,
    #                      headers=headers, data=record).json()
    post = json.dumps(post)
    return post


def postSubject(asid, record):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/subjects/" + str(asid)
    post = postIt(baseURL + endpoint, headers, record)
    # post = requests.post(baseURL + endpoint,
    #                      headers=headers, data=record).json()
    post = json.dumps(post)
    return post


def postTopContainer(repo, asid, record):
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = "/repositories/" + str(repo) + "/top_containers/" + str(asid)

    post = postIt(baseURL + endpoint, headers, record)
    post = json.dumps(post)
    return post


def suppressEnumerationValue(asid, mode="suppress"):
    # Set mode to 'unsuppress' to do so, otherwise suppress
    if mode == "suppress":
        suppress_flag = "suppressed=true"
    else:
        suppress_flag = "suppressed=false"
    headers = ASAuthenticate(user, baseURL, password)
    endpoint = (
        "/config/enumeration_values/" + str(asid) + "/suppressed?" + suppress_flag
    )
    # TODO: add postIt method without record data? Test this.
    post = postIt(baseURL + endpoint, headers, "")
    post = requests.post(baseURL + endpoint, headers=headers).json()
    post = json.dumps(post)
    return post


def unpublishArchivalObject(repo, asid):
    x = getArchivalObject(repo, asid)
    y = json.loads(x)
    y["publish"] = False
    z = json.dumps(y)
    return postArchivalObject(repo, asid, z)


if __name__ == "__main__":
    main()
