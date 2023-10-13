import logging
from configparser import ConfigParser

from asnake.utils import get_note_text

from .aspace_client import ArchivesSpaceClient


class PhysdescToExtent(object):
    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
            handlers=[
                logging.FileHandler(f"physdesc_to_extent_{mode}.log",),
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

    def run(self, repo_id=2):
        archival_objects = self.as_client.aspace.repositories(repo_id).archival_objects
        for ao in archival_objects:
            try:
                physdesc_notes = self.as_client.has_physdesc(ao)
                extent_possible = [
                    self.parsable_physdesc(physdesc_note, "folder")
                    for physdesc_note in physdesc_notes
                ]
                if len(extent_possible) == 1:
                    if extent_possible[0] is None:
                        pass
                    elif ao.extents:
                        logging.info(f"{ao.uri} has an extent statement. Skipping...")
                    elif self.has_folder_instance(ao.json()):
                        logging.info(
                            f"{ao.uri} has folder information in an instance. Skipping..."
                        )
                    else:
                        physdesc_note = extent_possible[0]
                        extent_number = self.parse_physdesc_number(physdesc_note)
                        self.move_to_extent_statement(
                            extent_number, physdesc_note.json(), ao.json()
                        )
                        logging.info(f"Moved physdesc to extent statement: {ao.uri}")
            except Exception as e:
                logging.error(f"{ao.uri}: {e}")

    def has_folder_instance(self, ao_json):
        """Checks whether an archival object has folder information in at least one instance.

        Args:
            ao_json (dict): JSON of an ASpace archival object
        """
        instances_with_folder = []
        for instance in ao_json.get("instances", []):
            if instance["instance_type"] != "digital_object":
                if instance.get("subcontainer"):
                    subcontainer_type = instance["subcontainer"]["type_2"]
                    if "folder" in subcontainer_type.lower():
                        instances_with_folder.append(instance)
        if instances_with_folder:
            return True

    def move_to_extent_statement(self, extent_number, physdesc_note, ao_json):
        """Creates an extent statement and deletes a physdesc note.

        Args:
            extent_number (str): extent number
            physdesc_note (dict): physdesc note
            ao_json (dict): ASpace archival object or resource json
        """
        extent_statement = {
            "portion": "whole",
            "extent_type": "folders",
            "jsonmodel_type": "extent",
        }
        extent_statement["number"] = extent_number
        ao_json["extents"] = [extent_statement]
        ao_json["notes"] = ao_json["notes"].remove(physdesc_note)
        self.as_client.aspace.client.post(ao_json["uri"], json=ao_json)

    def parsable_physdesc(self, physdesc, extent_type):
        """Parses an ASnake note object to determine if it matches an extent statement.

        Extent statements have a number followed by an extent type.

        Args:
            physdesc (obj): ASnake abstraction layer note
            extent_type (str): extent type, e.g., folder

        Returns:
            obj: ASnake abstraction layer note

        """
        physdesc_note = get_note_text(physdesc.json(), self.as_client.aspace.client)[0]
        physdesc_list = physdesc_note.strip("()").lower().split(" ")
        if len(physdesc_list) == 2:
            if physdesc_list[0].isnumeric() and extent_type in physdesc_list[1]:
                return physdesc

    def parse_physdesc_number(self, physdesc):
        """Parses an ASnake note object to get number if note matches extent format.

        Extent statements have a number followed by an extent type.

        Args:
            physdesc (obj): ASnake abstraction layer note

        Returns:
            str: extent number

        """
        physdesc_note = get_note_text(physdesc.json(), self.as_client.aspace.client)[0]
        physdesc_list = physdesc_note.strip("()").lower().split(" ")
        if len(physdesc_list) == 2 and physdesc_list[0].isnumeric():
            return physdesc_list[0]
