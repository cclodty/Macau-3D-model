# Macau architecture interchange source of truth

For a new local Blender/Codex session, start with [`docs/handoff.md`](docs/handoff.md). It records the current phase, first-run commands, visual checks, reference handoff requirements, and the next recommended Codex instruction.

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

The current second-stage pass adds facade air-conditioning units and service pipes, a podium column rhythm, individual shop awnings, kerbs, drains, and street lights. See `docs/production-stages.md` for the seven-stage production and acceptance plan.

## Phase-three calibration

The third-stage generator adds separate window frames and balcony rails for the Hero facade. Its geometry remains provisional. `references/calibration_manifest.json` is the evidence ledger for dimensions and the four required photo-matching views; the validator prevents a file containing estimates from being labelled `CALIBRATED`.

Register only reference media that the project is permitted to use. Give each source a stable ID, capture date/epoch, provenance, licence, and repository-relative or controlled external URI. Replace a measurement's `BLOCKOUT_ESTIMATE` only when its `source_id` points to that registered evidence. Run `python3 scripts/validate_project.py` after every calibration edit.

## Integration status

The architecture, PBR, and site manifests are now consumed by one blockout build entry point and checked by one project validator. PR #17 established the integrated foundation; subsequent modelling passes should change the manifests and generators together rather than introducing independent binary-only state.
