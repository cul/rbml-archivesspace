import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.update_order import DateException, OrderUpdater


class TestOrderUpdater(unittest.TestCase):
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_init(self, mock_aspace):
        update_order = OrderUpdater()
        self.assertTrue(update_order)

    @patch(
        "scripts.update_order.ArchivesSpaceClient.update_aspace_field",
        return_value=None,
    )
    @patch("scripts.aspace_client.ArchivesSpaceClient.get_json")
    @patch("scripts.aspace_client.ArchivesSpaceClient.__init__", return_value=None)
    def test_add_date_from_string(
        self, mock_init, mock_get_json, mock_update_aspace_field
    ):
        with open(Path("fixtures", "ao_without_date.json")) as s:
            ao_without_date = json.load(s)
        mock_get_json.return_value = ao_without_date
        added_date = OrderUpdater().add_date_from_string("1974", "/fake/uri")
        self.assertTrue(added_date)
        with self.assertRaises(DateException):
            OrderUpdater().add_date_from_string("This is a title", "/fake/uri")
        with open(Path("fixtures", "ao_with_date.json")) as s:
            ao_with_date = json.load(s)
        mock_get_json.return_value = ao_with_date
        not_added_date = OrderUpdater().add_date_from_string("1974", "/fake/uri")
        self.assertTrue(not_added_date)

    @patch("scripts.update_order.OrderUpdater.__init__", return_value=None)
    def test_create_date_object(self, mock_init):
        expected_single_dates = ["1968", "1968-03", "1968-03-21"]
        for x in expected_single_dates:
            date_object = OrderUpdater().create_date_object(x)
            self.assertIsInstance(date_object, dict)
            self.assertEqual(len(date_object.items()), 4)
            self.assertEqual(date_object["date_type"], "single")
            self.assertEqual(date_object["begin"], x)
        expected_date_range = "1950-1960"
        date_object = OrderUpdater().create_date_object(expected_date_range)
        self.assertIsInstance(date_object, dict)
        self.assertEqual(len(date_object.items()), 5)
        self.assertEqual(date_object["date_type"], "inclusive")
        incorrect_dates = ["n.d.", "1941 sept", "1947-9", "4/13/1990"]
        for x in incorrect_dates:
            with self.assertRaises(DateException):
                OrderUpdater().create_date_object(x)
