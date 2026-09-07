# Macau 3D Model

本專案的 Unreal 資產製作規範集中於以下文件：

- [Nanite、LOD 與碰撞製作規範](docs/unreal-asset-guidelines.md)
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
