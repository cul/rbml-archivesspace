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


lower_accepted_values = [
    "hidden collections",
    "tbm/ami",
    "digital",
    "conservation",
    "missing",
    "backlog",
    "mold",
]

uris_to_replace = [
    "/repositories/2/assessments/5",
    "/repositories/2/assessments/25",
    "/repositories/2/assessments/28",
    "/repositories/2/assessments/46",
    "/repositories/2/assessments/47",
    "/repositories/2/assessments/48",
    "/repositories/2/assessments/56",
    "/repositories/2/assessments/62",
    "/repositories/2/assessments/64",
    "/repositories/2/assessments/71",
    "/repositories/2/assessments/84",
    "/repositories/2/assessments/86",
    "/repositories/2/assessments/88",
    "/repositories/2/assessments/89",
    "/repositories/2/assessments/90",
    "/repositories/2/assessments/91",
    "/repositories/2/assessments/92",
    "/repositories/2/assessments/104",
    "/repositories/2/assessments/107",
    "/repositories/2/assessments/111",
    "/repositories/2/assessments/113",
    "/repositories/2/assessments/114",
    "/repositories/2/assessments/115",
    "/repositories/2/assessments/116",
    "/repositories/2/assessments/126",
    "/repositories/2/assessments/127",
    "/repositories/2/assessments/129",
    "/repositories/2/assessments/130",
    "/repositories/2/assessments/133",
    "/repositories/2/assessments/134",
    "/repositories/2/assessments/135",
    "/repositories/2/assessments/138",
    "/repositories/2/assessments/139",
    "/repositories/2/assessments/140",
    "/repositories/2/assessments/143",
    "/repositories/2/assessments/146",
    "/repositories/2/assessments/150",
    "/repositories/2/assessments/151",
    "/repositories/2/assessments/152",
    "/repositories/2/assessments/155",
    "/repositories/2/assessments/159",
    "/repositories/2/assessments/162",
    "/repositories/2/assessments/166",
    "/repositories/2/assessments/167",
    "/repositories/2/assessments/168",
    "/repositories/2/assessments/169",
    "/repositories/2/assessments/171",
    "/repositories/2/assessments/173",
    "/repositories/2/assessments/174",
    "/repositories/2/assessments/175",
    "/repositories/2/assessments/176",
    "/repositories/2/assessments/182",
    "/repositories/2/assessments/183",
    "/repositories/2/assessments/184",
    "/repositories/2/assessments/185",
    "/repositories/2/assessments/186",
    "/repositories/2/assessments/188",
    "/repositories/2/assessments/191",
    "/repositories/2/assessments/192",
    "/repositories/2/assessments/194",
    "/repositories/2/assessments/195",
    "/repositories/2/assessments/196",
    "/repositories/2/assessments/198",
    "/repositories/2/assessments/199",
    "/repositories/2/assessments/203",
    "/repositories/2/assessments/205",
    "/repositories/2/assessments/206",
    "/repositories/2/assessments/207",
    "/repositories/2/assessments/208",
    "/repositories/2/assessments/212",
    "/repositories/2/assessments/213",
    "/repositories/2/assessments/214",
    "/repositories/2/assessments/216",
    "/repositories/2/assessments/219",
    "/repositories/2/assessments/221",
    "/repositories/2/assessments/222",
    "/repositories/2/assessments/224",
    "/repositories/2/assessments/228",
    "/repositories/2/assessments/230",
    "/repositories/2/assessments/232",
    "/repositories/2/assessments/234",
    "/repositories/2/assessments/238",
    "/repositories/2/assessments/239",
    "/repositories/2/assessments/242",
    "/repositories/2/assessments/243",
    "/repositories/2/assessments/244",
    "/repositories/2/assessments/248",
    "/repositories/2/assessments/257",
    "/repositories/2/assessments/258",
    "/repositories/2/assessments/260",
    "/repositories/2/assessments/262",
    "/repositories/2/assessments/263",
    "/repositories/2/assessments/264",
    "/repositories/2/assessments/265",
    "/repositories/2/assessments/266",
    "/repositories/2/assessments/267",
    "/repositories/2/assessments/268",
    "/repositories/2/assessments/269",
    "/repositories/2/assessments/270",
    "/repositories/2/assessments/272",
    "/repositories/2/assessments/273",
    "/repositories/2/assessments/274",
    "/repositories/2/assessments/275",
    "/repositories/2/assessments/276",
    "/repositories/2/assessments/277",
    "/repositories/2/assessments/278",
    "/repositories/2/assessments/279",
    "/repositories/2/assessments/280",
    "/repositories/2/assessments/281",
    "/repositories/2/assessments/282",
    "/repositories/2/assessments/284",
    "/repositories/2/assessments/285",
    "/repositories/2/assessments/286",
    "/repositories/2/assessments/289",
    "/repositories/2/assessments/290",
    "/repositories/2/assessments/291",
    "/repositories/2/assessments/292",
    "/repositories/2/assessments/293",
    "/repositories/2/assessments/294",
    "/repositories/2/assessments/297",
    "/repositories/2/assessments/299",
    "/repositories/2/assessments/300",
    "/repositories/2/assessments/301",
    "/repositories/2/assessments/304",
    "/repositories/2/assessments/306",
    "/repositories/2/assessments/307",
    "/repositories/2/assessments/309",
    "/repositories/2/assessments/312",
    "/repositories/2/assessments/314",
    "/repositories/2/assessments/316",
    "/repositories/2/assessments/320",
    "/repositories/2/assessments/325",
    "/repositories/2/assessments/327",
    "/repositories/2/assessments/328",
    "/repositories/2/assessments/331",
    "/repositories/2/assessments/335",
    "/repositories/2/assessments/339",
    "/repositories/2/assessments/341",
    "/repositories/2/assessments/346",
    "/repositories/2/assessments/348",
    "/repositories/2/assessments/353",
    "/repositories/2/assessments/354",
    "/repositories/2/assessments/355",
    "/repositories/2/assessments/356",
    "/repositories/2/assessments/357",
    "/repositories/2/assessments/359",
    "/repositories/2/assessments/365",
    "/repositories/2/assessments/371",
    "/repositories/2/assessments/372",
    "/repositories/2/assessments/375",
    "/repositories/2/assessments/377",
    "/repositories/2/assessments/380",
]


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
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", f"{mode}_baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
        )

    def run(self):
        for uri in uris_to_replace:
            new_purpose = None
            assessment_json = self.as_client.get_json(uri)
            purpose = assessment_json["purpose"]
            if len(purpose) >= 25:
                self.move_purpose_to_scope(assessment_json)
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
            if new_purpose:
                print(f"{purpose}\t{new_purpose}")
            else:
                print(f"{purpose}\tno new purpose")
            new_purpose = None

    def move_purpose_to_scope(self, assessment):
        purpose = assessment["purpose"]
        scope = assessment.get("scope")
        new_scope = ". ".join([scope, purpose]) if scope else purpose
        print(new_scope)

        # change the assessment data
        # update scope of assessment to new text
        # replace purpose of assessment with value of new_purpose
        # post the new assessment
