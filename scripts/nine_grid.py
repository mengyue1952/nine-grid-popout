#!/usr/bin/env python3
"""Deterministic geometry for the nine-grid-popout skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


def load_rgba(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save_json(path: str, value: dict) -> None:
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def cover(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    resized = image.resize(size, Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    box = image.getchannel("A").getbbox()
    if box is None:
        raise ValueError("Cutout contains no nontransparent pixels")
    return box


def lowest_point(image: Image.Image) -> tuple[float, int]:
    alpha = image.getchannel("A")
    box = alpha_bbox(image)
    y = box[3] - 1
    xs = [x for x in range(image.width) if alpha.getpixel((x, y)) > 0]
    if not xs:
        raise ValueError("Unable to locate lowest nontransparent pixels")
    return ((min(xs) + max(xs)) / 2.0, y)


def round_half_away(value: float) -> int:
    return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)


def sha256_pixels(image: Image.Image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_grid(args: argparse.Namespace) -> None:
    paths = [args.background1, args.photo2, args.photo3, args.photo4, args.photo5, args.photo6]
    images = [load_rgba(p) for p in paths]
    cell, gap = args.cell, args.gap
    margin = args.margin if args.margin is not None else gap
    if cell <= 0 or gap < 0 or margin < 0:
        raise ValueError("cell must be positive; gap and margin must be nonnegative")
    side = 2 * margin + 3 * cell + 2 * gap
    canvas = Image.new("RGBA", (side, side), "white")

    def xy(row: int, col: int) -> tuple[int, int]:
        return margin + col * (cell + gap), margin + row * (cell + gap)

    x1, y1 = xy(0, 1)
    region = cover(images[0], 2 * cell + gap, 2 * cell + gap)
    canvas.alpha_composite(region, (x1, y1))
    draw = ImageDraw.Draw(canvas)
    if gap:
        draw.rectangle((x1 + cell, y1, x1 + cell + gap - 1, y1 + 2 * cell + gap - 1), fill="white")
        draw.rectangle((x1, y1 + cell, x1 + 2 * cell + gap - 1, y1 + cell + gap - 1), fill="white")

    placements = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]
    for image, (row, col) in zip(images[1:], placements):
        canvas.alpha_composite(cover(image, cell, cell), xy(row, col))

    canvas.convert("RGB").save(args.output, quality=95)
    target = margin + 2 * cell + gap
    save_json(args.metadata, {
        "version": 1, "cell": cell, "gap": gap, "margin": margin,
        "grid_size": [side, side], "target_T": [target, target],
        "background": str(Path(args.output).resolve()),
    })


def scale_cutout(args: argparse.Namespace) -> None:
    if not args.scale > 0:
        raise ValueError("scale must be greater than 0")
    image = load_rgba(args.input)
    box = alpha_bbox(image)
    cropped = image.crop(box)
    target = (max(1, round(cropped.width * args.scale)), max(1, round(cropped.height * args.scale)))
    resized = cropped.resize(target, Image.Resampling.LANCZOS)
    resized = resized.crop(alpha_bbox(resized))
    resized.save(args.output)
    if args.metadata:
        save_json(args.metadata, {
            "version": 1, "source_alpha_bbox": list(box),
            "source_subject_size": [cropped.width, cropped.height],
            "requested_scale": args.scale, "output_subject_size": list(resized.size),
            "output": str(Path(args.output).resolve()),
        })


def placement(background: Image.Image, cutout: Image.Image, meta: dict, offset_x: int = 0, offset_y: int = 0) -> dict:
    box = alpha_bbox(cutout)
    px, py = lowest_point(cutout)
    tx, ty = meta["target_T"]
    dx = round_half_away(tx - px) + offset_x
    dy = round_half_away(ty - py) + offset_y
    visible_left, visible_top = dx + box[0], dy + box[1]
    visible_right, visible_bottom = dx + box[2], dy + box[3]
    min_x, min_y = min(0, visible_left), min(0, visible_top)
    max_x = max(background.width, visible_right)
    max_y = max(background.height, visible_bottom)
    origin = (-min_x, -min_y)
    return {
        "P_cutout": [px, py], "T_grid": [tx, ty],
        "requested_offset": [offset_x, offset_y],
        "effective_target": [tx + offset_x, ty + offset_y],
        "delta": [dx, dy],
        "cutout_alpha_bbox": list(box),
        "origin_shift": list(origin), "background_position": list(origin),
        "cutout_position": [dx + origin[0], dy + origin[1]],
        "canvas_size": [max_x - min_x, max_y - min_y],
        "P_final": [px + dx + origin[0], py + dy + origin[1]],
        "T_final": [tx + origin[0], ty + origin[1]],
    }


def composite(args: argparse.Namespace) -> None:
    background, cutout = load_rgba(args.background), load_rgba(args.cutout)
    meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    report = placement(background, cutout, meta, args.offset_x, args.offset_y)
    canvas = Image.new("RGBA", tuple(report["canvas_size"]), "white")
    canvas.alpha_composite(background, tuple(report["background_position"]))
    canvas.alpha_composite(cutout, tuple(report["cutout_position"]))
    canvas.save(args.output)
    report.update({
        "version": 1, "background_pixel_sha256": sha256_pixels(background),
        "cutout_pixel_sha256": sha256_pixels(cutout),
        "output": str(Path(args.output).resolve()),
    })
    save_json(args.report, report)


def verify(args: argparse.Namespace) -> None:
    background, cutout = load_rgba(args.background), load_rgba(args.cutout)
    result = load_rgba(args.composite)
    meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    offset = report.get("requested_offset", [0, 0])
    expected = placement(background, cutout, meta, int(offset[0]), int(offset[1]))
    errors = []
    keys = ("requested_offset", "effective_target", "delta", "origin_shift", "background_position", "cutout_position", "canvas_size", "P_final", "T_final")
    for key in keys:
        if report.get(key) != expected[key]:
            errors.append(f"report mismatch: {key}")
    if report.get("background_pixel_sha256") != sha256_pixels(background):
        errors.append("background hash mismatch")
    if report.get("cutout_pixel_sha256") != sha256_pixels(cutout):
        errors.append("cutout hash mismatch")
    if list(result.size) != expected["canvas_size"]:
        errors.append("composite canvas size mismatch")
    rebuilt = Image.new("RGBA", tuple(expected["canvas_size"]), "white")
    rebuilt.alpha_composite(background, tuple(expected["background_position"]))
    rebuilt.alpha_composite(cutout, tuple(expected["cutout_position"]))
    if sha256_pixels(rebuilt) != sha256_pixels(result):
        errors.append("composite pixels differ from deterministic rebuild")
    if errors:
        raise SystemExit("VERIFY FAILED: " + "; ".join(errors))
    print("VERIFY OK: geometry, source hashes, layer order, and composite pixels match")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build-grid")
    for name in ("background1", "photo2", "photo3", "photo4", "photo5", "photo6"):
        b.add_argument(f"--{name}", required=True)
    b.add_argument("--cell", type=int, default=1000)
    b.add_argument("--gap", type=int, default=24)
    b.add_argument("--margin", type=int)
    b.add_argument("--output", required=True)
    b.add_argument("--metadata", required=True)
    b.set_defaults(func=build_grid)
    s = sub.add_parser("scale-cutout")
    s.add_argument("--input", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--scale", type=float, default=1.2)
    s.add_argument("--metadata")
    s.set_defaults(func=scale_cutout)
    c = sub.add_parser("composite")
    c.add_argument("--background", required=True)
    c.add_argument("--metadata", required=True)
    c.add_argument("--cutout", required=True)
    c.add_argument("--output", required=True)
    c.add_argument("--report", required=True)
    c.add_argument("--offset-x", type=int, default=0)
    c.add_argument("--offset-y", type=int, default=0)
    c.set_defaults(func=composite)
    v = sub.add_parser("verify")
    v.add_argument("--background", required=True)
    v.add_argument("--metadata", required=True)
    v.add_argument("--cutout", required=True)
    v.add_argument("--composite", required=True)
    v.add_argument("--report", required=True)
    v.set_defaults(func=verify)
    return p


if __name__ == "__main__":
    namespace = parser().parse_args()
    namespace.func(namespace)
