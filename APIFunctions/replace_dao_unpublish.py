import ASFunctions as asf
import json
from pprint import pprint
import re
import csv
from sheetFeeder import dataSheet

# Script to take a list of uids for archival objects with daos in them (scraped from EAD), and do a bulk search/replace on the URIs of the digital_objects. 
# Requires a CSV of format repo,uid.

def main():

    # Set to Test | Dev | Prod
    asf.setServer('Prod')

    the_report_sheet=dataSheet('1wNO0t2j5G9U0hUmb7E-jLd4T5skTs1aRxN7HrlyZwEI','daos-unpub!A:Z')


    id_file = 'replace_dao_unpublish.csv'
    output_folder = 'output/daos-unpub'

    # Read a list of repo and object ids (csv)
    the_ids = []
    ids = open(id_file)
    for row in csv.reader(ids):
        the_ids.append([row[0],row[1]])
    ids.close()


    the_before_afters = []

    the_heads = ['repo', 'asid', 'uid', 'title', 'before', 'after']

    the_before_afters.append(the_heads)

    for an_obj in the_ids:

        out_path = output_folder + '/' + an_obj[0] + '_' + an_obj[1] + '_old.json'

        # read from API

        # try:
        x = asf.getDigitalObjectFromParent(an_obj[0],an_obj[1])

        # Save copy of existing object
        print('Saving data to ' + out_path + '....')

        f = open(out_path, "w+")
        f.write(x)
        f.close()

        x = json.loads(x)

        # the_old_field_data = x['file_versions'][0]['file_uri']
        the_old_field_data = x['publish']

        asid = str(x['uri'].split('/')[-1]) # get the asid from the uri string.

        title = x['title']

        repo = str(an_obj[0])

        y = x

        # Here set the desired value
        y['publish'] = True


        if y['publish'] == the_old_field_data:
            the_new_field_data = "[no change]"
        else:
            the_new_field_data = y['publish']


        the_before_afters.append([an_obj[0], asid, an_obj[1], title,  the_old_field_data,  the_new_field_data ])

        # convert dict back to json for posting.
        z = json.dumps(y)

        # Post the fixed object back to API.
        # (Comment these out for testing.)
        if the_new_field_data != "[no change]":
            resp = asf.postDigitalObject(repo,asid,z)
            print(resp)
        else:
            print('No update: skipping record.')

        # except:
        #     print('Could not retrieve record ' + str(an_obj[1]))
            

    # Report changes to Google Sheet
    print('Writing before/after info to sheet...')
    the_report_sheet.clear()
    the_report_sheet.appendData(the_before_afters)


    print("Done!")

    quit()





if __name__ == '__main__':
    main()


