from asnake.aspace import ASpace
from asnake.utils import walk_tree


class ArchivesSpaceClient:
    """Handles communication with ArchivesSpace."""

    def __init__(self, baseurl, username, password):
        self.aspace = ASpace(baseurl=baseurl, username=username, password=password)

    def get_digital_objects(self, repo_id):
        """Get data about digital object records from AS.

        Args:
            repo_id (int): ASpace repository ID (e.g., 2)

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
        tree = walk_tree(resource, self.aspace.client)
        next(tree)
        for child in tree:
            if len(child["ancestors"]) > 3:
                print(child["display_string"], child["level"], len(child["ancestors"]))

    def get_assessments(self, repo_id):
        """Gets assessment information from an ArchivesSpace repository.

        Args:
            repo_id (int): ASpace repository ID (e.g., 2)

        Yields:
            str: Full JSON of AS assessment record
        """
        repo = self.aspace.repositories(repo_id)
        for assessment in repo.assessments:
            yield assessment.json()


    def published_resources(self, repo_id):
        for resource in self.aspace.repositories(repo_id).resources:
            if resource.publish and not resource.suppressed:
                yield resource

    def update_aspace_field(self, aspace_json, field_name, new_info):
        """Updates (or adds) a field to an ArchivesSpace record.

        Args:
            aspace_json (dict): ArchivesSpace data
            field_name (str): name of field to update
            new_info (str): value of updated field
        """
        aspace_json[field_name] = new_info
        self.aspace.client.post(aspace_json["uri"], json=aspace_json)

    def get_recent_accessions(self, repo_id):
        """Get accessions that have been updated since a provided timestamp.

        Args:
            repo_id (int): ASpace repository ID (e.g., 2)

        Yields:
            obj: JSON model object for ASpace resource
        """
        for year in [2018, 2019, 2020, 2021, 2022]:
            search_string = f"repositories/{repo_id}/search?q=primary_type:accession&page=1&filter_query[]=accession_date_year:{year}&page_size=250"
            search_results = self.aspace.client.get(search_string).json()["results"]
            for result in search_results:
                yield result
