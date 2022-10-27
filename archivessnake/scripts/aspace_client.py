from asnake.aspace import ASpace
from asnake.utils import walk_tree


class ArchivesSpaceClient:
    """Handles communication with ArchivesSpace."""

    def __init__(self, baseurl, username, password):
        self.aspace = ASpace(baseurl=baseurl, username=username, password=password)

    def get_digital_objects(self, repo_id):
        """Get data about digital object records from AS.

        Yields:
          str: Full JSON of AS digital object record
        """
        self.repo = self.aspace.repositories(repo_id)
        search_query = "primary_type:digital_object"
        for digital_object in self.repo.search.with_params(q=search_query):
            digital_object_json = digital_object.json()
            yield digital_object_json

    def delete_in_aspace(self, target):
        """Delete a thing in AS.

        Args:
            target (str): URI of thing to delete
        """
        self.aspace.client.delete(target)

    def get_ead(self, repo_id, resource_id):
        """Get EAD for a resource.

        Args:
            repo_id (int): ASpace repository ID (e.g., 2)
            resource_id (int): ASpace resource ID (e.g., 1234)

        Returns:
            str: XML response
        """
        params = {"include_unpublished": False, "include_daos": True}
        response = self.aspace.client.get(
            f"/repositories/{repo_id}/resource_descriptions/{resource_id}.xml",
            params=params,
        )
        return response.content.decode("utf-8")

    def get_json(self, uri):
        """Get JSON of an ASpace record.

        Args:
            uri (str): ASpace uri
        """
        response = self.aspace.client.get(uri)
        return response.json()

    def get_all_children(self, resource):
        """Prints out information from the tree of a resource."""
        for child in walk_tree(resource, self.aspace.client):
            if child["level"] != "collection":
                if len(child["ancestors"]) > 3:
                    print(
                        child["display_string"], child["level"], len(child["ancestors"])
                    )

    def get_assessments(self, repo_id):
        """docstring for get_assessments"""
        repo = self.aspace.repositories(repo_id)
        for assessment in repo.assessments:
            yield assessment.json()
