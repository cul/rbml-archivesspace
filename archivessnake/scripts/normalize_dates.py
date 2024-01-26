import logging
from configparser import ConfigParser
from re import fullmatch

from .aspace_client import ArchivesSpaceClient


class NormalizeDates(object):
    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
            handlers=[
                logging.FileHandler(f"normalize_dates_{mode}.log",),
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
        for resource in self.as_client.aspace.repositories(repo_id).resources:
            if resource.publish and not resource.suppressed:
                self.update_dates(resource)

    def update_dates(self, resource):
        resource_json = resource.json()
        dates = resource_json["dates"]
        new_dates = []
        for date in dates:
            new_date = self.normalize_expression(date)
            if new_date:
                new_dates.append(new_date)
            else:
                new_dates.append(date)
        if dates != new_dates:
            resource_json["dates"] = new_dates
            self.as_client.aspace.client.post(resource.uri, json=resource_json)
            logging.info(f"Updated {resource.title} ({resource.uri})")
            # TODO: what happens when you push a single date with a begin and end date to ArchivesSpace via the API?

    def normalize_expression(self, date):
        expression = date.get("expression", "")
        begin = date.get("begin")
        end = date.get("end")
        if begin is None or end is None:
            if fullmatch(r"\d\d\d\d-\d\d\d\d", expression):
                if begin is None:
                    date["begin"] = expression.split("-")[0]
                elif begin.startswith(expression.split("-")[0]) and begin.endswith(
                    "-01-01"
                ):
                    date["begin"] = begin[:4]
                if end is None:
                    date["end"] = expression.split("-")[-1]
                elif end.startswith(expression.split("-")[-1]) and end.endswith(
                    "-01-01"
                ):
                    date["end"] = end[:4]
                return date
            else:
                return False
        else:
            return False
