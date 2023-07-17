import unittest
from unittest.mock import patch

from scripts.delete_orphan_daos import DigitalObjectDeleter


class TestDigitalObjectDeleter(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_init(self, mock_aspace):
        dao_deleter = DigitalObjectDeleter()
        self.assertTrue(dao_deleter)
