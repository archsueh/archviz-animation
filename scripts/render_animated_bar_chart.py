#!/usr/bin/env python3
"""
Animated bar chart renderer for archviz-diagram + archviz-animation crossover.
Generates growing bar chart animation as GIF.
"""
import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Theme from archviz-animation
THEME = {
    "bg": "#000000",
    "white": "#f4f0ee",
    "muted": "#cfc7c5",
    "frame": "#5c6265",
    "green": "#22c86f",
    "cyan": "#7ee3d6",
    "purple": "#bd54d3",
    "amber": "#f4b64e",
    "pink": "#ff7ab6",
}

# Chart colors (from archviz-diagram)
CHART_COLORS = [
    "#002fa7",  # IKB
    "#94a3b8",  # Slate
    "#a8a29e",  # Stone
    "#d6d3d1",  # Pebble
    "#c96442",  # Terracotta
    "#5e5d59",  # Warm Gray
]

SCALE = 2
DEFAULT_W = 800
DEFAULT_H = 500
DEFAULT_FRAMES = 30
DEFAULT_FPS = 15


def hex_rgba(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def c(v):
    return int(round(v * SCALE))


def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, c(size))
        except OSError:
            continue
    return ImageFont.load_default()


def ease_out_cubic(t):
    """Easing function for smooth animation."""
    return 1 - (1 - t) ** 3


def render_frame(data, progress, width, height):
    """Render a single frame of the animated bar chart."""
    img = Image.new("RGBA", (width * SCALE, height * SCALE), hex_rgba(THEME["bg"]))
    draw = ImageDraw.Draw(img)

    # Layout
    margin_left = 80
    margin_right = 40
    margin_top = 60
    margin_bottom = 80
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    # Title
    title = data.get("title", "Chart")
    font_title = load_font(24, bold=True)
    draw.text(
        (c(margin_left), c(20)),
        title,
        font=font_title,
        fill=hex_rgba(THEME["white"]),
    )

    # Subtitle
    subtitle = data.get("subtitle", "")
    if subtitle:
        font_sub = load_font(14)
        draw.text(
            (c(margin_left), c(48)),
            subtitle,
            font=font_sub,
            fill=hex_rgba(THEME["muted"]),
        )

    # Data
    categories = data.get("categories", [])
    values = data.get("values", [])
    labels = data.get("labels", [])

    if not categories or not values:
        return img

    # Calculate bar width
    n_bars = len(categories)
    bar_width = min(60, chart_width / n_bars * 0.7)
    gap = (chart_width - bar_width * n_bars) / (n_bars + 1)

    # Max value for scaling
    max_val = max(values) if values else 1

    # Draw bars with animation
    font_label = load_font(12)
    font_value = load_font(11)

    for i, (cat, val) in enumerate(zip(categories, values)):
        # Animated height (ease out)
        animated_progress = ease_out_cubic(min(progress * 1.2 - i * 0.05, 1.0))
        animated_progress = max(0, animated_progress)

        bar_height = (val / max_val) * chart_height * animated_progress
        x = margin_left + gap + i * (bar_width + gap)
        y = margin_top + chart_height - bar_height

        # Bar color
        color = CHART_COLORS[i % len(CHART_COLORS)]

        # Draw bar
        draw.rectangle(
            [c(x), c(y), c(x + bar_width), c(margin_top + chart_height)],
            fill=hex_rgba(color),
            outline=hex_rgba(THEME["white"], 100),
        )

        # Category label
        label = labels[i] if i < len(labels) else cat
        bbox = draw.textbbox((0, 0), label, font=font_label)
        label_width = bbox[2] - bbox[0]
        draw.text(
            (c(x + bar_width / 2 - label_width / 2 / SCALE), c(margin_top + chart_height + 10)),
            label,
            font=font_label,
            fill=hex_rgba(THEME["white"]),
        )

        # Value label (animated)
        if animated_progress > 0.8:
            value_text = f"{val:.1f}"
            bbox = draw.textbbox((0, 0), value_text, font=font_value)
            value_width = bbox[2] - bbox[0]
            draw.text(
                (c(x + bar_width / 2 - value_width / 2 / SCALE), c(y - 20)),
                value_text,
                font=font_value,
                fill=hex_rgba(THEME["green"]),
            )

    # Y-axis
    draw.line(
        [(c(margin_left), c(margin_top)), (c(margin_left), c(margin_top + chart_height))],
        fill=hex_rgba(THEME["frame"]),
        width=c(1),
    )

    # X-axis
    draw.line(
        [(c(margin_left), c(margin_top + chart_height)), (c(width - margin_right), c(margin_top + chart_height))],
        fill=hex_rgba(THEME["frame"]),
        width=c(1),
    )

    # Y-axis labels
    for i in range(5):
        val = max_val * i / 4
        y = margin_top + chart_height - (val / max_val) * chart_height
        draw.line(
            [(c(margin_left - 5), c(y)), (c(margin_left), c(y))],
            fill=hex_rgba(THEME["frame"]),
            width=c(1),
        )
        label = f"{val:.0f}"
        bbox = draw.textbbox((0, 0), label, font=font_value)
        label_width = bbox[2] - bbox[0]
        draw.text(
            (c(margin_left - 10 - label_width / SCALE), c(y - 6)),
            label,
            font=font_value,
            fill=hex_rgba(THEME["muted"]),
        )

    return img


def render_animated_chart(data, outdir, basename, frames=DEFAULT_FRAMES, fps=DEFAULT_FPS):
    """Render animated bar chart as GIF."""
    width = data.get("width", DEFAULT_W)
    height = data.get("height", DEFAULT_H)

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Generate frames
    images = []
    for i in range(frames):
        progress = i / (frames - 1)
        frame = render_frame(data, progress, width, height)
        images.append(frame)

    # Save GIF
    gif_path = outdir / f"{basename}.gif"
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / fps),
        loop=0,
    )
    print(f"GIF saved: {gif_path}")

    # Save static PNG (last frame)
    png_path = outdir / f"{basename}.png"
    images[-1].save(png_path)
    print(f"PNG saved: {png_path}")

    return gif_path, png_path


def main():
    parser = argparse.ArgumentParser(description="Animated bar chart renderer")
    parser.add_argument("--spec", required=True, help="JSON spec file")
    parser.add_argument("--outdir", default="./output", help="Output directory")
    parser.add_argument("--basename", default="chart", help="Output filename base")
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES, help="Number of frames")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Frames per second")
    args = parser.parse_args()

    # Load spec
    with open(args.spec, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Render
    gif_path, png_path = render_animated_chart(
        data, args.outdir, args.basename, args.frames, args.fps
    )

    print(f"\nDone! Generated:")
    print(f"  - {gif_path}")
    print(f"  - {png_path}")


if __name__ == "__main__":
    main()
