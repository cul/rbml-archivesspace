import csv
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient
from .helpers import write_data_to_csv


class AspaceFinder(object):
    def __init__(self, mode="dev"):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def run(self, csv_file):
        bibids_in_portal = {}
        with open(csv_file) as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                bibids_in_portal[row[0]] = row[1]
        not_in_aspace = []
        for bibid, repo_id in bibids_in_portal.items():
            try:
                if not self.as_client.find_by_bibid(bibid, repo_id):
                    not_in_aspace.append([bibid, repo_id])
            except Exception as e:
                print(e, bibid)
        write_data_to_csv(not_in_aspace, "not_in_aspace.csv")
