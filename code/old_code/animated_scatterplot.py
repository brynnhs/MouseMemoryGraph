# This script creates an animation of the mouse's movement over time. 
# It reads the data from a CSV file, extracts the body parts and coordinates, and creates a scatter plot of the mouse's movement. 
# It then animates the scatter plot to show the mouse's movement over time.
# TODO: Show to Julian and Maria
# Interesting but not super useful for Livia 


# Load Libraries
import pandas as pd
import matplotlib.pyplot as plt
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

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(coords_x.min().min() - 10, coords_x.max().max() + 10)
ax.set_ylim(coords_y.min().min() - 10, coords_y.max().max() + 10)
ax.invert_yaxis()
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")
ax.set_title("Mouse Movement Over Time")

# Create scatter points
scatters = {part: ax.plot([], [], 'o', label=part)[0] for part in body_parts}
ax.legend()

# Animation function
def update(frame):
    for part in body_parts:
        scatters[part].set_data(coords_x[part].iloc[frame], coords_y[part].iloc[frame])
    return scatters.values()

# Create animation
ani = animation.FuncAnimation(fig, update, frames=len(coords_x), interval=50, blit=True)

plt.show()