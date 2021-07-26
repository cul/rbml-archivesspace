# Script to add authorities or make other changes to subjects. See ACFA-287.

import ASFunctions as asf
import json
from pprint import pprint
from sheetFeeder import dataSheet
import os.path


SERVER = "Prod"
# SERVER = "Test"
asf.setServer(SERVER)

MY_NAME = __file__

# This makes sure the script can be run from any working directory and still find related files.
MY_PATH = os.path.dirname(__file__)


def main():

    sheet_id = "1GEeNpKBhfjOCJGx1zJfi6XgZ4OWhGhzWsOHRT9DkmpY"

    # list_sheet = dataSheet(sheet_id, 'Test!A:Z')  # test
    list_sheet = dataSheet(sheet_id, "batch!A:Z")
    report_sheet = dataSheet(sheet_id, "output!A:Z")

    the_uris = list_sheet.getDataColumns()[0]

    output_data = []
    for uri in the_uris:
        asid = uri.split("/")[3]
        x = fix_agent(asid, "families")
        pprint(x["display_name"])
        res = asf.postAgent(asid, json.dumps(x), agent_type="families")
        print(res)
        row = [SERVER, uri, str(res)]
        output_data.append(row)

    print(output_data)

    report_sheet.appendData(output_data)

    quit()


def fix_agent(asid, agent_type):
    x = json.loads(asf.getAgent(asid, agent_type=agent_type))

    for name in x["names"]:
        print(name)
        if name["is_display_name"] == True:
            name["source"] = "local"
            name["rules"] = "dacs"

    x["display_name"]["source"] = "local"
    x["display_name"]["rules"] = "dacs"

    return x


if __name__ == "__main__":
    main()
