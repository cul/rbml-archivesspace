import csv
import logging
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient


class AddFassInstances(object):
    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
            handlers=[
                logging.FileHandler(
                    f"add_fass_instances_{mode}.log",
                ),
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

    def get_subseries_data(self, subseries_uri):
        tree = walk_tree(subseries_uri, self.as_client.aspace.client)
        next(tree)
        sheet_data = []
        sheet_data.append(["display_string", "uri"])
        for child in tree:
            sheet_data.append([child["display_string"], child["uri"]])

    def write_data_to_csv(sheet_data, subseries_from_AS):
        with open(subseries_from_AS, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sheet_data)
