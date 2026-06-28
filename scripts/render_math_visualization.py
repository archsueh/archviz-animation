#!/usr/bin/env python3
"""
Math Visualization Animation Renderer.
Style: 3Blue1Brown / THEMATHFLOW inspired math education visualization.
Features:
- Clean geometric shapes
- Low-saturation color palette
- 3D perspective composition
- Real-time synchronized animations
- Mathematical notation support
"""
import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Theme inspired by math education videos
MATH_THEME = {
    "bg": "#f5f0eb",  # Warm off-white
    "grid": "#e0dbd5",  # Light grid
    "text": "#2c2c2c",  # Dark gray text
    "accent1": "#e8734a",  # Warm orange (unit circle)
    "accent2": "#d4567a",  # Rose/pink (sin)
    "accent3": "#4a9e8e",  # Teal/blue-green (cos)
    "accent4": "#6b7b8d",  # Slate blue (secondary)
    "highlight": "#f0c040",  # Yellow highlight
}

SCALE = 2
DEFAULT_W = 1200
DEFAULT_H = 800
DEFAULT_FPS = 30
DEFAULT_FRAMES = 60


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


def draw_grid(draw, width, height, spacing=50, color=None):
    """Draw background grid."""
    theme = MATH_THEME
    color = color or theme["grid"]
    
    for x in range(0, width, spacing):
        draw.line([(c(x), 0), (c(x), c(height))], fill=hex_rgba(color), width=c(1))
    for y in range(0, height, spacing):
        draw.line([(0, c(y)), (c(width), c(y))], fill=hex_rgba(color), width=c(1))


def draw_unit_circle(draw, cx, cy, radius, angle, theme):
    """Draw unit circle with angle indicator."""
    # Circle outline
    draw.ellipse(
        [c(cx - radius), c(cy - radius), c(cx + radius), c(cy + radius)],
        outline=hex_rgba(theme["accent1"]),
        width=c(2),
    )
    
    # Angle arc
    arc_points = []
    for i in range(int(angle * 10) + 1):
        a = i / 10
        x = cx + radius * 0.3 * math.cos(a)
        y = cy - radius * 0.3 * math.sin(a)
        arc_points.append((c(x), c(y)))
    
    if len(arc_points) > 1:
        draw.line(arc_points, fill=hex_rgba(theme["highlight"]), width=c(2))
    
    # Point on circle
    px = cx + radius * math.cos(angle)
    py = cy - radius * math.sin(angle)
    draw.ellipse(
        [c(px - 8), c(py - 8), c(px + 8), c(py + 8)],
        fill=hex_rgba(theme["accent1"]),
        outline=hex_rgba(theme["text"]),
    )
    
    # Radius line
    draw.line([(c(cx), c(cy)), (c(px), c(py))], fill=hex_rgba(theme["text"]), width=c(2))
    
    return px, py


def draw_sin_curve(draw, start_x, y_center, width, height, angle, theme):
    """Draw sin(x) curve up to given angle."""
    points = []
    for i in range(int(angle * 100) + 1):
        a = i / 100
        x = start_x + (a / (2 * math.pi)) * width
        y = y_center - math.sin(a) * height * 0.4
        points.append((c(x), c(y)))
    
    if len(points) > 1:
        draw.line(points, fill=hex_rgba(theme["accent2"]), width=c(3))
    
    # Current value indicator
    if angle > 0:
        current_x = start_x + (angle / (2 * math.pi)) * width
        current_y = y_center - math.sin(angle) * height * 0.4
        draw.ellipse(
            [c(current_x - 6), c(current_y - 6), c(current_x + 6), c(current_y + 6)],
            fill=hex_rgba(theme["accent2"]),
        )


def draw_cos_curve(draw, start_x, y_center, width, height, angle, theme):
    """Draw cos(x) curve up to given angle."""
    points = []
    for i in range(int(angle * 100) + 1):
        a = i / 100
        x = start_x + (a / (2 * math.pi)) * width
        y = y_center - math.cos(a) * height * 0.4
        points.append((c(x), c(y)))
    
    if len(points) > 1:
        draw.line(points, fill=hex_rgba(theme["accent3"]), width=c(3))
    
    # Current value indicator
    if angle > 0:
        current_x = start_x + (angle / (2 * math.pi)) * width
        current_y = y_center - math.cos(angle) * height * 0.4
        draw.ellipse(
            [c(current_x - 6), c(current_y - 6), c(current_x + 6), c(current_y + 6)],
            fill=hex_rgba(theme["accent3"]),
        )


def draw_projection_lines(draw, px, py, sin_x, sin_y, cos_x, cos_y, theme):
    """Draw projection lines from unit circle to curves."""
    # To sin curve (dashed effect by drawing segments)
    for i in range(0, 100, 8):
        t1 = i / 100
        t2 = min((i + 4) / 100, 1.0)
        x1 = px + (sin_x - px) * t1
        y1 = py + (sin_y - py) * t1
        x2 = px + (sin_x - px) * t2
        y2 = py + (sin_y - py) * t2
        draw.line(
            [(c(x1), c(y1)), (c(x2), c(y2))],
            fill=hex_rgba(theme["accent2"], 100),
            width=c(1),
        )
    
    # To cos curve (dashed effect)
    for i in range(0, 100, 8):
        t1 = i / 100
        t2 = min((i + 4) / 100, 1.0)
        x1 = px + (cos_x - px) * t1
        y1 = py + (cos_y - py) * t1
        x2 = px + (cos_x - px) * t2
        y2 = py + (cos_y - py) * t2
        draw.line(
            [(c(x1), c(y1)), (c(x2), c(y2))],
            fill=hex_rgba(theme["accent3"], 100),
            width=c(1),
        )


