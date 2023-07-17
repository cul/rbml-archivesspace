import unittest
from unittest.mock import patch

from scripts.google_sheets_client import GoogleSheetsClient

from .helpers import mock_build_service, mock_get_sheet_info


class TestGoogleSheetsClient(unittest.TestCase):
    @patch("scripts.google_sheets_client.build")
    def test_init(self, mock_build):
        mock_build.return_value = mock_build_service()
        google_sheets_client = GoogleSheetsClient(
            "access_token",
            "refresh_token",
            "client_id",
            "client_secret",
            "spreadsheet_id",
        )
        self.assertTrue(google_sheets_client)

    @patch("scripts.google_sheets_client.GoogleSheetsClient.get_sheet_info")
    def test_get_sheet_tabs(self, mock_sheet_info):
        mock_sheet_info.return_value = mock_get_sheet_info("sheet_info.json")
        sheet_tabs = GoogleSheetsClient(
            "access_token",
            "refresh_token",
            "client_id",
            "client_secret",
            "spreadsheet_id",
        ).get_sheet_tabs()
        self.assertEqual(len(sheet_tabs), 5)
        self.assertTrue("Collection Management" in sheet_tabs)
