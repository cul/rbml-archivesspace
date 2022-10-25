import unittest
from unittest.mock import patch

from scripts.aspace_upgrade_tests import APIComparer, EADComparer


class TestAPIComparer(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_init(self, mock_aspace):
        api_comparer = APIComparer()
        self.assertTrue(api_comparer)

    @patch("scripts.aspace_client.ArchivesSpaceClient.get_json", return_value=None)
    @patch("scripts.aspace_upgrade_tests.APIComparer.__init__", return_value=None)
    def test_compare_records(self, mock_aspace, mock_get_json):
        api_comparer = APIComparer()
        api_comparer.dev_client = mock_aspace
        api_comparer.prod_client = mock_aspace
        records_comparer = api_comparer.compare_records("uri")
        self.assertTrue(records_comparer)


class TestEADComparer(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_init(self, mock_aspace):
        ead_comparer = EADComparer()
        self.assertTrue(ead_comparer)
