import json
from configparser import ConfigParser
from datetime import date

from .aspace_client import ArchivesSpaceClient


class APIComparer(object):
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.dev_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", "dev_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )
        self.prod_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", "prod_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def compare_records(self, uri):
        """Compare JSON output from the same uri from two ASpace instances.

        Args:
            uri (str): ASpace uri
        """
        dev_json = self.dev_client.get_json(uri)
        prod_json = self.prod_client.get_json(uri)
        if dev_json == prod_json:
            print(f"No differences in {uri}")
        else:
            print("!!! DIFFERENCES IN {uri} !!!")
            filename = "_".join(uri.split("/")[1:])
            self.save_json(f"{filename}_dev.json", dev_json)
            self.save_json(f"{filename}_prod.json", prod_json)

    def save_json(self, filename, json_data):
        with open(filename, "w") as json_file:
            json.dump(json_data, json_file, indent=4)
        return filename


class EADComparer(object):
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.dev_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", "dev_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )
        self.prod_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", "prod_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def download_from_dev_and_prod(self, repo_id, resource_id):
        self.save_ead(repo_id, resource_id)
        self.save_ead(repo_id, resource_id, "prod")

    def save_ead(self, repo_id, resource_id, mode="dev"):
        today = date.today().strftime("%Y-%m-%d")
        if mode == "prod":
            filename = f"{today}_{repo_id}_{resource_id}_prod.xml"
            ead = self.prod_client.get_ead(repo_id, resource_id)
        else:
            filename = f"{today}_{repo_id}_{resource_id}_dev.xml"
            ead = self.dev_client.get_ead(repo_id, resource_id)
        with open(filename, "w") as ead_file:
            ead_file.write(ead)
        return filename
