# Script to unpublish (or re-publish) a list of archival objects and post back to API.
# Requirements:
# - ASFunctions.py
# - A csv of format repo,objectid
# - sheetFeeder (optional, for reporting purposes)


import ASFunctions as asf
import json
from pprint import pprint
import re
import csv
from sheetFeeder import dataSheet


def main():

    # Set value to switch to, publish (True) or unpublish (False)
    publish_value = False

    # Report changes to a spreadsheet?
    report_results = True

    asf.setServer('Prod')


    # A GSheet to post report to
    the_report_sheet=dataSheet('1wNO0t2j5G9U0hUmb7E-jLd4T5skTs1aRxN7HrlyZwEI','aos_unpub3!A:Z')

    # A CSV of format <repo>,<refid>
    id_file = '/Users/dwh2128/Documents/ACFA/TEST/ACFA-141-unpublish-archival-objects/unpublish_aos_series_IIIA_PROD_p7.csv'

    # A folder to put json objects for auditing purposes
    output_folder = 'output/unpubs3'


    # Read a list of repo and object ids (csv)
    the_ids = []
    ids = open(id_file)
    for row in csv.reader(ids):
        the_ids.append([row[0],row[1]])
    ids.close()


    the_before_afters = []


    the_heads = ['repo', 'asid', 'uid','title', 'before', 'after']

    the_before_afters.append(the_heads)

    for an_obj in the_ids:

        out_path = output_folder + '/' + an_obj[0] + '_' + an_obj[1] + '_old.json'

        # read from API
        x = asf.getArchivalObjectByRef(an_obj[0],an_obj[1])


        # Save copy of existing object
        print('Saving data to ' + out_path + '....')

        f = open(out_path, "w+")
        f.write(x)
        f.close()

        x = json.loads(x)

        asid = str(x['uri'].split('/')[-1]) # get the asid from the uri string.
        repo = str(an_obj[0])

        title = x['title']

        y = x
        old_value = x['publish']
        y['publish'] = publish_value
        new_value = y['publish']

        if new_value == old_value:
            new_value = '[no change]'

        the_before_afters.append([repo, asid,an_obj[1], title, old_value, new_value])

        # convert dict back to json for posting.
        z = json.dumps(y)

        if new_value != "[no change]":
            resp = asf.postArchivalObject(repo,asid,z)
            print(resp)

        else:
            print('No update: skipping record.')


    # Report changes to Google Sheet

    if report_results == True:
        print('Writing before/after info to sheet...')
        the_report_sheet.clear()
        the_report_sheet.appendData(the_before_afters)

    print("Done!")





if __name__ == '__main__':
    main()
