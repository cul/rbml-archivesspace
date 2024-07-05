import csv
import logging
from configparser import ConfigParser

from asnake.utils import walk_tree

from .aspace_client import ArchivesSpaceClient
from .helpers import write_data_to_csv


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

    def get_subseries_data(self, subseries_uri, output_csv):
        tree = walk_tree(subseries_uri, self.as_client.aspace.client)
        next(tree)
        sheet_data = []
        sheet_data.append(["display_string", "uri"])
        for child in tree:
            sheet_data.append([child["display_string"], child["uri"]])
            logging.info(child["display_string"])
        write_data_to_csv(sheet_data, output_csv)

    def add_instances_extents(self, subseries_csv, add_extents=False):
        with open(subseries_csv, "r") as csvfile:
            reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                ao_uri = row["uri"]
                ao_json = self.as_client.aspace.client.get(ao_uri).json()
                if add_extents:
                    extents = []
                    for num in range(3):
                        num += 1
                        if row[f"phys_extent_num{num}"] and row[f"phys_extent{num}"]:
                            extent_dict = {}
                            extent_dict["number"] = row[f"phys_extent_num{num}"]
                            extent_dict["extent_type"] = row[f"phys_extent{num}"]
                            extent_dict["jsonmodel_type"] = "extent"
                            extents.append(extent_dict)
                    if len(extents) == 1:
                        extents[0]["portion"] = "whole"
                    else:
                        for extent in extents:
                            extent["portion"] = "part"
                    ao_json["extents"] = extents
                # add digital object
                file_version_uri = row["doi"]
                search_query = f"{file_version_uri} primary_type:digital_object"
                response = self.as_client.aspace.repositories(2).search.with_params(
                    q=search_query
                )
                results = [x for x in response]
                if len(results) == 1:
                    digital_object_ref = {"ref": results[0].uri}
                    digital_object = {
                        "instance_type": "digital_object",
                        "jsonmodel_type": "instance",
                        "is_representative": False,
                        "digital_object": digital_object_ref,
                    }
                elif not results:
                    pass
                else:
                    logging.error(
                        f"{ao_uri}: Multiple DAOs found for {file_version_uri}"
                    )
            except Exception as e:
                logging.error(f"{ao_uri}: {e}")