def render_frame(data, progress, width, height):
    """Render a single frame of math visualization."""
    theme = MATH_THEME
    
    img = Image.new("RGBA", (width * SCALE, height * SCALE), hex_rgba(theme["bg"]))
    draw = ImageDraw.Draw(img)
    
    # Draw grid
    draw_grid(draw, width, height)
    
    # Title
    title = data.get("title", "Unit Circle & Trigonometric Functions")
    font_title = load_font(28, bold=True)
    draw.text((c(40), c(30)), title, font=font_title, fill=hex_rgba(theme["text"]))
    
    # Subtitle
    subtitle = data.get("subtitle", "sin(x) and cos(x) visualization")
    font_sub = load_font(16)
    draw.text((c(40), c(65)), subtitle, font=font_sub, fill=hex_rgba(theme["accent4"]))
    
    # Animation angle (0 to 2π)
    angle = progress * 2 * math.pi
    
    # Unit circle position
    circle_cx = 200
    circle_cy = 350
    circle_radius = 120
    
    # Draw unit circle
    px, py = draw_unit_circle(draw, circle_cx, circle_cy, circle_radius, angle, theme)
    
    # Sin curve area
    sin_start_x = 400
    sin_y = 250
    sin_width = 700
    sin_height = 200
    
    # Draw sin curve
    draw_sin_curve(draw, sin_start_x, sin_y, sin_width, sin_height, angle, theme)
    
    # Cos curve area
    cos_start_x = 400
    cos_y = 550
    cos_width = 700
    cos_height = 200
    
    # Draw cos curve
    draw_cos_curve(draw, cos_start_x, cos_y, cos_width, cos_height, angle, theme)
    
    # Current values
    sin_val = math.sin(angle)
    cos_val = math.cos(angle)
    
    # Projection lines
    sin_current_x = sin_start_x + (angle / (2 * math.pi)) * sin_width
    sin_current_y = sin_y - sin_val * sin_height * 0.4
    cos_current_x = cos_start_x + (angle / (2 * math.pi)) * cos_width
    cos_current_y = cos_y - cos_val * cos_height * 0.4
    
    draw_projection_lines(draw, px, py, sin_current_x, sin_current_y, 
                         cos_current_x, cos_current_y, theme)
    
    # Labels
    font_label = load_font(14)
    font_value = load_font(12)
    
    # Sin label
    draw.text((c(420), c(180)), "sin(x)", font=font_label, fill=hex_rgba(theme["accent2"]))
    draw.text((c(420), c(200)), f"= {sin_val:.3f}", font=font_value, fill=hex_rgba(theme["accent2"]))
    
    # Cos label
    draw.text((c(420), c(480)), "cos(x)", font=font_label, fill=hex_rgba(theme["accent3"]))
    draw.text((c(420), c(500)), f"= {cos_val:.3f}", font=font_value, fill=hex_rgba(theme["accent3"]))
    
    # Angle label
    angle_deg = math.degrees(angle)
    draw.text((c(220), c(420)), f"θ = {angle_deg:.1f}°", font=font_label, fill=hex_rgba(theme["highlight"]))
    
    # Signature
    font_sig = load_font(10)
    draw.text((c(width - 150), c(height - 40)), "@archsueh", font=font_sig, fill=hex_rgba(theme["accent4"]))
    
    return img


def render_math_animation(data, outdir, basename, frames=DEFAULT_FRAMES, fps=DEFAULT_FPS):
    """Render math visualization animation."""
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
    
    # Save MP4 (using ffmpeg)
    mp4_path = outdir / f"{basename}.mp4"
    
    # Save frames as temp images
    temp_dir = outdir / "temp_frames"
    temp_dir.mkdir(exist_ok=True)
    
    for i, img in enumerate(images):
        img.save(temp_dir / f"frame_{i:04d}.png")
    
    # Convert to MP4
    import subprocess
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(temp_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(mp4_path)
    ], capture_output=True)
    
    # Cleanup temp frames
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"MP4 saved: {mp4_path}")
    
    # Save static PNG
    png_path = outdir / f"{basename}.png"
    images[-1].save(png_path)
    print(f"PNG saved: {png_path}")
    
    return gif_path, mp4_path, png_path


def main():
    parser = argparse.ArgumentParser(description="Math visualization animation renderer")
    parser.add_argument("--spec", required=True, help="JSON spec file")
    parser.add_argument("--outdir", default="./output", help="Output directory")
    parser.add_argument("--basename", default="math-viz", help="Output filename base")
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES, help="Number of frames")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Frames per second")
    args = parser.parse_args()
    
    # Load spec
    with open(args.spec, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Render
    gif_path, mp4_path, png_path = render_math_animation(
        data, args.outdir, args.basename, args.frames, args.fps
    )
    
    print(f"\nDone! Generated:")
    print(f"  - {gif_path}")
    print(f"  - {mp4_path}")
    print(f"  - {png_path}")


if __name__ == "__main__":
    main()
