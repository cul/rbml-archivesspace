import json
import time
import csv

startTime = time.time()

#this will loop through each line of the LTI csv file, which is fine -- this should be equal to or greater than the number of records in AS
with open('LTIinfo.csv', 'rb') as csvfile:
	csv = csv.DictReader(csvfile, delimiter='|', quotechar='"')
	for row in csv:
		
#interate over the AS json records
		records = json.load(open('corps.json'))
		for i in range (0, len (records)):
		    record = json.dumps(records[i])
		    #try loop to force skip of records with no authority ID
		    try:
		    	authNo = records[i]['names'][0]['authority_id']
		    	#try to match on auth number
		    	if row['authNo'] == authNo:
		    		#on match, write record to python object
		    		python_obj = json.loads(record)
		    		#write values from csv into the right fields
		    		python_obj['names'][0]['primary_name'] = row['primary_name']
		    		python_obj['names'][0]['sort_name'] = row['sort_name']
		    		python_obj['display_name']['primary_name'] = row['primary_name']
		    		python_obj['display_name']['sort_name'] = row['sort_name']
		    		#convert back to json; probably write this object to an output file
		    		print json.dumps(python_obj)
		    except:
		    	#write unchanged to log only (presumably non-auth-ID'ed json object to output file, since we don't need to re-import)
		    	print records[i]['uri'], 'has no matching authority ID in AS'

   #account for LTI records coming back where the bib record is new, and the authority in AS doesn't have an auth_no yet.   

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)