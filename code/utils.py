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