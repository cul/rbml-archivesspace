# Script to replace text in designated fields in an archival object and post back to API.
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

    asf.setServer('Prod')

    the_report_sheet=dataSheet('1wNO0t2j5G9U0hUmb7E-jLd4T5skTs1aRxN7HrlyZwEI','ampersands!A:Z')

    id_file = 'archival_objects.csv'
    output_folder = 'output/archival_objects'

    # Read a list of repo and object ids (csv)
    the_ids = []
    ids = open(id_file)
    for row in csv.reader(ids):
        the_ids.append([row[0],row[1]])
    ids.close()

    # Search/replace patterns
    the_search_pattern = '&amp;amp;'
    the_replace_pattern = '&amp;'


    the_before_afters = []

    # the fields to perform regex replace on.
    the_fields = ['title', 'display_string']

    the_heads = ['repo', 'asid', 'uid','before', 'after']

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

        the_initial_values = [str('{' + f + '_old:} ' + x[f]) for f in the_fields ]
        the_initial_values = "\n".join(the_initial_values)
        # print(the_initial_values)


        # TODO: function modifies x as well as y. Harmless but messy.
        y = regex_dict(x, the_fields, the_search_pattern, the_replace_pattern)


        the_new_values = [ str('{' + f + '_new:} ' + y[f] + ' ') for f in the_fields ]
        the_new_values = "\n".join(the_new_values)

        the_before_afters.append([repo, asid,an_obj[1], the_initial_values, the_new_values ])

        # convert dict back to json for posting.
        z = json.dumps(y)


        # Post the fixed object back to API.
        # (Comment out these lines to test output without replacing.)
        post = asf.postArchivalObject(repo,asid,z)
        print(post)

    # Report changes to Google Sheet

    print('Writing before/after info to sheet...')
    the_report_sheet.clear()
    the_report_sheet.appendData(the_before_afters)

    print("Done!")


def regex_dict(dict,elements,pattern1, pattern2):
    # Perform regex replace on select items within a dict.
    dict_out = dict 
    for e in elements:
        if e in dict:
            dict_out[e] = re.sub(pattern1, pattern2, dict[e], re.MULTILINE)
    return dict_out





if __name__ == '__main__':
    main()
