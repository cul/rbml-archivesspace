import logging
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient


class DigitalObjectDeleter(object):
    """Delete digital objects without a linked component in an ASpace repository."""

    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename="deleted_orphans.log",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
        )
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def run(self):
        orphan_digital_objects = self.get_orphan_digital_objects()
        logging.info(
            "{} orphan digital objects will be deleted.".format(
                len(orphan_digital_objects)
            )
        )
        for digital_object in orphan_digital_objects:
            logging.info(f"Deleting {digital_object}...")
            self.as_client.delete_in_aspace(digital_object)
            logging.info(f"{digital_object} deleted.")

    def get_orphan_digital_objects(self):
        """Get digital objects that do not have linked instances.

        Returns:
            list: list of digital object URIs
        """
        orphan_daos = []
        for dao in self.as_client.get_digital_objects():
            if not dao.get("linked_instances"):
                orphan_daos.append(dao["uri"])
        return orphan_daos
