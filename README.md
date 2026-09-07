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
