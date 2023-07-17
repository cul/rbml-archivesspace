import logging
from configparser import ConfigParser
from re import fullmatch

from asnake.utils import walk_tree

from scripts.aspace_client import ArchivesSpaceClient


class DateException(Exception):
    pass


class OrderUpdater(object):
    def __init__(self, mode="dev", repo_id=2):
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

    def get_wayfinders(self, series_uri, stop_uri, filename=None):
        """Get list of archival objects in series that have children and 2 ancestors.

        If filename is provided, writes list to a file.

        Args:
            stop_uri (str): URI of archival object to stop traversing series tree
            filename (str): filename to write list to

        Returns:
            list
        """
        tree = walk_tree(series_uri, self.as_client.aspace.client)
        next(tree)
        wayfinders_to_delete = []
        for child in tree:
            if child["uri"] == stop_uri:
                break
            if len(child["ancestors"]) == 3:
                parent_uri = child["parent"]["ref"]
                if parent_uri not in wayfinders_to_delete:
                    wayfinders_to_delete.append(parent_uri)
                    print(parent_uri)
        if filename:
            with open(filename, "w") as f:
                for x in wayfinders_to_delete:
                    f.write(f"{x}\n")
        return wayfinders_to_delete

    def reorder_objects_from_file(
        self, series_uri, wayfinders_list_filename, delete=False
    ):
        """Reorders archival objects using list in a file."""
        with open(wayfinders_list_filename, "r") as f:
            print(f"Opening {wayfinders_list_filename}...")
            wayfinders_to_delete = [line.rstrip() for line in f]
        self.reorder_objects(series_uri.split("/")[-1], wayfinders_to_delete, delete)

    def reorder_objects(self, series_id, wayfinders_to_delete, delete=False):
        """For each archival object in a list, move each child up one level.

        Args:
            series_id (int): ASpace id of parent series (e.g., 1234)
            wayfinders_to_delete (list): ASpace archival object URIs
            delete (bool): remove wayfinder after reording children
        """
        for w in wayfinders_to_delete:
            print(f"Reordering children of {w}...")
            wayfinder_json = self.as_client.aspace.client.get(w).json()
            position = wayfinder_json["position"]
            tree = walk_tree(w, self.as_client.aspace.client)
            logging.info(f"Moving children of {w}")
            for child in tree:
                if child["parent"]["ref"] == w:
                    position += 1
                    params = {"parent": series_id, "position": position}
                    logging.info(f"Updating {child['uri']}...")
                    self.as_client.aspace.client.post(
                        f"{child['uri']}/parent", params=params
                    )
            if delete:
                self.as_client.delete_in_aspace(w)
                logging.info(f"Deleting {w}")

    def add_date_from_wayfinder_display_string(self, wayfinder_ao_uri, series_id, delete=False):
        """Takes a parent whose display string is a date, adds date to children.

        Reorders children to be at same level as parent.

        Args:
            wayfinder_ao_uri (str): ASpace URI for archival object with children and a display string that is a date
            series_id (str): ASpace id of parent series (e.g., 1234)
        """
        wayfinder_json = self.as_client.get_json_response(wayfinder_ao_uri)
        position = wayfinder_json["position"]
        tree = walk_tree(wayfinder_ao_uri, self.as_client.aspace.client)
        next(tree)
        for child in tree:
            self.add_date_from_string(wayfinder_json["display_string"], child["uri"])
            if child["parent"]["ref"] == wayfinder_ao_uri:
                position += 1
                params = {"parent": series_id, "position": position}
                logging.info(f"Updating {child['uri']}...")
                self.as_client.aspace.client.post(
                    f"{child['uri']}/parent", params=params
                )
        if delete:
            self.as_client.delete_in_aspace(wayfinder_ao_uri)
            logging.info(f"Deleting {wayfinder_ao_uri}")

    def add_date_from_string(self, date_string, ao_uri):
        """Updates ASpace record with date if date matches certain format.

        Only adds date if record does not already have a date.

        Args:
            ao_uri (str): ASpace URI
            date_string (str): date formatted YYYY, YYYY-DD, YYYY-MM-DD, or YYYY-YYYY
        """
        date_formats = [
            r"\d\d\d\d",
            r"\d\d\d\d-\d\d\d\d",
            r"\d\d\d\d-\d\d",
            r"\d\d\d\d-\d\d-\d\d",
        ]
        if [True for x in date_formats if fullmatch(x, date_string)]:
            ao_json = self.as_client.get_json(ao_uri)
            if ao_json["dates"]:
                return f"Dates already exist for {ao_uri}"
            else:
                date_obj = self.create_date_object(date_string)
                self.as_client.update_aspace_field(ao_json, "dates", [date_obj])
                return f"{date_string} added to {ao_uri}"
        else:
            raise DateException(f"Unexpected date format {date_string}")

    def create_date_object(self, date_string):
        """Turns a date string into an ASpace date.

        Args:
            date_string (str): date formatted YYYY, YYYY-DD, YYYY-MM-DD, or YYYY-YYYY

        Returns:
            dict: ASpace date object
        """
        date_object = {"label": "creation", "jsonmodel_type": "date"}
        single_date_formats = [r"\d\d\d\d", r"\d\d\d\d-\d\d", r"\d\d\d\d-\d\d-\d\d"]
        if [True for x in single_date_formats if fullmatch(x, date_string)]:
            date_object["begin"] = date_string
            date_object["date_type"] = "single"
            return date_object
        elif fullmatch(r"\d\d\d\d-\d\d\d\d", date_string):
            date_object["begin"] = date_string.split("-")[0]
            date_object["end"] = date_string.split("-")[-1]
            date_object["date_type"] = "inclusive"
            return date_object
        else:
            raise DateException
