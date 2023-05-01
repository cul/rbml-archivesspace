import logging
from configparser import ConfigParser
from re import fullmatch

from asnake.utils import walk_tree

from scripts.aspace_client import ArchivesSpaceClient

class DateException(Exception):
    pass
        

class OrderUpdater(object):
    def __init__(self, series_id, mode="dev", repo_id=2):
        # TODO: remove series_id from init
        self.series_id = series_id
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename=f"order_updater_{mode}.log",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
        )
        self.repo = self.as_client.aspace.repositories(repo_id)

    def get_wayfinders(self, stop_id, filename=None):
        """Get list of archival objects in series that have children and 2 ancestors.

        If filename is provided, writes list to a file.

        Args:
            stop_id (int): ID of archival object to stop traversing series tree
            filename (str): filename to write list to.

        Returns:
            list
        """
        series = self.repo.archival_objects(self.series_id)
        tree = walk_tree(series, self.as_client.aspace.client)
        next(tree)
        wayfinders_to_delete = []
        for child in tree:
            if len(child["ancestors"]) == 3:
                child_id = child["uri"].split("/")[-1]
                if child_id == stop_id:
                    break
                child_obj = self.repo.archival_objects(child_id)
                parent_id = child_obj.parent.uri
                if parent_id not in wayfinders_to_delete:
                    wayfinders_to_delete.append(parent_id)
        if filename:
            with open(filename, "w") as f:
                for x in wayfinders_to_delete:
                    f.write(x)
        return wayfinders_to_delete

    def reorder_objects_from_file(self, wayfinders_list_filename):
        """Reorders archival objects using list in a file."""
        with open(wayfinders_list_filename, "r") as f:
            wayfinders_to_delete = [line.rstrip() for line in f]
        self.reorder_objects(wayfinders_to_delete)

    def reorder_objects(self, wayfinders_to_delete):
        """For each archival object in a list, move each child up one level.

        Args:
            wayfinders_to_delete (list): ASpace archival object URIs
        """
        for w in wayfinders_to_delete:
            wayfinder_json = self.as_client.aspace.client.get(w).json()
            position = wayfinder_json["position"]
            tree = walk_tree(w, self.as_client.aspace.client)
            for child in tree:
                if child["parent"]["ref"] == w:
                    position += 1
                    params = {"parent": self.series_id, "position": position}
                    logging.info(f"Updating {child['uri']}...")
                    self.as_client.aspace.client.post(
                        f"{child['uri']}/parent", params=params
                    )

    def add_date_from_string(self, date_string, ao_uri):
        date_formats = [
            r"\d\d\d\d",
            r"\d\d\d\d-\d\d\d\d",
            r"\d\d\d\d-\d\d",
            r"\d\d\d\d-\d\d-\d\d",
        ]
        ao_json = self.as_client.get_json(ao_uri)
        if [True for x in date_formats if fullmatch(x, date_string)]:
            if ao_json["dates"]:
                logging.info(f"Dates already exist for {ao_uri}")
            else:
                self.create_date_object(date_string)
        else:
            raise Exception(f"Unexpected date format {date_string}")

    def create_date_object(self, date_string):
        date_object = {"label": "creation", "jsonmodel_type": "date"}
        single_date_formats = [r"\d\d\d\d", r"\d\d\d\d-\d\d", r"\d\d\d\d-\d\d-\d\d"]
        if [True for x in single_date_formats if fullmatch(x, date_string)]:
            date_object["begin"] = date_string
            date_object["date_type"] = "single"
            return date_object
        elif fullmatch(r"\d\d\d\d-\d\d\d\d", date_string):
            begin, end = date_string.split("-")
            date_object["begin"] = begin
            date_object["end"] = end
            date_object["date_type"] = "inclusive"
            return date_object
        else:
            raise DateException
            


{"begin": }

		{
			"expression": "1920, 1961-2018",
			"begin": "1920",
			"end": "2018",
			"date_type": "inclusive",
			"label": "creation",
			"jsonmodel_type": "date"
		}


