# Script to add on-site access notes to resources. See ACFA-154.

import ASFunctions as asf
import csv
import json
from pprint import pprint


def main():
    # Main code goes here.

    asf.setServer("Prod")

    output_folder = "output/resource_on-site_access"

    lookup_csv = "id_lookup_prod.csv"

    bibid_file = "/Users/dwh2128/Documents/ACFA/TEST/ACFA-154-add-onsite-note/acfa-154-add_onsite_note.csv"

    # Read a list of bibids (csv)
    the_bibids = []
    with open(bibid_file) as ids:
        for row in csv.reader(ids):
            the_bibids.append(row[0])

    the_access_note = {
        "jsonmodel_type": "note_multipart",
        "label": "Restrictions on Access",
        "type": "accessrestrict",
        "rights_restriction": {"local_access_restriction_type": []},
        "subnotes": [
            {
                "jsonmodel_type": "note_text",
                "content": "This collection is located on-site.",
                "publish": True,
            }
        ],
        "publish": True,
    }

    for bib in the_bibids:

        repo, asid = asf.lookupByBibID(bib, lookup_csv)

        out_path_old = output_folder + "/" + str(repo) + "_" + str(asid) + "_old.json"
        out_path_new = output_folder + "/" + str(repo) + "_" + str(asid) + "_new.json"

        the_resource = asf.getResource(repo, asid)

        # Save copy of existing object
        print("Saving data to " + out_path_old + "....")

        with open(out_path_old, "w+") as f:
            f.write(the_resource)

        the_data = json.loads(the_resource)

        # Test if there is already an access restriction note.
        has_note = False
        for a_note in the_data["notes"]:
            if a_note["type"] == "accessrestrict":
                has_note = True

        if has_note == True:
            print("Already has note -- skipping.")
        else:
            the_data["notes"].append(the_access_note)

            the_new_resource = json.dumps(the_data)

            # Save copy of new object
            print("Saving data to " + out_path_new + "....")

            with open(out_path_new, "w+") as f:
                f.write(the_new_resource)

            post = asf.postResource(repo, asid, the_new_resource)
            print(post)

    quit()


# Functions go here.

if __name__ == "__main__":
    main()

