# Macau streetscape asset kit

This repository contains a lightweight, modular streetscape kit for building
Macau road scenes.  The geometry is stored as Wavefront OBJ so it can be used
directly in Blender, Godot, Unity, Unreal, or a GIS/DCC pipeline without a
proprietary dependency.

## Contents

- `assets/environment/` — pavement, curb, drain, asphalt, manhole, and road
  marking modules.
- `assets/street_furniture/` — Macau-oriented lights, signals, signs, railings,
  utilities, bus-stop, and parking objects.
- `assets/urban_details/` — pipes, cables, condensate drains, CCTV, drying
  racks, security grilles, lightboxes, and small storefront equipment.
- `assets/mobility/` — left-hand-traffic vehicles and compact pedestrian
  silhouettes.
- `scenes/macau_street_layout.json` — explicit, deterministic placement data.
- `tools/generate_assets.py` — dependency-free source generator for every OBJ.

All dimensions and transforms are in metres.  Object forward is local **+Y**,
up is **+Z**, and rotations use degrees in XYZ order.  The sample street uses
left-hand traffic.  Pedestrians and vehicles are kept outside the four
documented building-inspection view corridors.

## Regenerate and validate

```bash
python3 tools/generate_assets.py
python3 tools/validate_scene.py
```

The layout deliberately contains no random placement. Each instance has a
stable ID, exact transform, curb offset, and placement note so transforms can
be replaced one-by-one with photo-survey measurements when reference images or
survey control points are available.
