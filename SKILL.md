---
name: nine-grid-popout
description: Build a fixed 3x3 six-photo grid and composite Photo 1's supplied transparent person cutout over it at a default 120% scale with exact P=T anchoring. Use for 九宫格、九宫格突破人物、人物破框、六图九宫格 and similar deterministic photo-compositing requests; afterward support user-directed scale or position variants.
---

# Nine-grid popout portrait

Create a deterministic two-layer PNG from six ordered photos plus two user-prepared Photo 1 assets: a person-free background and a complete transparent person cutout. Do not upload these images or regenerate supplied assets unless the user explicitly requests and authorizes that edit.

## Required inputs

- Photo 1 person-free background, already repaired by the user.
- Photo 1 complete transparent person cutout.
- Photos 2–6 in an explicit order.

If either Photo 1 derivative is missing, ask for it. Keep every input untouched.

## Workflow

1. Inspect the inputs. Confirm that the cutout has genuine transparency and a complete subject.
2. Run `scripts/nine_grid.py build-grid` using the supplied Photo 1 background and original Photos 2–6. This stage ends with a standalone grid background; do not add the cutout yet.
3. Run `scripts/nine_grid.py scale-cutout` on the uploaded transparent cutout with scale `1.2` (120%). Derive this edition directly from the original cutout with one high-quality RGBA resampling operation; do not regenerate, re-extract, retouch, or otherwise alter its visible content.
4. Run `scripts/nine_grid.py composite` with the 120% cutout. Read T once from the grid metadata as the lower-right vertex of cell 5. Recompute P from the scaled cutout's lowest nontransparent pixels. Translate only the scaled cutout so P=T, then lock its position.
5. Keep the grid unchanged as the bottom layer and the cutout as the top layer. If visible subject pixels extend outside the grid, expand the canvas only in those directions to the union of the grid and visible subject bounds. Do not crop or reposition either layer.
6. Run `scripts/nine_grid.py verify`. Fix the relevant prior stage if verification fails.
7. Show the 120% PNG and its saved path. Then tell the user: “已完成九宫格突破人物合成：人物以原始抠像为基准放大至120%，并按P=T标准位置对齐，成品已通过校验。如果人物大小或位置还需要调整，可以指定新的比例（如80%、100%、140%），也可以告诉我向左、向右、向上或向下平移到你想要的位置。”

Only generate an adjusted edition when the user asks for it. Treat 120% as the default first edition. For any other positive scale, including 100%, derive the requested scale directly from the original cutout, recompute P, and default to P=T unless the user also requests a position change. For a position variant, keep T fixed and express the requested X/Y translation as an offset from the standard P=T placement. Never derive a resized edition from another resized output.

Read [references/specification.md](references/specification.md) for the exact layout, anchor mathematics, canvas union, and verification invariants. Read [references/edit-prompts.md](references/edit-prompts.md) only if the user explicitly asks Codex to create either missing Photo 1 derivative.

## Default command pattern

```powershell
python scripts/nine_grid.py build-grid --background1 photo1-background.png --photo2 photo2.png --photo3 photo3.png --photo4 photo4.png --photo5 photo5.png --photo6 photo6.png --output grid.png --metadata grid.json
python scripts/nine_grid.py scale-cutout --input photo1-cutout.png --output photo1-cutout-120.png --scale 1.2 --metadata photo1-cutout-120.json
python scripts/nine_grid.py composite --background grid.png --metadata grid.json --cutout photo1-cutout-120.png --output final-120.png --report final-120.json
python scripts/nine_grid.py verify --background grid.png --metadata grid.json --cutout photo1-cutout-120.png --composite final-120.png --report final-120.json
```

## Locked invariants

- The Photo 1 background continuously spans cells 2, 3, 5, and 6; it is not four copies.
- Photos 2–6 occupy cells 1, 4, 7, 8, and 9 respectively.
- Every cell is square, separators are uniformly white, and images use proportional cover-cropping without distortion.
- T is determined only from the grid and never moves. P is determined only from alpha-positive cutout pixels.
- The default cutout is derived once from the original at exactly 120%, then receives one X/Y translation with no further visible-pixel modification.
- Optional variants may change scale or add a user-requested X/Y offset, but must not alter any other visible subject pixels.
- The cutout always covers photos and white grid lines.
- The grid is not a crop boundary. Preserve every visible grid and subject pixel by expanding the final canvas when needed.
