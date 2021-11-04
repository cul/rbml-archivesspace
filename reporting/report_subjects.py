import ASFunctions as asf
import json
import os.path
from pprint import pprint
from sheetFeeder import dataSheet
import dpath.util
import datetime
import dcps_utils as util
import digester  # for generating composite digest of report info.


my_name = __file__
script_name = os.path.basename(my_name)


# This makes sure the script can be run from any working directory and still find related files.
my_path = os.path.dirname(__file__)

sheet_id = "1pZk2tPMuZDOd1veOBSJNRk2fprA6p3Qb3WKZDtZay88"
the_sheet = dataSheet(sheet_id, "subjects!A:Z")
# the_sheet = dataSheet(sheet_id, "test!A:Z") # test

now1 = datetime.datetime.now()
start_time = str(now1)
end_time = ""  # set later


# First get the subject records from API (this can take a long time!)

asf.setServer("Prod")  # AS instance: Prod | Dev | Test


# out_path = os.path.join(my_path, "output/subjects.pickle")
out_path = "/cul/cul0/ldpd/archivesspace/subjects/subjects.pickle"

# uncomment to do the full download.
the_subjects = asf.getSubjects()
util.pickle_it(the_subjects, out_path)


# Report the saved data to Google Sheet

# List of fields to extract, expressed as dpaths.
the_fields = [
    ["uri", "uri"],
    ["title", "title"],
    ["source", "source"],
    ["authority_id", "authority_id"],
    # ["vocabulary", "terms/0/vocabulary"],
    ["is_linked_to_published_record", "is_linked_to_published_record"],
    ["publish", "publish"],
    ["last_modified_by", "last_modified_by"],
    ["last_modified", "system_mtime"],
]

# Read from the pickle into list.
the_subject_data = util.unpickle_it(out_path)

the_heads = [x[0] for x in the_fields]
the_output = [the_heads]

subj_cnt = len(the_subject_data)

for s in the_subject_data:
    the_row = []
    # Use dpath to extract values from dict and compose into rows.
    for af in the_fields:
        try:
            d = str(dpath.util.get(s, af[1]))
        except:
            d = ""
        the_row.append(d)
    # print(the_row)

    # Handle subclassifications
    if 'terms' in s:
        the_terms = s['terms']
        for t in the_terms:
            the_row.append(t['term'] + ' [' + t['term_type'] + ']')

    the_output.append(the_row)

the_sheet.clear()
save = the_sheet.appendData(the_output)
print(save)
digester.post_digest(
    script_name, "Total subject records: " + str(len(the_output)-1))


# Generate log

now2 = datetime.datetime.now()
end_time = str(now2)
my_duration = str(now2 - now1)


the_log = (
    str(subj_cnt)
    + " subject records imported by "
    + my_name
    + ". "
    + " Start: "
    + start_time
    + ". Finished: "
    + end_time
    + " (duration: "
    + my_duration
    + ")."
)


log_range = "log!A:A"
log_sheet = dataSheet(sheet_id, log_range)

log_sheet.appendData([[the_log]])

print(" ")

print(the_log)


print(" ")

exit_msg = "Script done. Updated data is available at " + \
    "https://docs.google.com/spreadsheets/d/" + \
    str(sheet_id) + "/edit?usp=sharing"
print(exit_msg)
digester.post_digest(script_name, exit_msg)
