#!/usr/bin/env python3
"""
Display /home/rickg/LEGARD/Tests/HeatMap/coordinates.txt as a heat map
and refresh the picture every 0.5 s.
"""
import os, numpy as np, matplotlib.pyplot as plt, matplotlib.animation as anim

FILE = "/home/rickg/LEGARD/Tests/HeatMap/coordinates.txt"
BINS = (101, 101)          # matches your –50 … 50 grid
RANGE = [[-50, 50], [-50, 50]]

fig, ax = plt.subplots(figsize=(8, 6))
im  = ax.imshow(np.zeros(BINS).T, origin='lower', extent=[-50, 50, -50, 50],
                cmap='viridis', interpolation='nearest')
sc  = ax.scatter([], [], c='red', s=100, marker='o', label='Average')
plt.colorbar(im, ax=ax, label='Frequency')
ax.set_title('Cartesian Heat Map of Random Coordinates (live)')
ax.set_xlabel('X-axis'); ax.set_ylabel('Y-axis')
ax.grid(color='white', linestyle='--', linewidth=0.5); ax.legend()

def update(_frame):
    """Read the whole file (cheap: ≤ ~100 k lines/s) and redraw."""
    if not os.path.exists(FILE):
        return im, sc                      # nothing yet
    with open(FILE) as f:
        coords = [tuple(map(float, ln.split(', '))) for ln in f if ln.strip()]
    if not coords:                         # file empty
        return im, sc
    x, y      = zip(*coords)               # unpack
    heat, *__) = np.histogram2d(x, y, bins=BINS, range=RANGE)
    im.set_data(heat.T)                    # refresh colours
    sc.set_offsets([[np.mean(x), np.mean(y)]])
    return im, sc

anim.FuncAnimation(fig, update, interval=500, blit=False)   # 0.5 s cadence
plt.show()

