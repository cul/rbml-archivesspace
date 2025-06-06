import logging
from configparser import ConfigParser
from asnake.utils import walk_tree

from .aspace_client import ArchivesSpaceClient


class AddContainers(object):
    """Adds container instance data to archival objects in ArchivesSpace.

    This class provides methods to traverse an ArchivesSpace series or resource
    tree and propagate container instance information from archival
    objects to archival objects that lack instance data.
    """

    def __init__(self, mode="dev"):
        """Initializes the AddContainers class.

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
                    f"add_containers_{mode}.log",
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

    def run(self, series_id):
        """Processes a given ArchivesSpace series to add container instances.

        Walks through the archival objects within the specified series. If an
        archival object (at 'file' or 'item' level) lacks container
        instance data, it attempts to inherit it from the most recently
        encountered archival object with instance data.

        Args:
            series_id (int): The ID of the ArchivesSpace series to process.
        """
        instances = None
        series = self.as_client.aspace.repositories(2).archival_objects(series_id)
        tree = walk_tree(series, self.as_client.aspace.client)
        next(tree)
        logging.info(f"Updating {series.title}...")
        for ao in tree:
            if ao["level"].lower() in ["file", "item"]:
                if ao["instances"]:
                    instances = ao["instances"]
                else:
                    if instances:
                        self.as_client.update_aspace_field(ao, "instances", instances)

    def run_resource(self, resource_id):
        """Processes a given ArchivesSpace resource to add container instances.

        Walks through the archival objects within the specified resource. If an
        archival object (at 'file' or 'item' level) lacks container
        instance data, it attempts to inherit it from the most recently
        encountered archival object with instance data.

        Args:
            resource_id (int): The ID of the ArchivesSpace resource to process.
        """
        instances = None
        resource = self.as_client.aspace.repositories(2).resources(resource_id)
        tree = walk_tree(resource, self.as_client.aspace.client)
        next(tree)
        logging.info(f"Updating {resource.title}...")
        for ao in tree:
            if ao["level"].lower() in ["file", "item"]:
                if ao["instances"]:
                    instances = ao["instances"]
                else:
                    if instances:
                        self.as_client.update_aspace_field(ao, "instances", instances)
