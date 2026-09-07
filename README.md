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
