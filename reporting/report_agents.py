import ASFunctions as asf
import json
import os.path
from sheetFeeder import dataSheet
import dpath.util
import datetime
import dcps_utils as util
import digester  # for generating composite digest of report info.


MY_NAME = __file__
SCRIPT_NAME = os.path.basename(MY_NAME)

DEBUG = False


def main():

    # This makes sure the script can be run from any working directory and still find related files.
    my_path = os.path.dirname(__file__)

    if DEBUG is True:
        sheet_id = "18uvn9wIABHVIdjlSRNXqnHUKB2aTvZgKO62e-UFNuO8"  # test
    else:
        sheet_id = "1dTeMAK_cGWAUvrqvAiY2hGy4gJewrmWjnuIZu8NhWwE"

    now1 = datetime.datetime.now()
    start_time = str(now1)
    end_time = ""  # set later

    # First get the agent records from API (this can take a long time!)

    asf.setServer("Prod")  # AS instance: Prod | Dev | Test

    if DEBUG is True:
        out_folder = "/cul/cul0/ldpd/archivesspace/test/agents"
    else:
        out_folder = "/cul/cul0/ldpd/archivesspace/agents"

    family_agents_file = os.path.join(out_folder, "agents_families.pickle")
    corp_agents_file = os.path.join(out_folder, "agents_corporate.pickle")
    persons_agents_file = os.path.join(out_folder, "agents_persons.pickle")

    the_info = [
        {"name": "families",
         "endpoint": "/agents/families",
         "sheet": dataSheet(sheet_id, "families!A:Z"),
         "pickle": family_agents_file
         },
        {"name": "corporate",
         "endpoint": "/agents/corporate_entities",
         "sheet": dataSheet(sheet_id, "corporate!A:Z"),
         "pickle": corp_agents_file
         },
        {"name": "persons",
         "endpoint": "/agents/people",
         "sheet": dataSheet(sheet_id, "persons!A:Z"),
         "pickle": persons_agents_file
         },
    ]

    # List of fields to extract, expressed as dpaths.
    the_fields = [
        ["uri", "uri"],
        ["title", "title"],
        ["source", "names/0/source"],
        ["authority_id", "names/0/authority_id"],
        ["is_linked_to_published_record", "is_linked_to_published_record"],
        ["publish", "publish"],
        ["last_modified_by", "last_modified_by"],
        ["last_modified", "system_mtime"],
    ]

    the_record_cnts = {}

    if DEBUG is True:
        print("*** (DEBUG MODE) ***")

    for i in the_info:
        print("Getting agents: " + i["name"])
        agent_data = get_agent_data(i["name"], i["endpoint"], i["pickle"])

        print(" ")

        # Report the saved data to Google Sheet

        the_sheet = i["sheet"]

        the_heads = [x[0] for x in the_fields]
        the_output = [the_heads]

        the_record_cnts[i["name"]] = str(len(agent_data))

        for agent in agent_data:
            the_row = []
            # Use dpath to extract values from dict and compose into rows.
            for af in the_fields:
                try:
                    d = str(dpath.util.get(agent, af[1]))
                except:
                    d = ""
                the_row.append(d)
            # print(the_row)
            the_output.append(the_row)

        the_sheet.clear()
        save = the_sheet.appendData(the_output)
        print(save)

    # Generate log

    print(the_record_cnts)
    print(" ".join(the_record_cnts))

    cnt_str = "".join(k + "=" + v + ". " for k, v in the_record_cnts.items())

    # print(cnt_str)

    now2 = datetime.datetime.now()
    end_time = str(now2)
    my_duration = str(now2 - now1)

    the_log = (
        "Data imported by "
        + MY_NAME
        + ". "
        + cnt_str
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
    log_it(SCRIPT_NAME, the_log)
    # digester.post_digest(SCRIPT_NAME, the_log)

    print(" ")

    exit_msg = "Script done. Updated data is available at " + \
        "https://docs.google.com/spreadsheets/d/" + \
        str(sheet_id) + "/edit?usp=sharing"

    print(exit_msg)
    log_it(SCRIPT_NAME, exit_msg)

    quit()


def log_it(script, log):
    if DEBUG is not True:
        digester.post_digest(script, log)


def get_agent_data(name, endpoint, pickle_path):
    print("Getting agents: " + name)
    # out_path = os.path.join(my_path, "output/agents_" + i["name"] + ".pickle")
    # out_path = os.path.join(out_folder, "agents_" + i["name"] + ".pickle")
    # Get a list of agent ids from API
    agents_list = json.loads(asf.getResponse(endpoint + "?all_ids=true"))

    agent_cnt_str = "Number of agents (" + \
        name + "): " + str(len(agents_list))
    print(agent_cnt_str)
    log_it(SCRIPT_NAME, agent_cnt_str)

    agent_data = []

    # Loop through agent ids and get full record from API.
    for cnt, agent in enumerate(agents_list):
        # print("COUNT: " + str(cnt))
        # print("Agent # " + str(agent))
        x = asf.getResponse(endpoint + "/" + str(agent))
        agent_data.append(json.loads(x))

    # Save data as pickle
    util.pickle_it(agent_data, pickle_path)
    return agent_data


if __name__ == "__main__":
    main()
