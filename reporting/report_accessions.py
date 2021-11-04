# Automated reporting of ArchivesSpace accessions info.

import ASFunctions as asf
import json
from pprint import pprint
from sheetFeeder import dataSheet
from operator import itemgetter
import datetime
import re
import os.path
import dateutil.parser
import digester  # for generating composite digest of report info.


# set Prod | Dev | Test
target_server = 'Prod'  # Prod | Dev | Test
asf.setServer(target_server)

DEBUG = False
# mode = 'Prod'  # Prod or Test

MY_NAME = __file__
SCRIPT_NAME = os.path.basename(MY_NAME)

# This makes sure the script can be run from any working directory and still find related files.
MY_PATH = os.path.dirname(__file__)

# File to use to lookup bibids
LOOKUP_CSV = os.path.join(MY_PATH, "id_lookup_prod.csv")


def main():
    now1 = datetime.datetime.now()
    start_time = str(now1)
    end_time = ''  # set later
    # day_offset = now1.weekday() + 1 # Calculate the Sunday of current week
    day_offset = 7  # use past seven days, regardless of current day

    print('Script ' + MY_NAME + ' begun at ' + start_time + '. ')

    if not DEBUG:
        the_sheet_id = '1JA5bRSnYV80sx4m5SOFQ6QJ4u21SXvQeNdNbuRVCdds'
    else:
        the_sheet_id = '1e_TAK8eUsaHltBu9J5bNO1twThqt7_nE5olmz2pdCUw'  # test doc
        day_offset = 14  # use past 2 weeks for testing

    # Set date stamp of start of week (Sunday) to determine recently created accessions.
    begin_of_week = (now1 - datetime.timedelta(day_offset)).date()

    the_sheet_rbml = dataSheet(the_sheet_id, 'rbml!A:Z')
    the_sheet_avery = dataSheet(the_sheet_id, 'avery!A:Z')
    the_sheet_rbmlbooks = dataSheet(the_sheet_id, 'rbmlbooks!A:Z')

    # Location to save output
    if DEBUG is True:
        out_folder = "/cul/cul0/ldpd/archivesspace/test/accessions"
    else:
        out_folder = "/cul/cul0/ldpd/archivesspace/accessions"

    rbml_acc_file = os.path.join(out_folder, 'report_rbml_accessions.json')
    avery_acc_file = os.path.join(out_folder, 'report_avery_accessions.json')
    rbmlbooks_acc_file = os.path.join(
        out_folder, 'report_rbmlbooks_accessions.json')

    print(' ')

    print('Starting accession report in ' + 'https://docs.google.com/spreadsheets/d/' +
          str(the_sheet_id) + '/edit?usp=sharing')

    if not DEBUG:
        # Save the accessions as json files. In DEBUG mode, just use the files already saved.
        print('Saving Avery accession data to ' + avery_acc_file + '....')

        # Only fetch file if not in Debug mode
        with open(avery_acc_file, "w+") as f:
            try:
                x = asf.getAccessions(3)
                f.write(x)
            except:
                raise ValueError(
                    "There was an error in getting Avery accession data!")

            y = json.loads(x)
            if 'error' in y[0]:
                print(y[0]['error'])

        print('Saving RBML accession data to ' + rbml_acc_file + '....')

        with open(rbml_acc_file, "w+") as f:
            try:
                x = asf.getAccessions(2)
                f.write(x)
            except:
                raise ValueError(
                    "There was an error in getting RBML accession data!")

            y = json.loads(x)
            if 'error' in y[0]:
                print(y[0]['error'])

        print('Saving RBMLBOOKS accession data to ' +
              rbmlbooks_acc_file + '....')

        with open(rbmlbooks_acc_file, "w+") as f:
            try:
                x = asf.getAccessions(6)
                f.write(x)
            except:
                raise ValueError(
                    "There was an error in getting RBMLBOOKS accession data!")

            y = json.loads(x)
            if 'error' in y[0]:
                print(y[0]['error'])

    print(' ')

    # the_files = [
    #         [avery_acc_file, the_sheet_avery],
    #         [rbml_acc_file, the_sheet_rbml]
    #              ]

    the_recents = {}

    the_info = [{'repo_name': 'Avery',
                 'repo_id': 3,
                 'acc_file': avery_acc_file,
                 'the_sheet': the_sheet_avery
                 },
                {'repo_name': 'RBML',
                 'repo_id': 2,
                 'acc_file': rbml_acc_file,
                 'the_sheet': the_sheet_rbml
                 },
                {'repo_name': 'RBMLBOOKS',
                 'repo_id': 6,
                 'acc_file': rbmlbooks_acc_file,
                 'the_sheet': the_sheet_rbmlbooks
                 }
                ]

    # The top-level elements to save from the JSON (each can be further processed below)
    the_keys = {
        "title": "title",
        "uri": "uri",
        "repository": "repository",
        "accession_date": "accession_date",
        "id_0": "id_0",
                "id_1": "id_1",
                "id_2": "id_2",
                "id_3": "id_3",
                "extents": "extents",
                "related_resources": "related_resources",
                "collection_management": "collection_management",
                "user_defined": "user_defined",
                "create_time": "create_time",
                "system_mtime": "system_mtime",
                "last_modified_by": "last_modified_by"
    }

    ext_dict = {"ext-number": "number",
                "ext-portion": "portion",
                "ext-type": "extent_type"}
    for f in the_info:

        the_file = f['acc_file']
        the_target = f['the_sheet']
        repo_name = f['repo_name']

        with open(the_file) as f:
            the_data = json.load(f)

        all_rows = []

        for an_accession in the_data:
            # acc_info : prelim dict for each accession. Do things to it.
            acc_info = {}
            for key, value in the_keys.items():
                try:
                    acc_info.update({key: an_accession[value]})
                except (IndexError, KeyError):
                    acc_info.update({key: ""})

            # Refine elements by extracting subelements, etc.

            # Handle collection_management
            cm = acc_info["collection_management"]
            cm_dict = {"processing_priority": "processing_priority",
                       "processing_status": "processing_status"}
            for key, value in cm_dict.items():
                try:
                    acc_info[key] = cm[value]

                except (IndexError, KeyError, TypeError):
                    acc_info[key] = ''

            acc_info.pop("collection_management")

            # Parse resource id and get bibid
            res = acc_info["related_resources"]
            if len(res) > 0:
                res_url = res[0]["ref"]
                repo = res_url.split('/')[2]
                asid = res_url.split('/')[4]
                bibid = asf.lookupBibID(repo, asid, LOOKUP_CSV)
            else:
                bibid = ''
                asid = ''
            acc_info["resource_bibid"] = bibid
            acc_info["resource_asid"] = asid
            acc_info.pop("related_resources")

            # Parse BibID out of user_defined / integer_1
            try:
                usdef = acc_info["user_defined"]
                acc_info['integer_1'] = usdef['integer_1']
            except:
                acc_info['integer_1'] = ''
            acc_info.pop("user_defined")

            # Fix problem with leading "+" in id_3 (add apostrophe for display)
            acc_info["id_3"] = re.sub(r"^\+", "'+", acc_info["id_3"])

            # Handle repository
            repository = acc_info["repository"]
            if len(repository) > 0:
                repo_url = repository["ref"]
                repo = repo_url.split('/')[2]
            else:
                repo = ''
            acc_info["repo"] = repo
            acc_info.pop("repository")

            # Handle date
            acc_date = acc_info["accession_date"]
            yyyy = int(acc_date.split('-')[0])
            mm = int(acc_date.split('-')[1])
            dd = int(acc_date.split('-')[2])
            the_date = datetime.date(yyyy, mm, dd)
            # due to legacy import issue, some with unknown dates have malformed dates like 0002-01-23. Acknowledge their unknownness.
            if the_date.year < 1700:
                acc_info["accession_date"] = "0000-00-00"
                acc_info["year"] = ""
            else:
                acc_info["year"] = the_date.year

            # Fiscal year
            if the_date.year < 1700:
                acc_info["fiscal-year"] = ""
            else:
                if the_date.month > 6:
                    acc_info["fiscal-year"] = the_date.year + 1
                else:
                    acc_info["fiscal-year"] = the_date.year

            # Handle extents
            ext = acc_info["extents"]
            for key, value in ext_dict.items():
                try:
                    acc_info[key] = ext[0][value]
                except (IndexError, KeyError):
                    acc_info[key] = ''

            acc_info.pop("extents")

            # Clean up titles
            acc_info['title'] = str(acc_info['title']).strip()

            # Uncomment to list records in log.
            # print("processing: " + str(acc_info["uri"]).strip() + ' / ' + str(acc_info["title"]).strip() )

            all_rows.append(acc_info)

        processed_msg = 'Processed ' + \
            str(len(all_rows)) + ' records in ' + repo_name + '.'
        print(processed_msg)

        log_it(SCRIPT_NAME, processed_msg)

        # the_heads = list(all_rows[0].keys())

        # explicitly order the columns, as dict order is unpredictable.
        the_heads = ['title',
                     'uri',
                     'accession_date',
                     'id_0',
                     'id_1',
                     'id_2',
                     'id_3',
                     'integer_1',
                     'resource_bibid',
                     'resource_asid',
                     'repo',
                     'year',
                     'fiscal-year',
                     'ext-number',
                     'ext-portion',
                     'ext-type',
                     'processing_priority',
                     'processing_status',
                     'create_time',
                     'system_mtime',
                     'last_modified_by']

        the_output = []

        # Build row in order specified by the_heads
        for a_row in all_rows:
            # r = list(a_row.values())
            r = [a_row[h] for h in the_heads]
            the_output.append(r)
            # print(a_row)

        # sort by accession_date (the 2nd item in inner lists)
        the_output = sorted(the_output, key=itemgetter(2), reverse=True)

        # Get list of recents
        the_recents[repo_name] = []

        for i in the_output:
            # i[18] = the create date column
            i_date = dateutil.parser.isoparse(i[18]).date()

            if i_date > begin_of_week:

                the_recents[repo_name].append(i)

        # If there are recents, list them
        if the_recents[repo_name]:
            print(' ')
            recent_msg = str(len(the_recents[repo_name])) + \
                ' accessions recently added in ' + repo_name + ': '
            print(recent_msg)
            log_it(SCRIPT_NAME, recent_msg)
            print('-----------')
            for r in the_recents[repo_name]:
                print(r[0])
                print(r[1])
                print('Created ' + str(dateutil.parser.isoparse(r[18]).date()))
                print('Last edited by ' + r[20])
                print('-----------')
        else:
            print(' ')
            recent_msg = 'No recently created accessions in ' + repo_name
            print(recent_msg)
            log_it(SCRIPT_NAME, recent_msg)

            # print(the_recents[repo_name])

        the_output.insert(0, the_heads)

        print(' ')

        the_target.clear()

        print('Writing ' + repo_name + ' data to sheet ...')
        the_target.appendData(the_output)

        print(' ')

    # generate log and add to log tab, if exists.
    the_tabs = the_target.initTabs

    now2 = datetime.datetime.now()
    end_time = str(now2)
    my_duration = str(now2 - now1)

    if DEBUG is True:
        the_log = '[TEST] Data imported from ' + target_server + ' by ' + MY_NAME + '. Start: ' + \
            start_time + '. Finished: ' + end_time + \
            ' (duration: ' + my_duration + ').'
    else:
        the_log = 'Data imported from ' + target_server + ' by ' + MY_NAME + '. Start: ' + \
            start_time + '. Finished: ' + end_time + \
            ' (duration: ' + my_duration + ').'

    if 'log' in the_tabs:
        log_range = 'log!A:A'
        # today = datetime.datetime.today().strftime('%c')
        dataSheet(the_sheet_id, log_range).appendData([[the_log]])
    else:
        print('*** Warning: There is no log tab in this sheet. ***')

    print(' ')

    print(the_log)
    log_it(SCRIPT_NAME, the_log)

    print(' ')

    exit_msg = 'Script done. Updated data is available at ' + \
        'https://docs.google.com/spreadsheets/d/' + \
        str(the_sheet_id) + '/edit?usp=sharing'
    print(exit_msg)
    log_it(SCRIPT_NAME, exit_msg)
    # fin


def log_it(script, log):
    if DEBUG is not True:
        digester.post_digest(script, log)


if __name__ == "__main__":
    main()
