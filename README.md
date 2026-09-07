# Macau 3D model delivery workspace

This repository defines a repeatable optimisation, validation, comparison, and
delivery workflow for the Macau scene. Source geometry and reference
photographs are not committed to this repository; place authorised inputs in
`source/` and run the Blender pipeline before approving a delivery.

## Quick start

1. Open the scene in Blender 4.x and save the working file under
   `deliverables/master/`.
2. Review and adapt `config/pipeline.json` to the target platform.
3. Run the validator and exporter:

   ```bash
   blender --background deliverables/master/macau_master.blend \
     --python tools/blender_pipeline.py -- --config config/pipeline.json
   ```

4. Render every camera listed in `deliverables/reference/camera_manifest.csv`.
   Compare each render against its authorised reference at 50% opacity and put
   the resulting daytime overlays in `deliverables/screenshots/day/`.
5. Complete the acceptance, provenance, privacy, and copyright fields in the
   CSV/Markdown documents under `deliverables/`. A delivery is not approved
   while any item remains `PENDING` or `BLOCKED`.

The pipeline validates transforms, names, UV/lightmap channels, face normals,
material variants, per-importance texture limits, collision objects, and LOD naming. It exports glTF
2.0 and FBX in metres with Y-up conversion handled by the exporters.

## Repository policy

- Do not commit identifiable faces, licence plates, private interiors, or raw
  reference photos.
- Do not add third-party assets until their licence and source are recorded in
  `deliverables/licenses.csv`.
- Do not treat generated empty folders or templates as evidence of completed
  artistic review. Acceptance requires the signed checklist and actual renders.
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
