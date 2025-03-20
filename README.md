# [MouseMemoryGraph](https://wiki.bme-paris.com/2025-project05/tiki-index.php?page=HomePage)

## Overview
MouseMemoryGraph is a **Dash-based web application** for visualizing and analyzing neural and behavioral data from mouse experiments. The application integrates **photometry data** and **behavioral data** to provide interactive visualizations and event-based analyses. Click on the title above to check out our website which gives a detailed background on this project and our team.

## Features
- Interactive plots that combine photometry and behavioural data
- Event-related visualizations of freezing behaviour onset and offset events
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

MOUSEMEMORYGRAPH/
├── code/
│   ├── __pycache__/           # Compiled Python files
│   ├── assets/               # Static assets (images, CSS, etc.)
│   ├── components/           # JS components for the app
│   ├── pages/
│   │   ├── home.py           # Home page
│   │   ├── mouse.py          # Individual mouse pages
│   │   └── average.py        # Averages across and between groups
│   ├── app.py                # Main application entry point
│   ├── assignments.json      # For saving group assignments
│   ├── dataset.py            # Data loading and processing logic
│   ├── utils.py              # Utility functions
│   └── visualize.py          # To produce the visualizations
│-- data/                    # Data directory (must be manually populated)
│   ├── mousename_group/              # Example mouse dataset folder *how you name the files matters
│   │   ├── mousename_recording.csv      # Photometry data *where mousename is the mouse id
│   │   ├── mousename_behavior.csv      # Behavioral classification data from deeplabcut
│   ├── mouse2/              # Additional datasets
├── documentation/            # Documentation files
├── MouseMemoryGraph.spec     # PyInstaller or related spec file
├── README.md                 # Project README
├── requirements.txt          # Python dependencies
├── run_app.bat               # Windows script to run the app
├── run_app.sh                # Unix/Linux script to run the app
└── .gitignore                # Git ignore rules

## Adding Your Data
1. Launch the dashboard
2. Copy the path to your data folder on your computer
3. Paste the path into the input box on the home page of the dashboard
4. Ensure the data folder follows the structure above
5. Click the "Process" button on the home page
6. Navigate to the individual mouse pages or the group analysis
*If you add a new event on the homepage you must click the "Process" button again to include it in analysis

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
  
