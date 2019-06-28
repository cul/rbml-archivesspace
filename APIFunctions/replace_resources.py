# Script to replace text in a designated field in a resource and post the resource back to API.
# Requirements:
# - ASFunctions.py
# - A csv of format repo,asid
# - GoogleSheetAPITools (optional, for reporting purposes)

import ASFunctions as asf
import json
from pprint import pprint
import re
import csv
import GoogleSheetAPITools as gs


def main():

    asf.setServer('Test')

    # Google sheet used for reporting changes.
    the_sheet = '1wNO0t2j5G9U0hUmb7E-jLd4T5skTs1aRxN7HrlyZwEI'
    the_range = 'resources!A:Z'


    id_file = 'resource_replacements.csv'
    output_folder = 'output/resource_replacements'

    # Read a list of repo and object ids (csv)
    the_ids = []
    ids = open(id_file)
    for row in csv.reader(ids):
        the_ids.append([row[0],row[1]])
    ids.close()

    # Search/replace patterns
    the_search_pattern = 'NCC'
    the_replace_pattern = 'NNC'

    the_before_afters = []


    the_heads = ['repo', 'asid','before', 'after']

    the_before_afters.append(the_heads)

    for an_obj in the_ids:

        out_path = output_folder + '/' + an_obj[0] + '_' + an_obj[1] + '_old.json'

        # read from API
        x = asf.getResource(an_obj[0],an_obj[1])


        # Save copy of existing object
        print('Saving data to ' + out_path + '....')

        f = open(out_path, "w+")
        f.write(x)
        f.close()

        x = json.loads(x)


        the_old_field_data = x['user_defined']['string_2']


        y = x

        y['user_defined']['string_2'] = re.sub(the_search_pattern, the_replace_pattern, x['user_defined']['string_2'])

        if y['user_defined']['string_2'] == the_old_field_data:
            the_new_field_data = "[no change]"
        else:
            the_new_field_data = y['user_defined']['string_2']

        the_before_afters.append([an_obj[0], an_obj[1], '{string_2} ' + the_old_field_data, '{string_2} ' + the_new_field_data ])

        # convert dict back to json for posting.
        z = json.dumps(y)


        # Post the fixed object back to API.
        post = asf.postResource(an_obj[0], an_obj[1], z)
        print(post)


        

    # Report changes to Google Sheet
    

    print('Writing before/after info to sheet...')
    gs.sheetClear(the_sheet,the_range)
    gs.sheetAppend(the_sheet,the_range,the_before_afters)






if __name__ == '__main__':
    main()
