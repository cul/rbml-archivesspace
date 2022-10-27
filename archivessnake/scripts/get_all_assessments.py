from configparser import ConfigParser

from .aspace_client import ArchivesSpaceClient
from .helpers import write_data_to_csv


class AssessmentFinder(object):
    def __init__(self, mode="dev"):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def run(self, csv_filepath):
        sheet_data = []
        sheet_data.append(
            [
                "uri",
                "purpose",
                "created_by",
                "last_modified_by",
                "create_time",
                "user_mtime",
            ]
        )
        assessment_records = self.as_client.get_assessments(2)
        for assessment in assessment_records:
            assessment_info = self.get_assessment_info(assessment)
            if assessment_info:
                sheet_data.append(assessment_info)
        write_data_to_csv(sheet_data, csv_filepath)

    def get_assessment_info(self, assessment):
        if assessment.get("purpose"):
            return [
                assessment["uri"],
                assessment["purpose"],
                assessment["created_by"],
                assessment["last_modified_by"],
                assessment["create_time"],
                assessment["user_mtime"],
            ]
