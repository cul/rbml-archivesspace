import unittest
from unittest.mock import patch

from scripts.aspace_upgrade_tests import APIComparer, EADComparer


class TestAPIComparer(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_init(self, mock_aspace):
        api_comparer = APIComparer()
        self.assertTrue(api_comparer)


class TestEADComparer(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_init(self, mock_aspace):
        ead_comparer = EADComparer()
        self.assertTrue(ead_comparer)
