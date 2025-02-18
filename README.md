# [MouseMemoryGraph](https://wiki.bme-paris.com/2025-project05/tiki-index.php?page=HomePage)

## Overview
MouseMemoryGraph is a **Dash-based web application** for visualizing and analyzing neural and behavioral data from mouse experiments. The application integrates **photometry data** and **behavioral tracking data** to provide interactive visualizations and interval-based analyses. Click on the title above to check out our website which gives a detailed background on this project and our team.

## Features
- Interactive plots for photometry and behavioral data
- Interval-based epoch extraction for event-aligned visualizations
- Reprocessing functionality to incorporate newly added datasets
- Web-based dashboard for intuitive data exploration

## Dependencies
Ensure the following dependencies are installed before running the application:

```bash
pip install -r requirements.txt
```
To generate the `requirements.txt` file from your current environment, run:

```bash
pip freeze > requirements.txt
```

### Main Libraries Used:
- `dash` for web application interface
- `plotly` for interactive graphing
- `pandas` & `numpy` for data handling and processing
- `scipy` for signal filtering

## Installation & Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/MouseMemoryGraph.git
   cd MouseMemoryGraph
   ```
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python code/app.py
   ```
5. Open your browser and navigate to:
   ```
   http://127.0.0.1:8050/
   ```

## Directory Structure
```
MouseMemoryGraph/
│-- assets/                  # Static files (images, CSS, etc.)
│   ├── header.png           # Header image for the dashboard
│   ├── footer.png           # Footer image for the dashboard
│   ├── style.css            # (Optional) Custom styles
│-- code/                    # Source code
│   ├── app.py               # Main Dash application
│   ├── dataset.py           # Data processing classes
│   ├── dashboard.py         # Dashboard layout and callbacks
│-- data/                    # Data directory (must be manually populated)
│   ├── mouse1/              # Example mouse dataset folder
│   │   ├── cfc_2046.csv      # Photometry data
│   │   ├── behavior.csv      # Behavioral tracking data
│   ├── mouse2/              # Additional dataset
│-- dist/                    # Compiled application (if using PyInstaller)
│-- README.md                # This file
```

## Adding Your Data
1. Place photometry and behavioral data files in the `data/` directory.
2. Organize them into subfolders named after each mouse (e.g., `data/mouse1/`).
3. Ensure file names follow the expected format:
   - **Photometry:** `cfc_2046.csv`
   - **Behavior:** `a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv`
4. Run the application, and it will dynamically detect and load new datasets.

## Acknowledgments
This project includes concepts inspired by:
- [Photometry Data Processing Repository](https://github.com/katemartian/Photometry_data_processing)
- [JOVE Paper: Multi-Fiber Photometry](https://www.jove.com/video/60278/multi-fiber-photometry-to-record-neural-activity-freely-moving)
  
## License
This project is licensed under the MIT License. See `LICENSE` for more details.

## Authors

- [Brynn Harris-Shanks](https://www.linkedin.com/in/brynn-harris-shanks/)
- [Julian Ostermaier](https://www.linkedin.com/in/julian-ostermaier-6821761b3/)
- [Maria Jose Araya](https://www.linkedin.com/in/maria-araya/)
  
