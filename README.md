# Macau architecture interchange source of truth

This repository intentionally keeps the reviewable pipeline contract separate from large binary model files. `architecture_manifest.json` defines the five delivery modules, names, transforms, Unreal destinations, collision/material expectations, optimisation status, output filenames, progress, and external binary references. Update the manifest version and each module's `binary_asset` record when a formal `.blend` is promoted in the external asset registry.

## Validate the contract

The semantic validator uses only the Python standard library:

```bash
python3 scripts/validate_architecture_manifest.py
```

The companion JSON Schema is suitable for editor and CI integration. If the optional `jsonschema` package is available, run:

```bash
python3 -m jsonschema -i architecture_manifest.json schemas/architecture-manifest.schema.json
```

## Generate Blender collections and pipeline greyboxes

With Blender available, create five empty module Collections beneath `EXPORT_ARCHITECTURE`:

```bash
blender --background --python scripts/blender_architecture_setup.py -- \
  --save build/architecture-empty.blend
```

Add metre-scale placeholder geometry, collision hulls where required, save a disposable working file, and export five test FBXs:

```bash
blender --background --python scripts/blender_architecture_setup.py -- \
  --greybox --export-dir build/fbx --save build/architecture-greybox.blend
```

The script reads the manifest rather than duplicating asset destinations and filenames. It sets metric scene units, uses the shared world origin contract, attaches searchable custom properties to the scene and Collections, creates placeholder material slots, and applies the documented `SM_…` / `UCX_…` naming templates. Generated `.blend` and FBX files are disposable validation artefacts and must not replace the external formal binaries.

## Unified PBR material contract

`material_manifest.json` defines the shared placeholder palette and the Unreal master-material mapping. ORM textures always use **R = ambient occlusion, G = roughness, B = metallic**. Validate both architecture and material contracts together with:

```bash
python3 scripts/validate_project.py
```

The architecture greybox command above now creates the canonical materials and assigns manifest-backed variants to every declared mesh slot. To generate only the Blender Principled BSDF preview library, use:

```bash
blender --background --python scripts/blender_material_setup.py
```

The generated materials deliberately contain no embedded textures. `slot_bindings` is the explicit bridge between the architecture manifest's material slots and the canonical PBR definitions; the combined validator rejects missing or surplus bindings. Replace placeholders with licensed source textures, preserve the manifest IDs and Unreal mappings, and record formal binary versions externally before promoting the greybox to a surveyed production model.

## First estate and street blockout

The first recognisable modelling pass is driven by `site_manifest.json`. It creates a podium, three residential towers with floor/window rhythm, balconies, rooftop plant, ten shopfronts, three entrances, a provisional section of Avenida de Venceslau de Morais, pavement, road markings, and three review cameras:

```bash
blender --background --python scripts/blender_build_blockout.py -- \
  --save build/PatTat_Blockout.blend
```

Every generated object is marked `ESTIMATED_AWAITING_SURVEY`. The dimensions are an editable modelling baseline—not a claim of surveyed accuracy—and must be calibrated against licensed photographs and measurements before the asset advances beyond blockout.

## Integration status

The local Git object database contains PR #16 only. It supplies the five-module architecture contract and greybox generator. No remote, additional PR refs, or recoverable dangling commits are present in this checkout, so the PBR contract above completes the missing reviewable foundation locally rather than depending on unavailable PR branches.
