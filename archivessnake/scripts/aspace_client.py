import json
from pathlib import Path

from asnake.aspace import ASpace
from asnake.utils import get_note_text


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

    def resources_without_rights(self, repo_id):
        repo = self.aspace.repositories(repo_id)
        for resource in repo.resources:
            if resource.publish and not resource.suppressed:
                if not resource.title.startswith("Carnegie Corporation of New York"):
                    if not resource.metadata_rights_declarations:
                        yield resource

    def get_json_response(self, uri):
        """Get JSON response for ASpace get request

        Args:
            uri (str): ASpace URI
        """
        response = self.aspace.client.get(uri)
        return response.json()

    def replace_title_with_note(
        self, ao_json, note_type, strip_parens=True, delete_note=True
    ):
        notes = [x for x in ao_json["notes"] if x["type"] == note_type]
        if len(notes) == 1:
            note = notes[0]
            note_content = get_note_text(note, self.aspace.client)[0]
            new_title = note_content.strip("()") if strip_parens else note_content
            self.update_aspace_field(ao_json, "title", new_title)
            if delete_note:
                new_json = self.get_json_response(ao_json["uri"])
                self.update_aspace_field(
                    new_json, "notes", new_json["notes"].remove(note)
                )
        else:
            raise Exception(f"Expected 1 {note_type} note, found {len(notes)}.")

    def strip_parens_from_content(self, ao_json):
        notes = ao_json["notes"]
        for x in notes:
            if x.get("subnotes"):
                x["subnotes"][0]["content"] = x["subnotes"][0]["content"].strip("()")
        self.update_aspace_field(ao_json, "notes", notes)

    def replace_rbml_title_tags(self, ref_id):
        ao_json = self.aspace.client.get(
            f"/repositories/2/find_by_id/archival_objects?ref_id[]={ref_id};resolve[]=archival_objects"
        ).json()["archival_objects"][0]["_resolved"]
        self.update_aspace_field(
            ao_json,
            "title",
            ao_json["title"].replace("<title>", '<title render="italic">'),
        )

    def update_altrender_avery(self, ref_id):
        try:
            ao_json = self.aspace.client.get(
                f"/repositories/3/find_by_id/archival_objects?ref_id[]={ref_id};resolve[]=archival_objects"
            ).json()["archival_objects"][0]["_resolved"]
            if "<title altrender" in json.dumps(ao_json):
                if ao_json.get("title"):
                    if "<title altrender" in ao_json["title"]:
                        ao_title = ao_json["title"].replace(
                            "<title altrender=", "<title render="
                        )
                        ao_title = ao_title.replace("italics", "italic")
                        self.update_aspace_field(
                            ao_json, "title", ao_title,
                        )
                        ao_json = self.aspace.client.get(
                            f"/repositories/3/find_by_id/archival_objects?ref_id[]={ref_id};resolve[]=archival_objects"
                        ).json()["archival_objects"][0]["_resolved"]
                ao_notes = json.dumps(ao_json["notes"])
                if "<title altrender" in ao_notes:
                    ao_notes = ao_notes.replace("<title altrender=", "<title render=")
                    ao_notes = ao_notes.replace("italics", "italic")
                    self.update_aspace_field(
                        ao_json, "notes", json.loads(ao_notes),
                    )
                return True
        except Exception:
            pass

    def replace_avery_title_altender(self, ref_id):
        ao_json = self.aspace.client.get(
            f"/repositories/3/find_by_id/archival_objects?ref_id[]={ref_id};resolve[]=archival_objects"
        ).json()["archival_objects"][0]["_resolved"]

        ao_json["title"] = ao_json["title"].replace(
            "<title altrender=", "<title render="
        )

    def has_physdesc(self, ao):
        """Checks wheter an archival object has physdesc note(s)

        Args:
            ao (obj): ASnake archival object

        Returns:
            list: list of physdesc notes
        """
        if getattr(ao, "notes", False):
            physdesc_notes = []
            for note in ao.notes:
                if note.type == "physdesc":
                    physdesc_notes.append(note)
            return physdesc_notes

    def get_ead_records(self, repo_id):
        """Get EAD for resources in an ASpace repository.

        Args:
            repo_id (int): ASpace repository ID (e.g., 2)

        Yields:
            string: EAD for ASpace resource
        """
        resource_ids = self.aspace.client.get(
            f"/repositories/{repo_id}/resources",
            params={"all_ids": True, "publish": True},
        ).json()
        for resource_id in resource_ids:
            ead = self.aspace.client.get(
                f"/repositories/{repo_id}/resource_descriptions/{resource_id}.xml",
                params={"include_unpublished": False, "include_daos": True},
            ).content.decode("utf-8")
            yield ead

    def save_ead_records(self, ead_cache, repo_id, timestamp):
        """Save EAD for resources in an ASpace repository.

        Uses filename convention as_ead_ldpd_[id_0].xml

        Args:
            ead_cahe (str or Path obj): directory to save EAD files
            repo_id (int): ASpace repository ID (e.g., 2)
            timestamp (int): A UTC timestamp coerced to an integer

        Yields:
            string: EAD for ASpace resource
        """
        resource_ids = self.aspace.client.get(
            f"/repositories/{repo_id}/resources",
            params={"all_ids": True, "publish": True},
        ).json()
        for resource_id in resource_ids:
            resource = self.aspace.repositories(repo_id).resources(resource_id)
            ead = self.aspace.client.get(
                f"/repositories/{repo_id}/resource_descriptions/{resource_id}.xml",
                params={
                    "include_unpublished": False,
                    "include_daos": True,
                    "modified_since": timestamp,
                },
            ).content.decode("utf-8")
            with open(
                Path(ead_cache, f"as_ead_ldpd_{resource.id_0}.xml"), "w"
            ) as ead_file:
                ead_file.write(ead)
