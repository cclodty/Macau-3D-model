# Macau modular city scene

This repository contains a Blender scene builder for a modular, Unreal-friendly
city block.  The generated scene deliberately keeps buildings, façade modules,
props, roads, and skyline masses as separate assets instead of joining a street
into one mesh.

## Build the scene

Run the script from Blender 4.x:

```bash
blender --background --python scripts/build_asset_hierarchy.py
```

By default this writes `build/macau_asset_hierarchy.blend` and
`build/instance_manifest.json`.  Override the output directory with:

```bash
blender --background --python scripts/build_asset_hierarchy.py -- --output /path/to/output
```

You can also open Blender's Scripting workspace and run the script. In that
case, relative output is resolved from the repository (or the current working
directory when the script path is unavailable).

## Scene organization

The top-level `MACAU_CITY` collection is split by both asset role and viewing
distance:

| Collection | Purpose | Unreal usage |
| --- | --- | --- |
| `01_HERO/Buildings` | Podium, tower, and rooftop structure sections | Individual Static Meshes |
| `01_HERO/Facade_Modules` | Reusable window groups, balconies, storefront frames, and canopies | ISM/HISM candidates |
| `01_HERO/Props` | Air conditioners, railings, lamp posts, and bins | ISM/HISM candidates |
| `01_HERO/Roads` | Intersection, straight road, sidewalk, and kerb sections | Tiled Static Meshes |
| `02_CONTEXT` | Mid-distance buildings with small relief removed | Individual Static Meshes |
| `03_SKYLINE` | Distant silhouette-only building masses | HLOD/background meshes |

Repeated objects share one Blender mesh datablock (the equivalent of linked
duplicates). Their transforms are additionally written to the JSON manifest so
an Unreal import pipeline can reconstruct Instanced Static Mesh or Hierarchical
Instanced Static Mesh components. Coordinates in that file are converted from
Blender metres (`X, Y, Z`) to Unreal centimetres (`X, -Y, Z`), and rotations are
stored as quaternions to avoid Euler-order ambiguity.

Each generated object also contains custom properties (`asset_role`,
`distance_band`, `unreal_mode`, and `asset_id`) for filtering and validation.

## Unreal import notes

1. Export only objects tagged `STATIC_MESH` once per `asset_id` as base meshes.
2. Read `instance_manifest.json` and create ISM/HISM components for records in
   `instance_groups`; all transforms in a group reference the same base mesh.
3. Keep the four road tile types independent so World Partition can stream and
   cull them per cell.
4. Import `03_SKYLINE` with simple collision disabled and use it only beyond the
   context area.
5. Do not apply a blanket **Join** operation to any top-level collection.
# Macau 3D material contract

This repository tracks the lightweight, reviewable contract for Macau environment
materials. Large photographs, baked normal maps, and atlases remain in the external
object store; no production texture binary is committed here.

## Files

* `config/material_manifest.json` is the source of truth for DCC names, Unreal
  instances, PBR texture locations, color spaces, dimensions, density, defaults,
  blending capabilities, provenance, and bundle version.
* `config/texture_versions.json` pins each downloaded binary by SHA-256 and asset
  version. Populate `files` when the `macau-textures-2026.09` bundle is released.
* `config/material_slots.json` is the optional Blender/export material-slot inventory.
* `previews/material_swatches.svg` is a small, repository-native review sheet; its
  colors match each manifest fallback, not the absent production photography.

## Usage

Validate metadata while allowing absent external binaries:

```sh
python3 scripts/validate_materials.py
```

After downloading a binary bundle into `textures/`, enforce every texture:

```sh
python3 scripts/validate_materials.py --require-textures
```

The validator checks naming, Unreal texture suffixes, color space/channel intent,
PNG bit depth and dimensions, power-of-two manifest dimensions, categories, and
material-slot assignments. ORM uses **R=ambient occlusion, G=roughness,
B=metallic**. Base color and emissive are sRGB; normal, ORM, and mask are linear.

Create or refresh Blender preview materials (Blender 4.x):

```sh
blender scene.blend --background --python scripts/build_blender_materials.py -- \
  --manifest config/material_manifest.json
```

Missing base-color images receive an obvious procedural checker based on the
manifest fallback. Missing normal/ORM/emissive maps retain scalar defaults. The
builder stores wetness and aging support as material custom properties so an
export pipeline can map them to `M_Macau_Surface` parameters.
