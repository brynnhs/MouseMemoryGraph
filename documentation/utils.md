# Utils Module Documentation

## 1. Overview

The `utils.py` module provides utility functions for managing and persisting assignment data. It enables reading and writing JSON files to store assignments, making it easier to handle persistent data storage in the application.

---

## 2. Dependencies and Imports

The module relies on built-in Python libraries:

- **json:** Used for serializing and deserializing assignment data to/from JSON format.
- **os:** Used for file path operations and checking file existence.

---

## 3. Constants

### ASSIGNMENTS_FILE

A constant that defines the absolute path to the `assignments.json` file, which is used to store assignment data.

```python
import os

ASSIGNMENTS_FILE = os.path.join(os.path.dirname(__file__), "assignments.json")
```

**Purpose:**
- Ensures that the file is always stored relative to the script’s location.
- Provides a central reference point for assignment data storage.

---

## 4. Functions

### 4.1 `load_assignments`

```python
def load_assignments():
    """Load assignments from file if it exists, otherwise return an empty dictionary."""
```

**Purpose:**
- Loads assignment data from `assignments.json` if it exists.
- Returns an empty dictionary if the file is missing.

**Behavior:**
- Checks for file existence using `os.path.exists`.
- Opens and reads the JSON file if present.
- Returns a dictionary containing assignments.

**Return Value:**
- A dictionary containing assignment data or an empty dictionary if no file exists.

### 4.2 `save_assignments`

```python
def save_assignments(assignments):
    """Save the assignments dictionary to the JSON file."""
```

**Purpose:**
- Saves assignment data into `assignments.json` in JSON format.

**Behavior:**
- Opens `assignments.json` in write mode.
- Converts the dictionary into a JSON string and writes it to the file.

**Parameters:**
- `assignments` (dict): A dictionary containing assignment data to be saved.

---

## 5. Usage Example

### Loading and Saving Assignments

```python
import utils

# Load current assignments
assignments = utils.load_assignments()

# Modify assignments
assignments['task1'] = 'Complete project documentation.'

# Save updated assignments
utils.save_assignments(assignments)
```

**Expected Behavior:**
- If `assignments.json` exists, its contents will be loaded into `assignments`.
- The user modifies the dictionary by adding or changing tasks.
- `save_assignments` writes the updated dictionary back to `assignments.json`.

---

## 6. Extensibility

The module is designed to be easily extendable:

- Additional validation mechanisms can be added to ensure JSON integrity.
- Error handling can be improved to manage file I/O exceptions.
- More utility functions can be introduced to support searching, filtering, or structuring assignment data more effectively.

By using this module, assignment data management becomes straightforward and persistent across program runs.