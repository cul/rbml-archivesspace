import logging
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
        """Writes assessment information from ASpace records to a CSV.

        Only includes assessments that include purpose of assessment field.

        Args:
            csv_filepath (Path obj or str): Path object or string of CSV filepath
        """
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
        return csv_filepath

    def get_assessment_info(self, assessment):
        """Check if purpose of assessment exists and get certain fields.

        Args:
            assessment (dict): AS assessment record

        Returns:
            list: information from AS assessment
        """
        if assessment.get("purpose"):
            return [
                assessment["uri"],
                assessment["purpose"],
                assessment["created_by"],
                assessment["last_modified_by"],
                assessment["create_time"],
                assessment["user_mtime"],
            ]

    def get_notes_to_change(self):
        uris = []
        assessment_records = self.as_client.get_assessments(2)
        for assessment in assessment_records:
            if assessment.get("purpose"):
                purpose = assessment["purpose"]
                if purpose.lower() not in [
                    "hidden collections",
                    "tbm/ami",
                    "digital",
                    "conservation",
                    "missing",
                    "backlog",
                    "mold",
                ]:
                    uris.append(assessment["uri"])
        return uris


class AssessmentUpdater(object):
    ACCEPTED_VALUES = [
        "Unprocessed Collections",
        "TBM/AMI",
        "Digital",
        "Conservation",
        "Missing",
        "Backlog",
        "Mold",
    ]

    def __init__(self, mode="dev"):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename=f"update_assessments_{mode}.log",
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

    def run(self, uris_to_replace):
        """Replace purpose of assessment data with accepted value.

        Args:
            uris_to_replace (list): list of ASpace assessment record URIs
        """
        for uri in uris_to_replace:
            assessment_json = self.as_client.get_json(uri)
            purpose = assessment_json.get("purpose")
            if purpose:
                if len(purpose) >= 25:
                    self.copy_purpose_to_scope(assessment_json)
                    print(f"{purpose} moved to scope field for {uri}")
                    logging.info(f"{purpose} moved to scope field for {uri}")
                    assessment_json = self.as_client.get_json(uri)
                new_purpose = self.get_new_purpose(purpose)
                if new_purpose:
                    print(f"{purpose} will be replaced with {new_purpose} for {uri}")
                    logging.info(
                        f"{purpose} will be replaced with {new_purpose} for {uri}"
                    )
                    self.as_client.update_aspace_field(
                        assessment_json, "purpose", new_purpose
                    )
                    logging.info(f"{uri} purpose updated")
                else:
                    print(f"Not updating {uri}")
                    logging.info(f"Not updating {uri}")

    def copy_purpose_to_scope(self, assessment_json):
        """Copies information from purpose field to scope field.

        Args:
            assessment_json (dict): ASpace assessment record
        """
        purpose = assessment_json["purpose"]
        scope = assessment_json.get("scope")
        new_scope = ". ".join([scope, purpose]) if scope else purpose
        self.as_client.update_aspace_field(assessment_json, "scope", new_scope)

    def get_new_purpose(self, purpose):
        """Parses a string to determine what it should be replace with.

        Args:
            purpose (str): text that should be replaced
        """
        new_purpose = None
        if "mold" in purpose.lower():
            new_purpose = "Mold"
        elif "missing" in purpose.lower():
            new_purpose = "Missing"
        elif "tbm" in purpose.lower() or "ami" in purpose.lower():
            new_purpose = "TBM/AMI"
        elif "hidden" in purpose.lower() or "unprocessed" in purpose.lower():
            new_purpose = "Unprocessed Collections"
        elif "digital" in purpose.lower():
            new_purpose = "Digital"
        return new_purpose
