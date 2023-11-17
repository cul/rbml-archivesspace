import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.physdesc_to_extent import PhysdescToExtent
from asnake.utils import get_note_text


class TestPhysdescToExtent(unittest.TestCase):
    def test_init(self):
        pass

    @patch("scripts.physdesc_to_extent.PhysdescToExtent.__init__", return_value=None)
    def test_has_folder_instance(self, mock_init):
        # no instances
        # digital object
        # box no folder
        # with folder as subcontainer
        for filename in ["ao_folder", "ao_with_dao_folder"]:
            with open(Path("fixtures", f"{filename}.json")) as f:
                json_data = json.load(f)
            self.assertTrue(PhysdescToExtent().has_folder_instance(json_data))
        for filename in ["ao_dao_only", "ao_no_instances", "ao_with_dao_box"]:
            with open(Path("fixtures", f"{filename}.json")) as f:
                json_data = json.load(f)
            self.assertIsNone(PhysdescToExtent().has_folder_instance(json_data))

    def test_run(self):
        pass

    # @patch("scripts.physdesc_to_extent.PhysdescToExtent.has_folder_instance")
    @patch("scripts.physdesc_to_extent.PhysdescToExtent.__init__", return_value=None)
    def test_can_update(self, mock_init):
        with open(Path("fixtures", "ao_folder.json")) as f:
            json_data = json.load(f)
        self.assertFalse(PhysdescToExtent().can_update(json_data))
        with open(Path("fixtures", "ao_no_instances.json")) as f:
            json_data = json.load(f)
        self.assertTrue(PhysdescToExtent().can_update(json_data))

    def test_move_to_extent_statement(self):
        # writing to ASpace
        pass

    @patch("asnake.utils.get_note_text")
    @patch("scripts.physdesc_to_extent.PhysdescToExtent.__init__", return_value=None)
    def test_parsable_physdesc(self, mock_init, mock_note_text):
        mock_note_text.return_value = "something"

    # fixtures:
    # has physdesc that matches extent form
    # has physdesc that doesn't match
    # doesn't have physdesc
    # args:
    #   physdesc (obj): ASnake abstraction layer note
    #   extent_type (str): extent type, e.g., folder

    # with open(Path("fixtures", "extent_physdesc.json")) as f:
    #   json_data = json.load(f)
    # parsed_with_folder = PhysdescToExtent().parsable_physdesc(json_data)
    # self.assertIsInstance(parsed_with_folder, object)
    # self.assertEqual(parsed_with_folder, json_data)

    # for filename in ["physdesc_legit.json", "ao_with_date.json"]:
    #   with open(Path("fixtures", f"{filename}.json")) as f:
    #       json_data = json.load(f)
    #   self.assertIsNone(PhysdescToExtent().parsable_physdesc(json_data))

    # mock get_note_text
    # @patch("asnake.utils.get_note_text", return_value=None)
    # This is probably wrong but it's a start
    @patch("scripts.physdesc_to_extent.PhysdescToExtent.__init__", return_value=None)
    def test_parse_physdesc_number(self):
        pass
