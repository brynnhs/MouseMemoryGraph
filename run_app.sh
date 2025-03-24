#!/bin/bash

# Set the project folder name
PROJECT_FOLDER="MouseMemoryGraph"

# Navigate to the project folder (assuming this script is in the same directory as the project folder)
cd "$(dirname "$0")/$PROJECT_FOLDER" || { echo "Project folder not found."; exit 1; }

# Activate the Conda base environment
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed or not in PATH. Please install Conda first."
    exit 1
fi

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate base

# Navigate to the code folder
cd code || { echo "Code folder not found."; exit 1; }

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "app.py not found in the code folder."
    conda deactivate
    exit 1
fi

# Run the app.py file
python3 app.py

# Deactivate the Conda environment after execution
conda deactivate