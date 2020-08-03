import ASFunctions as asf
import json
import os.path
from sheetFeeder import dataSheet
import dpath.util
import datetime
import dcps_utils as util
import digester  # for generating composite digest of report info.


my_name = __file__
script_name = os.path.basename(my_name)

# This makes sure the script can be run from any working directory and still find related files.
my_path = os.path.dirname(__file__)

sheet_id = "1dTeMAK_cGWAUvrqvAiY2hGy4gJewrmWjnuIZu8NhWwE"
# sheet_id = "18uvn9wIABHVIdjlSRNXqnHUKB2aTvZgKO62e-UFNuO8"  # test

now1 = datetime.datetime.now()
start_time = str(now1)
end_time = ""  # set later


# First get the agent records from API (this can take a long time!)

asf.setServer("Prod")  # AS instance: Prod | Dev | Test


the_info = [
    {"name": "families", "endpoint": "/agents/families", },
    {"name": "corporate", "endpoint": "/agents/corporate_entities", },
    {"name": "persons", "endpoint": "/agents/people", },
]

for i in the_info:
    print("Getting agents: " + i["name"])
    out_path = os.path.join(my_path, "output/agents_" + i["name"] + ".pickle")

    # Get a list of agent ids from API
    agents_list = json.loads(asf.getResponse(i["endpoint"] + "?all_ids=true"))

    agent_cnt_str = "Number of agents (" + \
        i['name'] + "): " + str(len(agents_list))
    print(agent_cnt_str)
    digester.post_digest(script_name, agent_cnt_str)

    cnt = 0

    agent_data = []

    # Loop through agent ids and get full record from API.
    for agent in agents_list:
        cnt += 1
        # print("COUNT: " + str(cnt))
        # print("Agent # " + str(agent))
        x = asf.getResponse(i["endpoint"] + "/" + str(agent))
        agent_data.append(json.loads(x))

    # Save data as pickle
    util.pickle_it(agent_data, out_path)

    print(" ")


# Report the saved data to Google Sheet

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


family_agents_file = os.path.join(my_path, "output/agents_families.pickle")
corp_agents_file = os.path.join(my_path, "output/agents_corporate.pickle")
persons_agents_file = os.path.join(my_path, "output/agents_persons.pickle")


the_stuff = [
    {
        "name": "families",
        "sheet": dataSheet(sheet_id, "families!A:Z"),
        "pickle": family_agents_file,
    },
    {
        "name": "corporate",
        "sheet": dataSheet(sheet_id, "corporate!A:Z"),
        "pickle": corp_agents_file,
    },
    {
        "name": "persons",
        "sheet": dataSheet(sheet_id, "persons!A:Z"),
        "pickle": persons_agents_file,
    },
]

the_record_cnts = {}

for i in the_stuff:
    the_sheet = i["sheet"]

    # open pickled file
    agent_data = util.unpickle_it(i["pickle"])
    # with open(i["pickle"], "rb") as f:
    #     agent_data = pickle.load(f)

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

cnt_str = ""

for k, v in the_record_cnts.items():
    cnt_str += k + "=" + v + ". "

# print(cnt_str)

now2 = datetime.datetime.now()
end_time = str(now2)
my_duration = str(now2 - now1)


the_log = (
    "Data imported by "
    + my_name
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
digester.post_digest(script_name, the_log)

print(" ")

exit_msg = "Script done. Updated data is available at " + \
    "https://docs.google.com/spreadsheets/d/" + \
    str(sheet_id) + "/edit?usp=sharing"

print(exit_msg)
digester.post_digest(script_name, exit_msg)
