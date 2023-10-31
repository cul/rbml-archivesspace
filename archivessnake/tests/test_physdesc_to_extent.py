import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.physdesc_to_extent import PhysdescToExtent


class TestPhysdescToExtent(unittest.TestCase):
    def test_init(self):
        pass

    @patch("scripts.physdesc_to_extent.PhysdescToExtent.__init__", return_value=None)
    def test_has_folder_instance(self, mock_init):
        # no instances
        # digital object
        # box no folder
        # with folder as subcontainer
        physdesc_to_extent = PhysdescToExtent()
        for filename in ["ao_folder", "ao_with_dao_folder"]:
            with open(Path("fixtures", f"{filename}.json")) as f:
                json_data = json.load(f)
            self.assertTrue(physdesc_to_extent.has_folder_instance(json_data))
        for filename in ["ao_dao_only", "ao_no_instances", "ao_with_dao_box"]:
            with open(Path("fixtures", f"{filename}.json")) as f:
                json_data = json.load(f)
            self.assertIsNone(physdesc_to_extent.has_folder_instance(json_data))

    def test_run(self):
        pass

    def test_can_update(self):
        pass

    def test_move_to_extent_statement(self):
        # writing to ASpace
        pass

    def test_parsable_physdesc(self):
        pass

    # mock get_note_text
    def test_parse_physdesc_number(self):
        pass
