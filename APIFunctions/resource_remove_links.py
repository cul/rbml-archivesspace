# Script to remove extraneous finding aid links when there is no finding aid (see ACFA-161).

import ASFunctions as asf
import re
import json
import csv
from pprint import pprint
import sys


def main():
    # Main code goes here.

    asf.setServer("Prod")

    output_folder = "output/resource_remove_links"
    the_lookup_csv = "id_lookup_prod.csv"
    bibid_file = "/Users/dwh2128/Documents/ACFA/TEST/ACFA-161-remove-links/acfa-161-remove-links.txt"

    # Read a list of bibids (csv)
    the_bibids = []
    with open(bibid_file) as ids:
        for row in csv.reader(ids):
            the_bibids.append(row[0])

    for b in the_bibids:

        try:
            repo, asid = asf.lookupByBibID(b, the_lookup_csv)
            print("Processing " + str(b) + "...")

            out_path_old = (
                output_folder + "/" + str(repo) + "_" + str(asid) + "_old.json"
            )
            out_path_new = (
                output_folder + "/" + str(repo) + "_" + str(asid) + "_new.json"
            )

            x = asf.getResource(repo, asid)

            # Save copy of existing object
            print("Saving data to " + out_path_old + "....")
            with open(out_path_old, "w+") as f:
                f.write(x)

            x_dict = json.loads(x)
            print(x_dict["ead_location"])
            if "ead_location" in x_dict:
                del x_dict["ead_location"]
            else:
                print("No URL to delete!")

            y = json.dumps(x_dict)
            # print(y)

            post = asf.postResource(repo, asid, y)
            print(post)

            # Save copy of new object
            print("Saving data to " + out_path_new + "....")

            with open(out_path_new, "w+") as f:
                f.write(y)

        except:
            print("Error: Could not process " + str(b))
            print(sys.exc_info())
            # raise

    quit()


# Functions go here.

if __name__ == "__main__":
    main()

