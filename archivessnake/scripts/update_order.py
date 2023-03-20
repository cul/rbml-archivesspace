import logging
from configparser import ConfigParser

from asnake.utils import walk_tree

from scripts.aspace_client import ArchivesSpaceClient


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
        self.repo = self.as_client.aspace.repositories(repo_id)

    def get_wayfinders(self, series_id, stop_id, filename):
        series = self.repo.archival_objects(series_id)
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
        with open(filename, "w") as f:
            for x in wayfinders_to_delete:
                f.write(x)
        return wayfinders_to_delete

    def reorder_objects_from_file(self, wayfinders_list_filename, series_id):
        with open(wayfinders_list_filename, "r") as f:
            wayfinders_to_delete = [line.rstrip() for line in f]
        self.reorder_objects(wayfinders_to_delete, series_id)

    def reorder_objects(self, wayfinders_to_delete, series_id):
        for w in wayfinders_to_delete:
            wayfinder_json = self.as_client.aspace.client.get(w).json()
            position = wayfinder_json["position"]
            tree = walk_tree(w, self.as_client.aspace.client)
            for child in tree:
                if child["parent"]["ref"] == w:
                    position += 1
                    params = {"parent": series_id, "position": position}
                    logging.info(f"Updating {child['uri']}...")
                    self.as_client.aspace.client.post(
                        f"{child['uri']}/parent", params=params
                    )
