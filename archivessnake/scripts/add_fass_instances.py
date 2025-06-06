import csv
import logging
import uuid
from configparser import ConfigParser
from time import sleep

from asnake.utils import walk_tree

from .aspace_client import ArchivesSpaceClient
from .helpers import write_data_to_csv


class AddFassInstances(object):
    """This class reads data from CSV files to identify archival objects that
    need updates, fetches existing data from ArchivesSpace, and then
    creates or updates physical instances (boxes/items), digital object
    instances (DAOs), and physical extents as required. It also handles
    the creation of new top containers and digital objects if they do not
    already exist in ArchivesSpace.
    """

    def __init__(self, mode="dev"):
        """Initializes the AddFassInstances class.

        Sets up logging and establishes a connection to the ArchivesSpace API.

        Args:
            mode (str, optional): The operational mode, either "dev" "prod", or "test".
                                  This determines which ArchivesSpace base URL
                                  is used from the configuration. Defaults to "dev".
        """
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
            self.get_fass_top_containers()
            for row in reader:
                try:
                    sleep(1)
                    ao_uri = row["uri"]
                    ao_json = self.as_client.aspace.client.get(ao_uri).json()
                    if add_extents:
                        ao_json = self.add_extents(row, ao_json)
                    if not ao_json["instances"]:
                        ao_json = self.add_instances(row, ao_json)
                    ao_json = self.add_dao(row, ao_json)
                    response = self.as_client.aspace.client.post(ao_uri, json=ao_json)
                    # print(response.status_code)
                    if not response.ok:
                        print(ao_uri)
                        print(response.status_code, response.reason)
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
        return ao_json

    def add_instances(self, row, ao_json):
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
            if not [x["uri"] for x in self.fass_containers if box_num == x["box_num"]]:
                self.create_top_container(box_num)
            box_uri = [
                x["uri"] for x in self.fass_containers if box_num == x["box_num"]
            ][0]
            new_instance = {
                "instance_type": "box",
                "jsonmodel_type": "instance",
                "is_representative": False,
                "sub_container": {
                    "jsonmodel_type": "sub_container",
                    "indicator_2": bf_num,
                    "type_2": "item",
                    "top_container": {"ref": box_uri},
                },
            }
            ao_json["instances"].append(new_instance)
        return ao_json

    def add_dao(self, row, ao_json):
        """
        Attempts to find a digital object based on DOI and adds it as an instance
        to the provided Archival Object JSON. Creates a digital object if none are
        found. Logs an error if multiple matching digital objects are found.

        Args:
            row (dict): A dictionary containing data from a row in the subseries CSV.
            ao_json (dict): The Archival Object JSON to be updated with the digital object.

        Returns:
            dict: The updated Archival Object JSON with the digital object added as an instance.
        """
        doi = row["_doi"].split(":")[-1]
        if doi:
            search_query = f"{doi} primary_type:digital_object"
            response = self.repo.search.with_params(q=search_query)
            results = [x for x in response]
            if len(results) > 1:
                logging.error(
                    f"{row['uri']}: {len(results)} DAOs found for {ao_json['uri']}"
                )
            else:
                if not results:
                    digital_object_uri = self.create_digital_object(
                        ao_json["title"], doi
                    )
                    digital_object_ref = {"ref": digital_object_uri}
                else:
                    digital_object_ref = {"ref": results[0].uri}
                    dao_json = self.as_client.aspace.client.get(
                        digital_object_ref["ref"]
                    ).json()
                    self.as_client.update_aspace_field(
                        dao_json, "title", ao_json["title"]
                    )
                digital_object = {
                    "instance_type": "digital_object",
                    "jsonmodel_type": "instance",
                    "is_representative": False,
                    "digital_object": digital_object_ref,
                }
                ao_json["instances"].append(digital_object)
        return ao_json

    def get_fass_top_containers(self):
        """
        Retrieves a list of top container dictionaries associated with a collection.

        Returns:
            list: A list of dictionaries representing associated top containers.
        """
        search_query = "primary_type:top_container AND collection_identifier_stored_u_sstr:11749061"
        search_results = self.repo.search.with_params(q=search_query)
        self.fass_containers = []
        for x in search_results:
            self.fass_containers.append({"uri": x.uri, "box_num": x.indicator})
        return self.fass_containers

    def create_top_container(self, box_num):
        """Creates a new top container in ArchivesSpace with the specified
        box number and a type of "box".

        After successful creation, the URI of the new top container is
        added to the `self.fass_containers` cache.

        Args:
            box_num (str): The indicator (box number) for the new top container.
        """
        json = {
            "jsonmodel_type": "top_container",
            "indicator": box_num,
            "type": "box",
        }
        response = self.as_client.aspace.client.post(
            "/repositories/2/top_containers", json=json
        )
        uri = response.json()["uri"]
        self.fass_containers.append({"uri": uri, "box_num": box_num})

    def create_digital_object(self, ao_title, doi):
        """Creates a new digital object in ArchivesSpace with the given title
        and DOI.

        A new UUID-based `digital_object_id` is generated, and a file version
        is created with the `file_uri` pointing to the DOI. The digital object
        is set to be published.

        Args:
            ao_title (str): The title for the new digital object, typically
                            derived from the associated archival object's title.
            doi (str): The Digital Object Identifier (DOI) that will form the
                       `file_uri` for the digital object.

        Returns:
            str: The ArchivesSpace URI of the newly created digital object.
        """
        json = {
            "jsonmodel_type": "digital_object",
            "title": ao_title,
            "digital_object_id": str(uuid.uuid4()).replace("-", ""),
            "publish": True,
            "file_versions": [
                {
                    "file_uri": f"https://doi.org/{doi}",
                    "publish": True,
                    "jsonmodel_type": "file_version",
                    "is_representative": False,
                }
            ],
        }
        response = self.as_client.aspace.client.post(
            "/repositories/2/digital_objects", json=json
        )
        uri = response.json()["uri"]
        return uri
