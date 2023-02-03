from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient
from .helpers import write_data_to_csv


class AMISpreadsheet(object):
    def __init__(self, mode="dev"):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )
        self.rights_info = "In Copyright"
        self.restrictions = "On-site Access"
        self.repo_code = "US-NNC-RB"

    def create(self, series_id):
        """Create a spreadsheet for AMI digitization.

        Args:
            series_id (int): ArchivesSpace ID for series
        """
        sheet_data = []
        sheet_data.append(
            [
                "collection_name",
                "bib_id",
                "rights",
                "restrictions",
                "repo_code",
                "series_title",
                "subseries_title",
                "ref_id",
                "unittitle",
                "unitdate",
                "creator_1",
                "creator_1_id",
                "creator_2",
                "creator_2_id",
                "box_num",
                "container2",
                "extent_number",
                "extent",
                "physfacet",
                "form",
                "scopenote",
                "language",
                "suggested_file_name",
            ]
        )
        self.av_series = self.as_client.get_abstract_series(series_id)
        creators = self.as_client.get_creators(self.av_series.resource)
        self.creator_1 = creators[0].names[0].sort_name
        self.creator_1_id = creators[0].names[0].authority_id
        self.creator_2 = creators[1].names[0].sort_name if len(creators) > 1 else ""
        self.creator_2_id = (
            creators[1].names[0].authority_id if len(creators) > 1 else ""
        )
        children = self.as_client.get_rbml_children(self.av_series)
        self.count = 1
        for child in children:
            try:
                row = self.create_row(child)
                sheet_data.append(row)
            except Exception as e:
                print(e, child.title)
        spreadsheet_name = f"{self.av_series.resource.id_0}_ami.csv"
        write_data_to_csv(sheet_data, spreadsheet_name)

    def create_row(self, ao):
        row_data = []
        row_data.append(self.av_series.resource.title)
        row_data.append(self.av_series.resource.id_0)
        row_data.append(self.rights_info)
        row_data.append(self.restrictions)
        row_data.append(self.repo_code)
        row_data.append(ao.ancestors[-2].title)
        subseries = ao.ancestors[-3].title if len(ao.ancestors) > 2 else ""
        row_data.append(subseries)
        row_data.append(ao.ref_id)
        row_data.append(getattr(ao, "title", ao.ancestors[0].title))
        if getattr(ao, "dates", None):
            row_data.append(ao.dates[0].expression)
        else:
            row_data.append("")
        row_data.append(self.creator_1)
        row_data.append(self.creator_1_id)
        row_data.append(self.creator_2)
        row_data.append(self.creator_2_id)
        box_num, container2 = self.get_container_info(ao)
        row_data.append(box_num)
        row_data.append(container2)
        if getattr(ao, "extents", None):
            row_data.append(ao.extents[0].number)
            row_data.append(ao.extents[0].extent_type)
        else:
            row_data.append("")
            row_data.append("")
        physfacet, scopenote = self.get_physfacet_scope()
        row_data.append(physfacet)
        row_data.append("VIDEO RECORDINGS")
        row_data.append(scopenote)
        row_data.append(self.as_client.get_language(ao))
        if container2:
            suggested_filename = (
                f"RBML_{self.av_series.resource.id_0}_{box_num}-{container2}"
            )
        else:
            suggested_filename = (
                f"RBML_{self.av_series.resource.id_0}_{box_num}-{self.count}"
            )
            self.count += 1
        digitized = self.is_digitized(ao)
        if digitized:
            suggested_filename = f"PREVIOUSLY DIGITIZED: {suggested_filename}"
        row_data.append(suggested_filename)
        print(row_data)

    def get_physfacet_scope(self, ao):
        physfacet, scopenote = "", ""
        if getattr(ao, "notes", None):
            for note in ao.notes:
                if note.type == "physfacet":
                    physfacet = note.content[0]
                if note.type == "scopecontent":
                    scopenote = note.subnotes[0].content
        return physfacet, scopenote

    def get_container_info(self, ao):
        if ao.instances[0].instance_type != "digital_object":
            return (
                ao.instances[0].sub_container.top_container.indicator,
                ao.instances[0].sub_container.json().get("indicator_2", ""),
            )
        elif len(ao.instances) > 1:
            if ao.instances[1].instance_type != "digital_object":
                return (
                    ao.instances[1].sub_container.top_container.indicator,
                    ao.instances[1].sub_container.json().get("indicator_2", ""),
                )
        else:
            return "", ""

    def is_digitized(self, ao):
        if any("digital_object" in obj.json() for obj in ao.instances):
            digital_objects = [
                a for a in ao.instances if a.instance_type == "digital_object"
            ]
        else:
            return False
