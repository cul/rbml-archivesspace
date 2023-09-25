import logging
from configparser import ConfigParser

from asnake.utils import get_note_text

from .aspace_client import ArchivesSpaceClient


class PhysdescToExtent(object):
    def __init__(self, mode="dev", repo_id=2):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename=f"physdesc_to_extent_{mode}.log",
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
        self.repo = self.as_client.aspace.repositories(repo_id)

    def run(self):
        archival_objects = self.repo.archival_objects
        for ao in archival_objects:
            if ao.extents:
                logging.info(f"{ao.uri} has an extent statement. Skipping...")
            else:
                physdesc_notes = self.as_client.has_physdesc(ao)
                extent_possible = [
                    self.parse_physdesc(physdesc_note, "folder")
                    for physdesc_note in physdesc_notes
                ]
                if len(extent_possible) == 1:
                    physdesc_note = extent_possible[0]
                    extent_statement = {
                        "portion": "whole",
                        "extent_type": "folder",
                        "jsonmodel_type": "extent",
                    }
                    extent_statement["number"] = self.parse_physdesc_number(
                        physdesc_note
                    )

    def parsable_physdesc(self, physdesc, extent_type):
        """Parses an ASnake note object to determine if it matches an extent statement.

        Extent statements have a number followed by an extent type.

        Args:
            physdesc (obj): ASnake abstraction layer
            extent_type (str): extent type, e.g., folder

        """
        physdesc_note = get_note_text(physdesc.json(), self.as_client.aspace.client)[0]
        physdesc_list = physdesc_note.strip("()").lower().split(" ")
        if len(physdesc_list) == 2:
            if physdesc_list[0].isnumeric() and extent_type in physdesc_list[1]:
                return physdesc

    def parse_physdesc_number(self, physdesc):
        """Parses an ASnake note object to determine if it matches an extent statement.

        Extent statements have a number followed by an extent type.

        Args:
            physdesc (obj): ASnake abstraction layer

        """
        physdesc_note = get_note_text(physdesc.json(), self.as_client.aspace.client)[0]
        physdesc_list = physdesc_note.strip("()").lower().split(" ")
        if len(physdesc_list) == 2 and physdesc_list[0].isnumeric():
            return physdesc_list[0]

    # # this is less of a train wreck now??
    #  def folders_instance(self, ao):
    #     for ao in archival_objects:
    #         if hasattr(ao, "type_1") == False:
    #             "type_1".append(physdesc_list[1]) and "indicator_1".append(physdesc_list[0])
    #         elif hasattr(ao, "type_1") == True and "folder" in "type_1".lower():
    #             del physdesc_list
    #         else
    #             pass
    #             # write to csv and/or freak out
    #

    # if getattr(ao, "container", False):
    #  container2_folder = []
    #  for container in ao.notes:
    #      if type_1.lower() == "folders":
    #         del physdesc_notes
    #      else: update_extent
    # if container/type_1 exists we don't want to do anything to the *container*
    # we want to delete the physdesc note and then move on to the next ao with a physdesc note

    # def update_extent(self, extent_list)
    # extent_value = int(extent_list[0])
    # for extent in [what?]:
    #   number.append(extent_value)
    # for extent in [what again?]:
    #   extent_type.append(lower(extent_list[1]))

    # def physdesc_csv(self, physdesc_notes, filename=None):
    # with open('filename.csv', 'w', newline='') as outfile:
    # writer = csv.writer(outfile)
    #  key_list = list(test.keys())
    # ugh this is gonna involve some weirdness with the ao isn't it

    # identify physdesc notes that have a folder count
    # use a regex to limit to folders and ignore other physdesc notes
    #     "content": [etc etc]
    #         if content == "folders"
    #         if content != "folders" pass
    #         if content == "folders" but ALSO some extraneous junk, parentheses check
    # account for parentheses but also cases where these may not have been added
    #     if content == "folders" and extra junk
    #         regex to check if extra junk is *anything other than* () or )
    #         if junk detector = TRUE, pass
    #         if junk detector = FALSE, delete parentheses in content
    # check for instance with folder value
    #          "instances":
    #     "container": {
    #         "type_1": "[F/folder{s}]" ! Account for variability (running .lower string method should work here)
    # do not add an extent if there is an instance with a folder value
    #     if "instances":
    #         "container": {
    #             "type_1": "[F/folder{s}]"
    #             == True
    #             delete physdesc content
    #     if "instances":
    #         "container": {
    #             "type_1": "[F/folder{s}]"
    #             == False, move on to string split
    # phydesc note is a string - need to split that into integer and container (controlled value)
    # move those physdesc note content to extent information:
    #     "extents":
    #         "number": "[number]"
    #         "extent_type": "folders"
    #
    # need to check that the value for folder we're using is what's in the ASpace controlled value list
