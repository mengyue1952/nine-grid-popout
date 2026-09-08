# Exact composition specification

Number cells row-major from 1 to 9:

```text
1 | 2 | 3
4 | 5 | 6
7 | 8 | 9
```

## Background grid

All nine base cells have one integer side length `C`. Every separator has width `G`, and the outer white margin has width `M` (default `M=G`). The square grid canvas side is `2M + 3C + 2G`.

Photo placement:

```text
Photo 2 | Photo 1 background | Photo 1 background
Photo 3 | Photo 1 background | Photo 1 background
Photo 4 | Photo 5            | Photo 6
```

Photo 1 background is cover-cropped once to the continuous square region of side `2C+G`; one vertical and one horizontal white separator of width `G` are then drawn over it. Photos 2–6 are independently cover-cropped into their cells without distortion or generation.

## Default 120% cutout and optional scale variants

For the first output, derive a 120% edition directly from the uploaded original cutout. Let the original alpha bounding box width and height be `W,H`; resize a tight alpha-bounded copy to `round(1.2W), round(1.2H)` using one high-quality RGBA resampling operation. Recompute P after scaling. Transparent padding does not define the visible subject extent and must not cause final-canvas expansion.

If the user requests another scale factor `s` such as `0.8`, `1.0`, or `1.4`, resize a tight alpha-bounded copy directly from the original to `round(sW), round(sH)` using one high-quality RGBA resampling operation. Recompute P after scaling. Never derive a variant from another resized file.

## Anchor and placement

Let `S` be all cutout pixels with alpha `> 0`. Let `ymax` be the largest y in `S`. Let the x values at `ymax` range from `xmin` to `xmax`. Define:

```text
P.x = (xmin + xmax) / 2
P.y = ymax
```

Half-pixel P.x values are valid. Placement on a raster canvas uses the uniquely documented integer translation produced by round-half-away-from-zero. The same rounded translation must be used by composition and verification.

Cell 5 occupies the second row and second column. Its lower-right vertex is:

```text
T.x = M + 2C + G
T.y = M + 2C + G
```

Compute once:

```text
deltaX = T.x - P.x
deltaY = T.y - P.y
```

Translate the entire cutout by the rounded delta and place it above every photo and separator. Compute the final canvas from the union of the complete grid rectangle and the translated alpha-positive subject bounds, ignoring transparent padding. If visible subject content exceeds any grid edge, expand the canvas in that direction and shift both layers by the same origin offset. Preserve P=T in the expanded coordinate system and never crop visible source pixels.

For a user-requested position variant, preserve the locked T and add explicit offsets `offsetX, offsetY` after computing the standard delta. The effective subject anchor becomes `P = T + (offsetX, offsetY)`. Record those offsets in the report and verify them deterministically. Do not apply unrequested aesthetic nudges.
