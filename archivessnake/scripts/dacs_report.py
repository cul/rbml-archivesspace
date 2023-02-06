from configparser import ConfigParser

from dacsspace.validator import Validator

from .aspace_client import ArchivesSpaceClient
from .helpers import write_data_to_csv


class DACSReport(object):
    def __init__(self, mode="dev"):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def validate_all(self):
        repositories = {"rbml": 2, "avery": 3, "starr": 4, "burke": 5}
        for name, repo_id in repositories.items():
            self.validate_repository(name, repo_id)

    def validate_repository(self, name, repo_id):
        schema = "rbml" if name == "rbml" else "cul"
        validator = Validator(f"{schema}".json, None)
        sheet_data = []
        sheet_data.append(
            [
                "resource url",
                "uri",
                "error count",
                "ead location",
                "explanation 1",
                "explanation 2",
            ]
        )
        for resource in self.as_client.aspace.repositories(repo_id, validator):
            if resource.publish:
                row_data = []
                row_data = self.dacs_compliance(resource, validator)
                if row_data:
                    sheet_data.append(row_data)
        write_data_to_csv(sheet_data, f"dacs_{name}.csv")

    def dacs_compliance(self, resource, validator):
        resource_id = resource.uri.split("/")[-1]
        resource_url = f"https://aspace.library.columbia.edu/resources/{resource_id}"
        result = validator.validate_data(resource.json())
        if not result["valid"]:
            row_data = [
                resource_url,
                result["uri"],
                result["error_count"],
                resource.json().get("ead_location"),
            ]
            for e in result["explanation"].split("\n"):
                row_data.append(e)
            return row_data
