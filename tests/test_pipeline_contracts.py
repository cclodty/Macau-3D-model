import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_architecture_manifest import validate as validate_architecture  # noqa: E402
from validate_material_manifest import validate as validate_materials  # noqa: E402
from validate_site_manifest import validate as validate_site  # noqa: E402


class PipelineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.architecture = json.loads((ROOT / "architecture_manifest.json").read_text(encoding="utf-8"))
        cls.materials = json.loads((ROOT / "material_manifest.json").read_text(encoding="utf-8"))
        cls.site = json.loads((ROOT / "site_manifest.json").read_text(encoding="utf-8"))

    def test_checked_in_manifests_are_valid(self):
        self.assertEqual([], validate_architecture(self.architecture))
        self.assertEqual([], validate_materials(self.materials))
        self.assertEqual([], validate_site(self.site))

    def test_every_architecture_slot_has_exactly_one_binding(self):
        expected = {
            slot
            for module in self.architecture["modules"]
            for slot in module["expected_material_slots"]
        }
        self.assertEqual(expected, set(self.materials["slot_bindings"]))

    def test_unknown_material_binding_is_rejected(self):
        changed = copy.deepcopy(self.materials)
        changed["slot_bindings"]["M_Podium_Facade"] = "missing_material"
        self.assertTrue(any("unknown material" in error for error in validate_materials(changed)))

    def test_blender_entry_points_exist(self):
        self.assertTrue((SCRIPTS / "blender_architecture_setup.py").is_file())
        self.assertTrue((SCRIPTS / "blender_material_setup.py").is_file())
        self.assertTrue((SCRIPTS / "blender_build_blockout.py").is_file())


if __name__ == "__main__":
    unittest.main()
