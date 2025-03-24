import json
import os

# Define a file to store assignments
ASSIGNMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assignments.json')

def load_assignments():
    """Load assignments from file if it exists, otherwise return an empty dict."""
    if os.path.exists(ASSIGNMENTS_FILE):
        with open(ASSIGNMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_assignments(assignments):
    """Save the assignments dict to file."""
    with open(ASSIGNMENTS_FILE, 'w') as f:
        json.dump(assignments, f)

def hex_to_rgba(hex_color, opacity):
    """
    Convert a hex color to an RGBA string with the specified opacity.
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r}, {g}, {b}, {opacity})'