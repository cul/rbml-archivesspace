# Script to add encoded languages based on language terms in lang_materials text notes.
# See ACFA-163.

import ASFunctions as asf
import re
from sheetFeeder import dataSheet
import json
from language_encode_lookup import language_codes


def main():

    asf.setServer("Prod")

    # the_lookup_csv = "id_lookup_TEST.csv"  # test
    the_lookup_csv = "id_lookup_prod.csv"  # test

    output_folder = "output/resource_language_encode"

    the_sheet = dataSheet("1eTPY7AbDvjDU-lzK2VQruvZAvlGkAJZglh2JrruPvdg", "Test6!A:Z")

    the_data = the_sheet.getData()

    the_new_data = []
    the_new_data.append(the_data.pop(0))

    counter = 0

    for a_row in the_data:

        counter += 1
        print(" ")
        print(counter)

        the_new_row = a_row
        the_bibid = a_row[0]
        the_041 = a_row[1]
        the_string = a_row[3]

        res_info = asf.lookupByBibID(the_bibid, the_lookup_csv)

        if res_info:
            out_path_old = (
                output_folder
                + "/"
                + str(res_info[0])
                + "_"
                + str(res_info[1])
                + "_old.json"
            )
            out_path_new = (
                output_folder
                + "/"
                + str(res_info[0])
                + "_"
                + str(res_info[1])
                + "_new.json"
            )

            # pull down the resource
            the_resource = asf.getResource(res_info[0], res_info[1])

            # Save copy of existing object
            print("Saving data to " + out_path_old + "....")

            with open(out_path_old, "w+") as f:
                f.write(the_resource)

            res_dict = json.loads(the_resource)

            langmaterials = res_dict["lang_materials"]

            # Collect encoded languages already present. There should be just one but not guaranteed, so make a list.
            primary_langs = []
            for n in langmaterials:
                try:
                    if n["language_and_script"]:
                        # print("YES")
                        primary_langs.append(n["language_and_script"]["language"])
                except:
                    print("Exception!")

            print("old:")
            print(primary_langs)

            print("new:")
            langs_parsed = language_lookup(the_string)
            print(langs_parsed)

            print("to add: ")
            langs_diff = diff(langs_parsed, primary_langs)
            print(langs_diff)

            if len(langs_diff) > 0:

                for l in langs_diff:
                    res_dict["lang_materials"].append(make_language_note(l))

                new_resource = json.dumps(res_dict)
                # Save new object
                print("Saving data to " + out_path_new + "....")

                with open(out_path_new, "w+") as f:
                    f.write(new_resource)

                # Post new resource back to API

                print("Posting data for " + str(res_info[0]) + " : " + str(res_info[1]))
                try:
                    post = asf.postResource(res_info[0], res_info[1], new_resource)
                    print(post)
                except:
                    print(
                        "Error: There was a problem posting resource "
                        + str(res_info[0])
                        + ":"
                        + str(res_info[1])
                        + "!"
                    )
                    langs_diff.append("[ERROR]")

            else:
                print("No new languages to add. Skipping.")

            the_new_row.append(",".join(langs_diff))
            the_new_data.append(the_new_row)

    the_sheet.clear()
    the_sheet.appendData(the_new_data)


def language_lookup(a_string):

    the_words = re.sub(r"[\W]", " ", a_string).split()

    the_matches = []

    for w in the_words:
        for l in language_codes:
            if w == l["name"]:
                the_matches.append(l["code"])
    # the_matches = list(set(the_matches))
    return the_matches


def make_language_note(lang_code):
    new_note = {
        "jsonmodel_type": "lang_material",
        "notes": [],
        "language_and_script": {
            "language": lang_code,
            "jsonmodel_type": "language_and_script",
        },
    }
    return new_note


def diff(first, second):
    # Return list of x - y (everything in x that is not in y). Reverse order to get inverse diff.
    second = set(second)
    the_diff = [item for item in first if item not in second]
    # return the unique items in the diff as a list.
    return list(set(the_diff))


if __name__ == "__main__":
    main()

