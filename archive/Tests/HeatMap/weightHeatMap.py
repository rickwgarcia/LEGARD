# Let's modify the code to calculate and plot the average point as well

import matplotlib.pyplot as plt
import numpy as np

# Read the coordinates from the file we previously created
file_path = "/home/rickg/LEGARD/archive/Tests/HeatMap/coordinates.txt"
with open(file_path, "r") as file:
    lines = file.readlines()

# Parse the coordinates into a list of tuples
coordinates = [tuple(map(int, line.strip().split("\t"))) for line in lines]

# Convert the coordinates into a 2D histogram for the heatmap
x_coords, y_coords = zip(*coordinates)
heatmap, x_edges, y_edges = np.histogram2d(x_coords, y_coords, bins=(101, 101), range=[[-50, 50], [-50, 50]])

# Calculate the average point
average_x = np.mean(x_coords)
average_y = np.mean(y_coords)

# Plot the color-coded heatmap on a Cartesian plane
plt.figure(figsize=(8, 6))
plt.imshow(heatmap.T, origin='lower', cmap='viridis', interpolation='nearest', extent=[-50, 50, -50, 50])
plt.colorbar(label='Frequency')
plt.title('Cartesian Heat Map of Random Coordinates with Average Point')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(color='white', linestyle='--', linewidth=0.5)

# Plot the average point as a special marker
plt.scatter(average_x, average_y, color='red', s=100, marker='o', label='Average Point')
plt.legend()

plt.show()
