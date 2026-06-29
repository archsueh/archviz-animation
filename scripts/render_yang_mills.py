#!/usr/bin/env python3
"""
Yang-Mills Gauge Field Visualization
Replicates the physics visualization style:
- Glowing gauge field surfaces on dark background
- Color wheel for internal SU(2) directions
- Moving Wilson loops measuring curvature
- Equation overlay: F = dA + A∧A

Dependencies: numpy, matplotlib, scipy
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import hsv_to_rgb
from scipy.ndimage import gaussian_filter
import argparse
import sys

# ── Configuration ─────────────────────────────────────────
RES = 200                # grid resolution
FIELD_SCALE = 6.0        # spatial extent
GAUGE_STRENGTH = 1.8     # gauge field amplitude
SELF_COUPLING = 0.6      # A∧A self-interaction strength
WILSON_SIZE = 1.2        # Wilson loop size
GLOW_SIGMA = 1.5         # glow blur radius
N_FRAMES = 180           # total frames
FPS = 30

# ── Color palette: Green/teal glow on black ──────────────
BG_COLOR = '#050a08'
GLOW_COLORMAP = 'viridis'  # green-teal-yellow glow
FIELD_COLORMAP = 'twilight'  # for direction visualization


def gauge_field(x, y, t):
    """
    SU(2)-inspired gauge field on 2D plane.
    Returns 3 components (like SU(2) generators) at each point.
    """
    # Rotating vortex-like configuration
    r = np.sqrt(x**2 + y**2) + 0.1
    theta = np.arctan2(y, x)
    
    # Time-dependent rotation
    omega = 0.3
    phase = omega * t
    
    # Multi-vortex configuration
    A1 = GAUGE_STRENGTH * np.sin(r * 1.5 + theta + phase) / (r * 0.5 + 1)
    A2 = GAUGE_STRENGTH * np.cos(r * 1.3 - theta * 2 + phase * 0.7) / (r * 0.6 + 1)
    A3 = GAUGE_STRENGTH * np.sin(r * 0.8 + theta * 2.5 + phase * 1.3) * np.exp(-r * 0.15)
    
    # Add self-interaction term (non-abelian)
    A1 += SELF_COUPLING * np.sin(x * 0.8 + y * 1.2 + t * 0.4) * np.exp(-r * 0.2)
    A2 += SELF_COUPLING * np.cos(x * 1.1 - y * 0.7 + t * 0.35) * np.exp(-r * 0.2)
    
    return np.stack([A1, A2, A3], axis=-1)


def compute_curvature(A, dx):
    """
    Compute field strength F = dA + A∧A
    Simplified 2D version: F_xy = ∂_x A_y - ∂_y A_x + [A_x, A_y]
    """
    # Partial derivatives
    dAx_dy = np.gradient(A[..., 0], dx, axis=0)
    dAy_dx = np.gradient(A[..., 1], dx, axis=1)
    
    # Abelian part: ∂_x A_y - ∂_y A_x
    F_abelian = dAy_dx - dAx_dy
    
    # Non-abelian part: A_x × A_y (cross product of SU(2) components)
    A_cross = np.cross(A[..., :2], A[..., 1:3])
    F_nonabelian = A_cross[..., 0]  # z-component of cross product
    
    # Total curvature magnitude
    F = np.sqrt(F_abelian**2 + F_nonabelian**2 + 1e-8)
    
    return F, F_abelian, F_nonabelian


def wilson_loop_measure(A, cx, cy, size, dx):
    """
    Measure gauge holonomy around a Wilson loop.
    Returns the accumulated phase change (simplified).
    """
    half = size / 2
    n = 20  # points per side
    
    # Top edge: left to right
    xs = np.linspace(cx - half, cx + half, n)
    ys = np.full(n, cy - half)
    # Bottom edge: right to left
    xs_b = np.linspace(cx + half, cx - half, n)
    ys_b = np.full(n, cy + half)
    # Left edge: bottom to top
    yl = np.linspace(cy - half, cy + half, n)
    xl = np.full(n, cx - half)
    # Right edge: top to bottom
    yr = np.linspace(cy + half, cy - half, n)
    xr = np.full(n, cx + half)
    
    # Combine path
    x_path = np.concatenate([xs, xr, xs_b[::-1], xl[::-1]])
    y_path = np.concatenate([ys, yr, ys_b[::-1], yl[::-1]])
    
    # Sample gauge field along path (interpolate from grid)
    ix = np.clip(((x_path + FIELD_SCALE) / (2 * FIELD_SCALE) * RES).astype(int), 0, RES - 1)
    iy = np.clip(((y_path + FIELD_SCALE) / (2 * FIELD_SCALE) * RES).astype(int), 0, RES - 1)
    
    # Accumulate holonomy (simplified)
    phases = A[iy, ix, 0]
    # Simple discrete integral
    holonomy = np.sum(phases) / len(phases)
    
    return abs(holonomy)


def create_animation(outpath, frames=N_FRAMES, fps=FPS):
    """Generate Yang-Mills gauge field animation."""
    x = np.linspace(-FIELD_SCALE, FIELD_SCALE, RES)
    y = np.linspace(-FIELD_SCALE, FIELD_SCALE, RES)
    X, Y = np.meshgrid(x, y)
    dx = 2 * FIELD_SCALE / RES
    
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(-FIELD_SCALE, FIELD_SCALE)
    ax.set_ylim(-FIELD_SCALE, FIELD_SCALE)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.subplots_adjust(0, 0, 1, 1)
    
    # Initial frame to set up artists
    A0 = gauge_field(X, Y, 0)
    F0, _, _ = compute_curvature(A0, dx)
    
    # Glow field (gaussian blurred curvature)
    F_glow = gaussian_filter(F0, sigma=GLOW_SIGMA)
    
    im = ax.imshow(
        F_glow,
        extent=[-FIELD_SCALE, FIELD_SCALE, -FIELD_SCALE, FIELD_SCALE],
        origin='lower',
        cmap=GLOW_COLORMAP,
        alpha=0.85,
        vmin=0,
        vmax=3.0,
        interpolation='bilinear'
    )
    
    # Direction overlay (lighter, translucent)
    direction_rgb = np.zeros((RES, RES, 3))
    for i in range(3):
        direction_rgb[..., i] = (A0[..., i] - A0[..., i].min()) / (A0[..., i].max() - A0[..., i].min() + 0.01)
    
    im_dir = ax.imshow(
        direction_rgb,
        extent=[-FIELD_SCALE, FIELD_SCALE, -FIELD_SCALE, FIELD_SCALE],
        origin='lower',
        alpha=0.25,
        interpolation='bilinear'
    )
    
    # Wilson loops - multiple loops at different positions
    n_loops = 5
    loop_colors = ['#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#ff922b']
    loops = []
    for i in range(n_loops):
        angle = 2 * np.pi * i / n_loops
        r = 3.5 + 0.5 * np.sin(i * 1.7)
        cx = r * np.cos(angle + 0.3 * i)
        cy = r * np.sin(angle + 1.1 * i)
        rect = plt.Rectangle(
            (cx - WILSON_SIZE / 2, cy - WILSON_SIZE / 2),
            WILSON_SIZE, WILSON_SIZE,
            fill=False, edgecolor=loop_colors[i], linewidth=1.5, alpha=0.7
        )
        ax.add_patch(rect)
        loops.append({'rect': rect, 'cx': cx, 'cy': cy,
                      'color': loop_colors[i], 'phase': i * 1.3})
    
    # Equation text
    eq_text = ax.text(
        0.02, 0.98,
        r'$\mathbf{F}_{\mu\nu} = \partial_\mu\mathbf{A}_\nu - \partial_\nu\mathbf{A}_\mu + [\mathbf{A}_\mu,\mathbf{A}_\nu]$',
        transform=ax.transAxes,
        color='white', fontsize=11, fontfamily='monospace',
        verticalalignment='top', alpha=0.7,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.3)
    )
    
    # Title
    title = ax.text(
        0.02, 0.05,
        'Yang-Mills Gauge Field',
        transform=ax.transAxes,
        color='white', fontsize=10, fontfamily='monospace',
        verticalalignment='bottom', alpha=0.4
    )
    
    def animate(frame):
        t = frame / fps * 1.5  # slow time
        
        A = gauge_field(X, Y, t)
        F, Fab, Fna = compute_curvature(A, dx)
        F_glow = gaussian_filter(F, sigma=GLOW_SIGMA)
        
        # Update field intensity
        im.set_array(F_glow)
        
        # Update direction colors
        for i in range(3):
            direction_rgb[..., i] = np.clip(
                (A[..., i] - A[..., i].min()) / (A[..., i].max() - A[..., i].min() + 0.01),
                0, 1
            )
        im_dir.set_array(direction_rgb)
        
        # Update Wilson loops (rotate around center)
        for i, loop in enumerate(loops):
            angle_offset = frame * 0.015 + loop['phase']
            r = np.sqrt(loop['cx']**2 + loop['cy']**2)
            base_angle = np.arctan2(loop['cy'], loop['cx']) + angle_offset
            
            # Perturb radius slightly
            r_mod = r + 0.3 * np.sin(frame * 0.04 + i * 1.5)
            
            cx = r_mod * np.cos(base_angle)
            cy = r_mod * np.sin(base_angle)
            
            loop['rect'].set_xy((cx - WILSON_SIZE / 2, cy - WILSON_SIZE / 2))
            
            # Measure curvature at loop position → adjust opacity
            hol = wilson_loop_measure(A, cx, cy, WILSON_SIZE, dx)
            alpha = 0.3 + 0.7 * np.clip(hol / 5.0, 0, 1)
            loop['rect'].set_alpha(alpha)
        
        return [im, im_dir, eq_text, title] + [l['rect'] for l in loops]
    
    ani = animation.FuncAnimation(
        fig, animate, frames=frames,
        interval=1000 / fps, blit=True,
        repeat=True
    )
    
    # Save
    print(f"Rendering {frames} frames @ {fps}fps...")
    ani.save(outpath, writer='ffmpeg', fps=fps, dpi=120,
             savefig_kwargs={'facecolor': BG_COLOR})
    print(f"Saved: {outpath}")
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Yang-Mills gauge field visualization')
    parser.add_argument('--out', default='yang-mills.mp4', help='Output file')
    parser.add_argument('--frames', type=int, default=N_FRAMES)
    parser.add_argument('--fps', type=int, default=FPS)
    parser.add_argument('--dpi', type=int, default=120)
    parser.add_argument('--strength', type=float, default=GAUGE_STRENGTH)
    parser.add_argument('--coupling', type=float, default=SELF_COUPLING)
    args = parser.parse_args()
    
    global GAUGE_STRENGTH, SELF_COUPLING
    GAUGE_STRENGTH = args.strength
    SELF_COUPLING = args.coupling
    
    create_animation(args.out, args.frames, args.fps)


if __name__ == '__main__':
    main()
