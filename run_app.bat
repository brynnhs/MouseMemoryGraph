:: filepath: /Users/julian/Documents/daten/STUDIUM Master/FabLab 2025/Codebase/MouseMemoryGraph/run_app.bat
@echo off

:: Set the project folder name
set PROJECT_FOLDER=MouseMemoryGraph

:: Locate the project folder (assuming this script is in the same directory as the project folder)
cd /d "%~dp0%PROJECT_FOLDER%"

:: Check if the virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Please create it using "python -m venv .venv".
    exit /b 1
)

:: Activate the virtual environment
call .venv\Scripts\activate

:: Navigate to the code folder
cd code

:: Check if app.py exists
if not exist "app.py" (
    echo app.py not found in the code folder.
    exit /b 1
)

:: Run the app.py file
python app.py

:: Deactivate the virtual environment after execution
deactivate

::
::Steps to Use:
::Save this script as run_app.bat in the MouseMemoryGraph folder.
::Ensure the virtual environment is created in the MouseMemoryGraph folder using:
::python -m venv .venv
::Activate the virtual environment and install the dependencies from requirements.txt:
::activate
::.venv\Scripts\activate
::pip install -r requirements.txt
::deactivate
::Double-click the run_app.bat file on a Windows machine to execute the script.
::This script assumes:

::The virtual environment is named .venv and located in the MouseMemoryGraph folder.
::The app.py file is located in the code folder.
