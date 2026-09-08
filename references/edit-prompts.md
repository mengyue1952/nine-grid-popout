# Semantic edit prompts

Use these only for the two Photo 1 edits. Preserve the source photo separately.

## A. Person removal for the continuous background

Use case: precise-object-edit
Asset type: source for a continuous 2x2 nine-grid background region
Primary request: Remove the complete person from Photo 1 and reconstruct only the environment that the person occluded.
Input image: Photo 1 is the edit target.
Constraints: Keep the original scene, camera, perspective, framing, color, lighting, texture, and all non-person content unchanged. The repaired area must continue surrounding structures and textures naturally.
Avoid: any person, body part, silhouette, residual shadow shaped like the person, duplicated scenery, smeared texture, obvious inpainting boundary, text, watermark, grid, or collage.

## B. Complete person extraction

Use case: background-extraction
Asset type: transparent foreground layer for deterministic compositing
Primary request: Delete every background pixel and return the complete original person on a genuine transparent background.
Input image: original Photo 1 is the edit target; do not use the repaired background.
Constraints: Preserve every visible part of the original person, including head, hair, facial features, torso, arms, hands, fingers, legs, feet, shoes, clothing, backpack and accessories. Preserve pose, anatomy, proportions, perspective, outline, color, illumination, sharpness, and natural semitransparent edge pixels. Keep the entire person inside the output.
Avoid: regeneration, beautification, face changes, pose changes, missing or invented anatomy, altered clothes, halo, colored matte, white background, shadow, text, watermark, cropping, or scaling.

After either edit, visually inspect at original detail. Do not ask the model to resize the person or perform final placement; deterministic local processing handles those steps. Use these prompts only when the user explicitly asks Codex to create a missing derivative and permits the required image-editing operation.
