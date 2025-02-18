import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.animation as animation

# Load the data
file_path = "/Users/brynnharrisshanks/Documents/GitHub/MouseMemoryGraph/data/a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv"
df = pd.read_csv(file_path)

# Extract body parts and coordinates
body_parts = df.iloc[0, ::3].values
coords_x = df.iloc[2:, 1::3].reset_index(drop=True).astype(float)
coords_y = df.iloc[2:, 2::3].reset_index(drop=True).astype(float)

# Ensure correct column names
num_columns = min(len(body_parts), coords_x.shape[1], coords_y.shape[1])
body_parts = body_parts[:num_columns]
coords_x = coords_x.iloc[:, :num_columns]
coords_y = coords_y.iloc[:, :num_columns]
coords_x.columns = body_parts
coords_y.columns = body_parts

# Select body part for visualization
selected_part = "nose"
x_positions = coords_x[selected_part]
y_positions = coords_y[selected_part]

# Set up figure and axis
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")
ax.set_title(f"Sliding Window Heatmap of {selected_part} Movement")

# Initialize heatmap
bins = 50
window_size = 100  # Number of frames in the sliding window
heatmap_data, xedges, yedges = np.histogram2d([], [], bins=bins)
hm = sns.heatmap(heatmap_data.T, cmap="inferno", cbar=False, ax=ax)

# Update function for animation
def update(frame):
    start = max(0, frame - window_size)
    x_window = x_positions[start:frame]
    y_window = y_positions[start:frame]
    
    # Compute heatmap for current window
    heatmap_data, _, _ = np.histogram2d(x_window, y_window, bins=[xedges, yedges])
    
    # Update heatmap
    hm.set_data(heatmap_data.T)
    return hm,

# Create animation
ani = animation.FuncAnimation(fig, update, frames=len(x_positions), interval=50, blit=False)

plt.show()

