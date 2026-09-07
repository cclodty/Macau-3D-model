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
