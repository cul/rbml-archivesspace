# Script to export all resources from a list of repos for reporting purposes.
# See ACFA-177.

import ASFunctions as asf
import json
from pprint import pprint
import dpath.util
from sheetFeeder import dataSheet
import os.path
from datetime import datetime, date, timedelta
from shutil import make_archive, move, rmtree
import digester  # for generating composite digest of report info.


def main():
    # Main code goes here.

    # set to True to use test sheet and test json folder location.
    debug = False

    asf.setServer("Prod")

    my_name = __file__
    script_name = os.path.basename(my_name)

    # This makes sure the script can be run from any working directory and still find related files.
    my_path = os.path.dirname(__file__)

    now1 = datetime.now()
    start_time = str(now1)
    end_time = ""  # set later
    today_str = str((date.today()).strftime("%Y%m%d"))

    if debug == True:
        print("[Running script in debug mode...]")
        parent_folder = "/cul/cul0/ldpd/archivesspace/test/resources"  # test folder
        sheet_id = "1wFyLN_Ea7ExCZSMuksB8MTrS9DjsUkwsmaPBujL7x0U"  # test sheet
        the_repos = [4]  # to test
    else:
        parent_folder = "/cul/cul0/ldpd/archivesspace/resources"
        sheet_id = "1T3EpIZmnh3Gk-VAIGtvavTQUIpS7AluyKQ8-sJsS8vg"
        the_repos = [2, 3, 4, 5]

    output_folder = parent_folder + "/" + today_str

    the_sheets = {
        "resources": dataSheet(sheet_id, "Resources!A:Z"),
        "cm": dataSheet(sheet_id, "Collection Management!A:Z"),
        "log": dataSheet(sheet_id, "log!A:Z"),
    }

    # Set number of chars to truncate the scope and bioghist notes.
    trunc_len = 400

    # List of fields to extract, expressed as dpaths.
    the_fields = [
        ["bibid", "/id_0"],
        ["title", "/title"],
        ["published", "/publish"],
        ["create_time", "/create_time"],
        ["system_mtime", "/system_mtime"],
        ["created_by", "/created_by"],
        ["last_modified_by", "/last_modified_by"],
        ["ead_location", "/ead_location"],
        ["ext_number", "/extents/0/number"],
        ["ext_portion", "/extents/0/portion"],
        ["ext_type", "/extents/0/extent_type"],
        # ["integer_1", "/user_defined/integer_1"],
        # ["integer_2", "/user_defined/integer_2"],
        # ["integer_3", "/user_defined/integer_3"],
        ["local call no.", "/user_defined/string_1"],
        ["other ctrl no. 1", "/user_defined/string_2"],
        ["other ctrl no. 2", "/user_defined/string_3"],
        ["other ctrl no. 3", "/user_defined/string_4"],
        # ["enum_1", "/user_defined/enum_1"],
        # ["enum_2", "/user_defined/enum_2"],
        ["description status", "/user_defined/enum_3"],
        ["collecting area", "/user_defined/enum_4"],
        # (Scope and bioghist notes are added in separately below.)
    ]

    # Get the collection management records for use in report.

    the_cms = []

    fields = [
        "id",
        "parent_id",
        "title",
        "system_mtime",
        "processing_priority",
        "processing_status",
    ]

    print(" ")
    print("*** Retrieve Collection Management Data ***")
    print(" ")

    for r in the_repos:
        print("Getting collection management records for repo: " + str(r) + "...")
        cm = asf.getCollectionManagements(r, filter="resource", fields=fields)
        for c in cm:
            row = [c[f] for f in fields]
            the_cms.append(row)

    # a data set of collection managment records to post to sheet below.
    the_cms.insert(0, fields)

    print(" ")
    print("*** Retrieve Resource Data ***")
    print(" ")

    # Get the list of resources for each repo and add to the_ids
    the_ids = []
    for r in the_repos:
        print("Getting ids for repo: " + str(r) + "...")
        asids = json.loads(
            asf.getResponse("/repositories/" + str(r) +
                            "/resources?all_ids=true")
        )

        print(str(len(asids)) + " records found in repo " + str(r) + ".")
        for i in asids:
            the_ids.append([r, i])

    # Construct the head row
    the_heads = [x[0] for x in the_fields]
    the_heads.insert(0, "asid")
    the_heads.insert(0, "repo")
    the_heads.append("scope note")
    the_heads.append("scopenote length")

    the_heads.append("bioghist note")
    the_heads.append("biognote length")

    the_output = [the_heads]

    # Fetch the resources from the ids
    print("Downloading resources...")

    if not os.path.exists(output_folder):
        print("Creating directory " + output_folder + "...")
        os.makedirs(output_folder)

    for repo, asid in the_ids:
        # print("Processsing " + str(repo) + ":" + str(asid) + "...")
        the_row = [repo, asid]
        res_json = asf.getResource(repo, asid)
        res_dict = json.loads(res_json)

        out_path = output_folder + "/" + str(repo) + "_" + str(asid) + ".json"

        # Write the JSON to file.
        with open(out_path, "w+") as f:
            f.write(res_json)

        # Use dpath to extract values from dict and compose into rows.
        for af in the_fields:
            try:
                d = str(dpath.util.get(res_dict, af[1]))
            except:
                d = ""
            the_row.append(d)

        # Process scope and bioghist notes

        the_notes = dpath.util.values(res_dict, "notes/*", afilter=None)

        the_scope_notes = []
        the_biog_notes = []

        for a_note in the_notes:
            try:
                if a_note["type"] == "scopecontent":
                    the_scope_notes.append(a_note)
            except:
                pass
            try:
                if a_note["type"] == "bioghist":
                    the_biog_notes.append(a_note)
            except:
                pass

        if len(the_scope_notes) > 0:
            # If there are scope notes, grab all the text and concatenate. Then get the total length in # chars.
            scope_note_texts = [s["subnotes"][0]["content"]
                                for s in the_scope_notes]
            the_scope_text = " ".join(scope_note_texts)
            scope_note_len = len(the_scope_text)

            scope_note_short = truncate_str(
                the_scope_text, length=trunc_len
            )
        else:
            scope_note_short = ""
            scope_note_len = 0

        if len(the_biog_notes) > 0:
            # If there are bioghist notes, grab all the text and concatenate. Then get the total length in # chars.
            biog_note_texts = [s["subnotes"][0]["content"]
                               for s in the_biog_notes]
            the_biog_text = " ".join(biog_note_texts)
            biog_note_len = len(the_biog_text)

            biog_note_short = truncate_str(the_biog_text, length=trunc_len
                                           )
        else:
            biog_note_short = ""
            biog_note_len = 0

        the_row.append(scope_note_short)
        the_row.append(str(scope_note_len))
        the_row.append(biog_note_short)
        the_row.append(str(biog_note_len))

        the_output.append(the_row)

    # Zip up the JSON files for storage.
    zip_out = make_archive(
        today_str, "zip", root_dir=parent_folder, base_dir=today_str)

    print(zip_out)

    # Zip is saved in working dir; move to correct location.
    print("Saving zip file " + str(today_str) + ".zip to " + parent_folder)

    # Test if file already exists.
    if os.path.exists(parent_folder + "/" + str(today_str) + ".zip"):
        print(
            "File "
            + parent_folder
            + "/"
            + str(today_str)
            + ".zip exists already. Replacing with new zip file..."
        )

        os.remove(parent_folder + "/" + str(today_str) + ".zip")

    move(zip_out, parent_folder)

    # Remove the json folder once zip is in place.
    rmtree(parent_folder + "/" + today_str)

    # Write output to Google sheet.

    print(" ")
    print("*** Writing Data to Report ***")
    print(" ")

    the_sheets["cm"].clear()
    the_sheets["cm"].appendData(the_cms)
    digester.post_digest(
        script_name, "Total collection management records: " + str(len(the_cms) - 1))

    the_sheets["resources"].clear()
    the_sheets["resources"].appendData(the_output)
    digester.post_digest(
        script_name, "Total number of resource records: " + str(len(the_output) - 1))

    ########################
    ### FINISH UP ###
    ########################

    # Generate log string.
    now2 = datetime.now()
    end_time = str(now2)
    my_duration = str(now2 - now1)

    the_log = (
        "Data imported by "
        + my_name
        + ". Start: "
        + start_time
        + ". Finished: "
        + end_time
        + " (duration: "
        + my_duration
        + ")."
    )

    the_sheets["log"].appendData([[the_log]])

    print(" ")

    print(the_log)

    print(" ")

    exit_msg = "Script done. Updated data is available at " + \
        the_sheets["resources"].url
    print(exit_msg)
    digester.post_digest(script_name, exit_msg)


# Functions go here.


def truncate_str(string, length=400):
    new_str = (string[:length] + "...") if len(string) > length else string
    return new_str


if __name__ == "__main__":
    main()
