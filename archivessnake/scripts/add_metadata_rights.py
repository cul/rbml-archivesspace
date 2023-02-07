import logging
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient


class MetadataRights(object):
    CC0 = {
        "file_uri": "https://creativecommons.org/publicdomain/zero/1.0/",
        "license": "public_domain",
        "jsonmodel_type": "metadata_rights_declaration",
    }

    def __init__(self, mode="test"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename=f"metadata_rights_{mode}.log",
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
        for resource in self.as_client.resources_without_rights(2):
            try:
                resource_json = resource.json()
                self.as_client.update_aspace_field(
                    resource_json, "metadata_rights_declarations", [self.CC0]
                )
                logging.info(f"Added metadata rights declaration to {resource.uri}")
            except Exception as e:
                logging.error(e)
