# Script to generate a digital deposit info slip for a given accession.
# Required argments: <repo>, <accession_id>
# Example usage: python createDepositForm.py 2 941

import json
import requests
import secrets
import argparse
import sys
# from pprint import pprint

def main():

	global baseURL
	global user
	global password

	baseURL = secrets.baseURL
	user = secrets.user
	password = secrets.password


	p = argparse.ArgumentParser(description = 'This is a script to generate an accession deposit slip. Usage: python <scriptname> <repo> <accession_id>. ')
	p.add_argument('repo', type=int, help='repo id (2=RBML, 3=Avery, 4=Starr, 5= Burke)')
	p.add_argument('id', type=int, help='Accession id number')
	args = p.parse_args()

	repo = str(args.repo)
	accession_id = str(args.id)


	output = json.loads(getAccession(repo, accession_id))

	if 'error' in output:
		print ('ERROR: ' + output['error'])
		quit()

	
	# Get the BibID, if any
	try:
		res_url = output['related_resources'][0]['ref']
		res_id = res_url.split('/')[-1]

		bib_id = getBibID(repo,res_id)

	except:
		bib_id = ''


	# Concatenate arbitrary set of ids into id string 
	id_keys = ['id_0', 'id_1', 'id_2', 'id_3']

	id_values = []

	for k in id_keys:
		if k in output:
			id_values.append(output[k])

	id_str = '-'.join(id_values)



	# Process extents
	extents = []

	if 'extents' in output:
		for e in output['extents']:
			if 'container_summary' in e:
				extents.append( e["container_summary"] + ' (' + e['number']  + ' ' + e['extent_type'] + ')')
			else:
				extents.append(  e['number']  + ' ' + e['extent_type'] )


	ext = []
	for e in enumerate(extents, start=1):
		e = ': '.join(map(str,e))
		ext.append(e)


	if len(extents) > 1:
		extents_input = input('Use which extent(s)? ' + ';   '.join(ext) + ' [enter 1-' + str(len(ext)) + ' or RETURN for all]: ') or 0

		print(extents_input)

		extents_input = int(extents_input)

		if extents_input == 0:
			extents_selected = extents
		else:
			extents_selected = [ extents[ int(extents_input) - 1] ]

	else:
		extents_selected = extents



	# Other field values that can be copied directly

	top_fields = ['title',
				'accession_date',
				'content_description',
				'access_restrictions_note']
 
	top_data = {}

	for f in top_fields:
		if f in output:
			top_data[f] = output[f]
		else:
			top_data[f] = 'NOT ENTERED'

	
	

	# New/Additions
	if "[NEW]" in top_data['title']: 
		newadd = 'New'
	if "[ADD]" in top_data['title']:
		newadd = 'Addition'
	else:
		newadd = 'Check title for [NEW] or [ADD]'


	# Accession source (if any)
	try:
		acc_source = output['user_defined']['text_2']
	except: 
		acc_source = 'NOT ENTERED'

	# Collection area (if any)
	try:
		collecting_area = output['user_defined']['enum_4']
	except:
		collecting_area = 'NOT ENTERED'


	# Output the data
	print("Collection Name: " + top_data['title'])

	print("Date Received: " + top_data['accession_date'])

	print("Bib ID of Collection: " + bib_id )

	print("Accession Number: " + id_str )

	print("Description: " + top_data['content_description'] )

	for s in extents_selected:
		print("Size: " + s )

	print("New Collection or Addition: " + newadd )

	print("Source of Acquisition: " + acc_source )

	print("Collecting Area: " + collecting_area )

	print("Access statement: " + top_data['access_restrictions_note'] )





## API functions copied from ASFunctions.py
def ASAuthenticate(user,baseURL,password):
    try:
        auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
        session = auth["session"]
        headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
    except json.decoder.JSONDecodeError:
        print("Error: There was a problem authenticating to the API!")
        sys.exit(1)
    return headers

def getAccession(repo,asid):
    headers = ASAuthenticate(user,baseURL,password)
    endpoint = '/repositories/' + str(repo) + '/accessions/' + str(asid)
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


if __name__ == '__main__':
    main()

