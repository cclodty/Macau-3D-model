"""Dependency-free bake manifest helpers shared by Blender tooling and tests."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TriangulationSettings:
    quad_method: str = "FIXED"
    ngon_method: str = "BEAUTY"
    min_vertices: int = 4
    keep_custom_normals: bool = True

    def validate(self) -> None:
        if self.quad_method not in {"BEAUTY", "FIXED", "FIXED_ALTERNATE", "SHORTEST_DIAGONAL", "LONGEST_DIAGONAL"}:
            raise ValueError(f"Unsupported quad method: {self.quad_method}")
        if self.ngon_method not in {"BEAUTY", "CLIP"}:
            raise ValueError(f"Unsupported ngon method: {self.ngon_method}")
        if self.min_vertices < 4:
            raise ValueError("min_vertices must be at least 4")


@dataclass(frozen=True)
class BakeManifest:
    low_poly: str
    high_poly: str
    cage: str | None
    cage_extrusion: float
    max_ray_distance: float
    normal_space: str
    triangulation: TriangulationSettings
    blender_version: str
    saved_utc: str

    def validate(self) -> None:
        if not self.low_poly or not self.high_poly:
            raise ValueError("low_poly and high_poly are required")
        if self.cage_extrusion < 0 or self.max_ray_distance < 0:
            raise ValueError("Bake distances cannot be negative")
        if self.normal_space != "TANGENT":
            raise ValueError("This pipeline only accepts tangent-space normals")
        self.triangulation.validate()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_manifest(manifest: BakeManifest, destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.to_json(), encoding="utf-8")
    return path
