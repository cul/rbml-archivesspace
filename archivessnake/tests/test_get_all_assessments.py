import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.get_all_assessments import AssessmentFinder, AssessmentUpdater


def mock_assessments_generator(filename="assessment.json"):
    with open(Path("fixtures", filename)) as s:
        accession = json.load(s)
    count = 0
    while count < 2:
        count += 1
        yield accession


class TestAssessmentFinder(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.get_assessments")
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_run(self, mock_aspace, mock_get_assessments):
        mock_get_assessments.return_value = mock_assessments_generator()
        assessment_finder = AssessmentFinder().run("csv_filepath.csv")
        self.assertTrue(assessment_finder)

    @patch("scripts.get_all_assessments.AssessmentFinder.__init__", return_value=None)
    def test_get_assessment_info(self, mock_init):
        with open(Path("fixtures", "assessment.json")) as f:
            with_purpose = json.load(f)
        with open(Path("fixtures", "assessment_no_purpose.json")) as f:
            without_purpose = json.load(f)
        get_info_with_purpose = AssessmentFinder().get_assessment_info(with_purpose)
        get_info_without_purpose = AssessmentFinder().get_assessment_info(
            without_purpose
        )
        self.assertIsInstance(get_info_with_purpose, list)
        self.assertEqual(len(get_info_with_purpose), 6)
        self.assertIsNone(get_info_without_purpose)

    @patch("scripts.aspace_client.ArchivesSpaceClient.get_assessments")
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_get_notes_to_change(self, mock_aspace, mock_get_assessments):
        mock_get_assessments.return_value = mock_assessments_generator(
            "assessment_to_change.json"
        )
        get_notes = AssessmentFinder().get_notes_to_change()
        self.assertTrue(get_notes)


class TestAssessmentUpdater(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_init(self, mock_aspace):
        assessment_updater = AssessmentUpdater()
        self.assertTrue(assessment_updater)

    @patch("scripts.get_all_assessments.AssessmentUpdater.__init__", return_value=None)
    def test_get_new_purpose(self, mock_init):
        self.assertIsNone(AssessmentUpdater().get_new_purpose("don't recognize"))
        self.assertEqual(
            AssessmentUpdater().get_new_purpose("Missing materials."), "Missing"
        )
        self.assertEqual(
            AssessmentUpdater().get_new_purpose("Digital contents"), "Digital"
        )
