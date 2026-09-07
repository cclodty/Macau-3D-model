import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("validator", Path("scripts/validate_materials.py"))
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ManifestValidationTests(unittest.TestCase):
    def test_repository_manifest_is_valid_without_external_bundle(self):
        errors, warnings = validator.validate(Path("config/material_manifest.json"), Path("config/material_slots.json"), False)
        self.assertEqual(errors, [])
        self.assertGreater(len(warnings), 0)

    def test_bad_unreal_suffix_is_rejected(self):
        data = json.loads(Path("config/material_manifest.json").read_text())
        data["materials"][0]["textures"]["normal"] = "facade/wrong.png"
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "manifest.json"
            manifest.write_text(json.dumps(data))
            errors, _ = validator.validate(manifest, Path("config/material_slots.json"), False)
        self.assertTrue(any("lacks Unreal suffix _N" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
