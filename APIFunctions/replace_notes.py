import ASFunctions as asf
import json
from pprint import pprint
import re
import csv
from GoogleSheetAPITools import dataSheet

# Script to take a list of uids for archival objects and remove any notes with subnotes containing <extref> xml elements.

def main():

    # Set to Test | Dev | Prod
    asf.setServer('Prod')

    the_report_sheet=dataSheet('1wNO0t2j5G9U0hUmb7E-jLd4T5skTs1aRxN7HrlyZwEI','notes!A:Z')


    id_file = 'replace_notes.csv'
    output_folder = 'output/notes'

    # Read a list of repo and object ids (csv)
    the_ids = []
    ids = open(id_file)
    for row in csv.reader(ids):
        the_ids.append([row[0],row[1]])
    ids.close()



    the_before_afters = []


    the_heads = ['repo', 'asid', 'uid', 'title', 'note_cnt1', 'note_cnt2', 'status']

    the_before_afters.append(the_heads)

    for an_obj in the_ids:

        out_path = output_folder + '/' + an_obj[0] + '_' + an_obj[1] + '_old.json'

        # read from API
        print('getting data for ' + str(an_obj[0]) + ', ' + str(an_obj[1]))

        try:
            x = asf.getArchivalObjectByRef(an_obj[0],an_obj[1])

            # Save copy of existing object
            print('Saving data to ' + out_path + '....')

            f = open(out_path, "w+")
            f.write(x)
            f.close()

            x = json.loads(x)


            asid = str(x['uri'].split('/')[-1]) # get the asid from the uri string.

            title = x['title']

            repo = str(an_obj[0])

            y = x


            my_notes_init = y['notes']
            my_notes_new = []

            if len(my_notes_init) > 0:
                if 'subnotes' in my_notes_init[0]:

                    for a_note in my_notes_init:
                        if 'subnotes' in a_note:
                            if 'extref' in a_note['subnotes'][0]['content']:
                                pass
                            else:
                                my_notes_new.append(a_note)

            if len(my_notes_new) == len(my_notes_init):
                the_status = "[no change]"
            else:
                the_status = "[deleted note]"


            y['notes'] = my_notes_new
            note_cnt1 = len(my_notes_init)
            note_cnt2 = len(y['notes'])


            the_before_afters.append([an_obj[0], asid, an_obj[1], title, note_cnt1, note_cnt2, the_status ])


            # convert dict back to json for posting.
            z = json.dumps(y)

            # Post the fixed object back to API.
            # (Comment these out for testing.)
            resp = asf.postArchivalObject(repo,asid,z)
            print(resp)

        except:
            print('Could not retrieve record ' + str(an_obj[1]))
            


    # Report changes to Google Sheet
    print('Writing before/after info to sheet...')

    the_report_sheet.clear()
    the_report_sheet.appendData(the_before_afters)


    print("Done!")

    quit()





if __name__ == '__main__':
    main()


