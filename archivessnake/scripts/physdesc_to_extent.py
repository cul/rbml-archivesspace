class PhysdescToExtent(object):
    def __init__(self):
        # TODO: add any arguments this method will take
        # TODO: set up logging
        # TODO: get config values
        # TODO: set up ArchivesSpace client
        pass

    # identify archival objects that have physdesc notes
    # identify physdesc notes that have a folder count
    # use a regex to limit to folders and ignore other physdesc notes
    # account for parentheses but also cases where these may not have been added
    # move those physdesc note content to extent information
    # phydesc note is a string - need to split that into integer and container (controlled value)
    # need to check that the value for folder we're using is what's in the ASpace controlled value list
    # do not add an extent if there is an instance with a folder value
