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
        self.repo = self.as_client.aspace.repositories(2)

    def get_subseries_data(self, subseries_uri, output_csv):
        """
        Extracts archival objects from a subseries and writes information to a CSV file.

        Args:
            subseries_uri (str): URI of the subseries to extract data from.
            output_csv (str): Path to the output CSV file.

        Returns:
            None
        """
        tree = walk_tree(subseries_uri, self.as_client.aspace.client)
        next(tree)
        sheet_data = []
        sheet_data.append(["display_string", "uri"])
        for child in tree:
            sheet_data.append([child["display_string"], child["uri"]])
            logging.info(child["display_string"])
        write_data_to_csv(sheet_data, output_csv)

    def add_instances_extents(self, subseries_csv, add_extents=False):
        """
        Parses a CSV file containing subseries data and adds extents, instances,
        and digital objects to archival objects for a given subseries in ASpace.

        Args:
            subseries_csv (str): Path to the CSV file containing subseries data.
            add_extents (bool, optional): Flag indicating whether to add physical
                extents to Archival Objects. Defaults to False.
        """
        with open(subseries_csv, "r") as csvfile:
            reader = csv.DictReader(csvfile)
        fass_containers = self.get_fass_top_containers()
        for row in reader:
            try:
                ao_uri = row["uri"]
                ao_json = self.as_client.aspace.client.get(ao_uri).json()
                if add_extents:
                    ao_json = self.add_extents(row, ao_json)
                if not ao_json["instances"]:
                    ao_json = self.add_instances(fass_containers, ao_json)
                ao_json = self.add_dao(row, ao_json)
                self.as_client.aspace.client.post(ao_uri, json=ao_json)
            except Exception as e:
                logging.error(f"{ao_uri}: {e}")

    def add_extents(self, row, ao_json):
        """
        Creates a list of extent dictionaries based on data in a row from the
        subseries CSV file and adds them to the provided Archival Object JSON.

        Args:
            row (dict): A dictionary containing data from a row in the subseries CSV.
            ao_json (dict): The Archival Object JSON to be updated with extents.

        Returns:
            dict: The updated Archival Object JSON with extents added.
        """
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

    def add_instances(self, row, fass_containers, ao_json):
        """
        Adds physical instances for boxes to the provided Archival Object JSON.

        Args:
            fass_containers (list): A list of dictionaries representing top containers.
            ao_json (dict): The Archival Object JSON to be updated with instances.

        Returns:
            dict: The updated Archival Object JSON with instances added.
        """
        box_numbers_list = row["box_number"].split(",")
        bf_numbers_list = row["BF_number"].split(",")
        for box_num, bf_num in zip(box_numbers_list, bf_numbers_list):
            box_uri = [x["uri"] for x in fass_containers if box_num == x["box_num"]][0]
            new_instance = {
                "instance_type": "box",
                "jsonmodel_type": "instance",
                "is_representative": False,
                "sub_container": {
                    "jsonmodel_type": "sub_container",
                    "gtop_container": {"ref": box_uri},
                },
            }
            ao_json["instances"].append(new_instance)
        return ao_json

    def add_dao(self, row, ao_json):
        """
        Attempts to find a digital object based on DOI and adds it as an instance
        to the provided Archival Object JSON. Logs an error if no or multiple
        matching digital objects are found.

        Args:
            row (dict): A dictionary containing data from a row in the subseries CSV.
            ao_json (dict): The Archival Object JSON to be updated with the digital object.

        Returns:
            dict: The updated Archival Object JSON with the digital object (if found) added as an instance.
        """
        file_version_uri = row["doi"]
        search_query = f"{file_version_uri} primary_type:digital_object"
        response = self.repo.search.with_params(q=search_query)
        results = [x for x in response]
        if len(results) == 1:
            digital_object_ref = {"ref": results[0].uri}
            digital_object = {
                "instance_type": "digital_object",
                "jsonmodel_type": "instance",
                "is_representative": False,
                "digital_object": digital_object_ref,
            }
            ao_json["instances"].append(digital_object)
        else:
            logging.error(f"{row['uri']}: {len(results)} DAOs found for {file_version_uri}")
        return ao_json

    def get_fass_top_containers(self):
        """
        Retrieves a list of top container dictionaries associated with a collection.

        Returns:
            list: A list of dictionaries representing associated top containers.
        """
        search_query = "primary_type:top_container AND collection_identifier_stored_u_sstr:11749061"
        search_results = self.repo.search.with_params(q=search_query)
        fass_containers = []
        for x in search_results:
            fass_containers.append({"uri": x.uri, "box_num": x.indicator_u_icusort})
        return fass_containers
