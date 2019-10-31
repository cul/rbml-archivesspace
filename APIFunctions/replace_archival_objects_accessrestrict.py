# Script to add access restrict note to archival object.
# Set the_type to 'vetted' or 'unvetted' to create an access restriction
# note with the values defined in access_types dict.
# If there is already an accessrestrict note, it will be skipped.

# Workflow: Use EAD extract to generate a list of ref ids to feed into the script as CSV.

# Requirements:
# - ASFunctions.py
# - A csv of format repo,objectid
# - an output folder to save JSON objects (for auditing of changes, if needed)


import ASFunctions as asf
import json
from pprint import pprint
import re
import csv
from operator import itemgetter


def main():

    asf.setServer('Prod')

    id_file = '/Users/dwh2128/Documents/ACFA/TEST/ACFA-147-hrw-access-restrictions/acfa-147-aos_UNVETTED.csv'
    output_folder = 'output/archival_objects_accessrestrict'

    # Read a list of repo and object ids (csv)
    the_ids = []
    ids = open(id_file)
    for row in csv.reader(ids):
        the_ids.append([row[0],row[1]])
    ids.close()


    access_types = {'unvetted':
                {'vocab':'TEMPORARILY UNAVAILABLE',
                'text':'[Unvetted]'},
            'vetted':
                {'vocab':'AVAILABLE',
                'text':'[Vetted, open]'}
            }

    # Set to 'vetted' or 'unvetted'
    the_type = 'unvetted'


    for an_obj in the_ids:
        out_path = output_folder + '/' + an_obj[0] + '_' + an_obj[1] + '_old.json'

        # read from API
        x = asf.getArchivalObjectByRef(an_obj[0],an_obj[1])


        # Save copy of existing object
        print('Saving data to ' + out_path + '....')

        with open(out_path, "w+") as f:
            f.write(x)

        y = json.loads(x)

        asid = str(y['uri'].split('/')[-1]) # get the asid from the uri string.
        repo = str(an_obj[0])

        print('Processing ' + str(repo) + ' - ' + str(asid) + '...')

        the_notes = y['notes']

        # Test if there is already an accessrestrict
        has_accrestrict = False
        for an_item in the_notes:
            if an_item['type'] == 'accessrestrict':
                has_accrestrict = True


        if has_accrestrict == False:

            print('Adding access restrict note ...')

            the_access_note =  {'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'rights_restriction': {'local_access_restriction_type': [access_types[the_type]['vocab']]},
                    'subnotes': [{'content': access_types[the_type]['text'],
                                'jsonmodel_type': 'note_text',
                                'publish': True}],
                    'type': 'accessrestrict'}


            y['notes'].append(the_access_note)
            # the_notes = y['notes']

            z = json.dumps(y)

            # print(z)

            post = asf.postArchivalObject(repo,asid,z)
            print(post)

        else:
            print('Already has access restrict note. Skipping!')

    print("Done!")






if __name__ == '__main__':
    main()
