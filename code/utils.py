# 1. Overview: This module provides utility functions for managing and persisting assignment data.
# 2. Dependencies and Imports
import json
import os

# 3. Constants: Define ASSIGNMENTS_FILE for persistent assignment storage.
# Define a file to store assignments
ASSIGNMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assignments.json')

# 4.1 Functions - load_assignments: Load assignments from file if it exists, otherwise return an empty dictionary.
def load_assignments():
    """Load assignments from file if it exists, otherwise return an empty dict."""
    if os.path.exists(ASSIGNMENTS_FILE):
        with open(ASSIGNMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

# 4.2 Functions - save_assignments: Save the assignments dictionary to file.
def save_assignments(assignments):
    """Save the assignments dict to file."""
    with open(ASSIGNMENTS_FILE, 'w') as f:
        json.dump(assignments, f)