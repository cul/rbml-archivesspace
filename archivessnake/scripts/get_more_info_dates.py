import csv
import logging
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient
from .helpers import write_data_to_csv


class GetMoreInfo(object):
    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
            handlers=[
                logging.FileHandler(f"get_aos_{mode}.log",),
                logging.StreamHandler(),
            ],
        )
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def run(self, input_csv, output_csv):
        with open(input_csv, "r") as input_csvfile:
            reader = csv.reader(input_csvfile)
            input_rows = [x for x in reader][1:]
        output_sheet_data = [
            [
                "Collection Title",
                "Collection Dates",
                "AO URL",
                "AO Ref ID",
                "AO Display String",
                "AO Dates",
            ]
        ]
        for input_row in input_rows:
            ao_uri = input_row[1]
            ao = self.as_client.aspace.client.get(ao_uri).json()
            (
                collection_title,
                collection_dates,
                collection_url,
            ) = self.get_collection_info(ao["resource"]["ref"])
            ao_url = (
                f"{collection_url}#tree::archival_object_{ao['uri'].split('/')[-1]}"
            )
            output_row = [
                collection_title,
                collection_dates,
                ao_url,
                ao["ref_id"],
                ao["display_string"],
            ]
            for date in ao["dates"]:
                output_row.append(date.get("expression"))
            output_sheet_data.append(output_row)
            write_data_to_csv(output_sheet_data, output_csv)

    def get_collection_info(self, resource_uri):
        resource = self.as_client.aspace.client.get(resource_uri).json()
        resource_dates = []
        for date in resource["dates"]:
            resource_dates.append(f"{date['expression']} ({date['date_type']})")
        collection_url = f"https://aspace.library.columbia.edu/resources/{resource['uri'].split('/')[-1]}"
        return resource["title"], resource_dates.join(", "), collection_url
