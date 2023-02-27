import logging
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient


class FileLevelRestrictions(object):
    UNVETTED = {
        "jsonmodel_type": "note_multipart",
        "type": "accessrestrict",
        "rights_restriction": {
            "local_access_restriction_type": ["TEMPORARILY UNAVAILABLE"]
        },
        "subnotes": [
            {"jsonmodel_type": "note_text", "content": "[Unvetted]", "publish": True}
        ],
        "publish": True,
    }

    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename=f"file_level_restrictions_{mode}.log",
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

    def run(self, resource_id):
        resource = self.as_client.aspace.repositories(2).resources(resource_id)
        logging.info(f"Starting {resource.title}...")
        for child in self.as_client.get_children_with_instances(resource):
            child_json = child.json()
            if not [
                n
                for n in child_json.get("notes", [])
                if n.get("type") == "accessrestrict"
            ]:
                child_notes = child_json.get("notes", [])
                child_notes.append(self.UNVETTED)
                self.as_client.update_aspace_field(child_json, "notes", child_notes)
                logging.info(f"Updating {child.uri}")
