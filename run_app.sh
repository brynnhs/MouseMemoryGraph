#!/bin/bash

# Set the project folder name
PROJECT_FOLDER="MouseMemoryGraph"

# Navigate to the project folder (assuming this script is in the same directory as the project folder)
cd "$(dirname "$0")/$PROJECT_FOLDER" || { echo "Project folder not found."; exit 1; }

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please create it using 'python3 -m venv .venv'."
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Navigate to the code folder
cd code || { echo "Code folder not found."; exit 1; }

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "app.py not found in the code folder."
    deactivate
    exit 1
fi

# Run the app.py file
python3 app.py

# Deactivate the virtual environment after execution
deactivate