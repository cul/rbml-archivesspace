import csv
import logging
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient


class UpdateDateInfo(object):
    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
            handlers=[
                logging.FileHandler(
                    f"update_info_dates_{mode}.log",
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

    def run(self, input_csv):
        with open(input_csv, "r") as input_csvfile:
            reader = csv.reader(input_csvfile)
            rows = [x for x in reader][1:]
        for row in rows:
            try:
                ao_uri = f"/repositories/2/archival_objects/{row[2].split('_')[-1]}"
                ao_json = self.as_client.aspace.client.get(ao_uri).json()
                dates = ao_json.get("dates", [])
                for date in dates:
                    if date.get("expression"):
                        if date["expression"] in ao_json.get("title", ""):
                            dates.remove(date)
                self.as_client.update_aspace_field(ao_json, "dates", dates)
                logging.info(f"Updated {ao_uri}")
            except Exception as e:
                logging.error(f"ao_uri: {e}")
