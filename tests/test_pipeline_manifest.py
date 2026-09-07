import json
from pathlib import Path
import tempfile
import unittest

from macau_pipeline.manifest import BakeManifest, TriangulationSettings, write_manifest


class ManifestTests(unittest.TestCase):
    def manifest(self, **overrides):
        values = dict(
            low_poly="Wall_low",
            high_poly="Wall_high",
            cage="Wall_cage",
            cage_extrusion=0.01,
            max_ray_distance=0.02,
            normal_space="TANGENT",
            triangulation=TriangulationSettings(),
            blender_version="4.2.0",
            saved_utc="2026-09-07T00:00:00+00:00",
        )
        values.update(overrides)
        return BakeManifest(**values)

    def test_serializes_required_reproducibility_settings(self):
        data = json.loads(self.manifest().to_json())
        self.assertEqual(data["normal_space"], "TANGENT")
        self.assertEqual(data["triangulation"]["quad_method"], "FIXED")
        self.assertTrue(data["triangulation"]["keep_custom_normals"])
        self.assertEqual(data["cage"], "Wall_cage")

    def test_rejects_object_space_and_negative_distance(self):
        with self.assertRaises(ValueError):
            self.manifest(normal_space="OBJECT").validate()
        with self.assertRaises(ValueError):
            self.manifest(max_ray_distance=-0.1).validate()

    def test_writes_utf8_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_manifest(self.manifest(low_poly="澳門牆_low"), Path(directory) / "wall.bake.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["low_poly"], "澳門牆_low")


if __name__ == "__main__":
    unittest.main()
