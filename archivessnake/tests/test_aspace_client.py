import unittest
from unittest.mock import Mock, patch

from scripts.aspace_client import ArchivesSpaceClient


class ArchivesSpaceClientTests(unittest.TestCase):
    def setUp(self):
        self.as_config = (
            "https://sandbox.archivesspace.org/api/",
            "admin",
            "admin",
        )

    @patch(
        "asnake.client.web_client.ASnakeClient.get.return_value.json.return_value.search.with_params"
    )
    @patch("asnake.client.web_client.ASnakeClient.get")
    @patch("asnake.client.web_client.ASnakeClient.authorize")
    def test_data(self, mock_authorize, mock_get, mock_search):
        """Asserts that individual digital_objects are returned."""
        mock_get.return_value.text = "v3.0.2"
        client = ArchivesSpaceClient(*self.as_config)

        mock_digital_object = Mock()
        expected_return = {"jsonmodel_type": "digital_object"}
        mock_digital_object.json.return_value = expected_return
        mock_search.return_value = [mock_digital_object]

        result = list(client.get_digital_objects(2))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_return)
