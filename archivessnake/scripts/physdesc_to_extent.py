import logging
from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient


class PhysdescToExtent(object):
    def __init__(self, mode="dev", repo_id=2):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),

        # TODO: add any arguments this method will take DONE
        # TODO: set up logging DONE
        # TODO: get config values DONE
        # TODO: set up ArchivesSpace client DONE

    # some Asnake setup stuff I don't understand goes here
        aos = self.as_client.get_archival_objects(2)
            for ao in aos:
                if 

    def get_physdesc_aos(self, archival_object)
        uris = [] 
        
    # identify archival objects that have physdesc notes
        #"notes": 
            # "type": "physdesc"
            # "content": [etc etc]

    # identify physdesc notes that have a folder count
    # use a regex to limit to folders and ignore other physdesc notes
        # "content": [etc etc]
            # if content == "folders" 
            # if content != "folders" pass
            # if content == "folders" but ALSO some extraneous junk, parentheses check 
    # account for parentheses but also cases where these may not have been added
        # if content == "folders" and extra junk
            # regex to check if extra junk is anything other than () or )
            # if junk detector = TRUE, pass
            # if junk detector = FALSE, delete parentheses in content 
    # check for instance with folder value
            #  "instances": 
        # "container": {
            # "type_1": "[F/folder{s}]" ! Account for variability 
    # do not add an extent if there is an instance with a folder value
        # if "instances": 
            # "container": {
                # "type_1": "[F/folder{s}]" 
                # == True 
                # delete physdesc content
        # if "instances": 
            # "container": {
                # "type_1": "[F/folder{s}]" 
                # == False, move on to string split
    # phydesc note is a string - need to split that into integer and container (controlled value)
    # move those physdesc note content to extent information: 
        # "extents": 
            #"number": "[number]"  
            # "extent_type": "folders"

    # need to check that the value for folder we're using is what's in the ASpace controlled value list
