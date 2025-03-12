import os
import sys
import time
import webbrowser
import dash
import dash_daq as daq
import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
from dash_local_react_components import load_react_component

# Import visualization functions (from your separate file)
from visualize import generate_average_plot, generate_plots
# Import layout and utils
from layout import create_layout

def get_color_hex(color_value):
    """
    Given a color value from a ColorPicker, returns a hex string.
    Expects either a dict with a 'hex' key or one with an 'rgb' key.
    """
    if isinstance(color_value, dict):
        if 'hex' in color_value:
            return color_value['hex']
        elif 'rgb' in color_value:
            rgb = color_value['rgb']
            return '#{:02x}{:02x}{:02x}'.format(rgb.get('r', 0), rgb.get('g', 0), rgb.get('b', 0))
    return color_value  # fallback if not a dict

# Determine the base path (works both for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")
data_dir = os.path.abspath(data_dir)

# Global container for mouse data:
mouse_data = {}

def load_raw_data():
    """Load raw merged data for all mice and store in mouse_data."""
    global mouse_data
    mouse_data = {}
    # Detect available mouse folders
    mouse_folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    for mouse in mouse_folders:
        photometry_path = os.path.join(data_dir, mouse, f"{mouse}.csv")
        behavior_path = os.path.join(data_dir, mouse, "Behavior.csv")
        if os.path.exists(photometry_path) and os.path.exists(behavior_path):
            photometry = PhotometryDataset(
                photometry_path,
                column_map={
                    "channel1_410": "ACC.control",
                    "channel1_470": "ACC.signal",
                    "channel2_410": "ADN.control",
                    "channel2_470": "ADN.signal"
                }
            )
            behavior = BehaviorDataset(behavior_path)
            photometry.normalize_signal()
            merged = MergeDatasets(photometry, behavior)
            mouse_data[mouse] = merged
    print(f"Loaded raw data for {len(mouse_data)} mice: {list(mouse_data.keys())}")

# Initial load of raw data
load_raw_data()

app = dash.Dash(__name__, use_pages=True, assets_folder='../assets')

# Load the GroupDropdown React component globally
GroupDropdown = load_react_component(app, "components", "GroupDropdown.js")

app.layout = html.Div([
    # Header image
    html.Div([
        html.Img(src='/assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),
    
    # Mouse selection dropdown (global navigation)
    html.Div([
        dcc.Dropdown(
            id='mouse-dropdown',
            options=(
                [{"label": dcc.Link(children="Averaged Data", href="/average"), "value": "/average"}] +
                [{"label": dcc.Link(children=f"Mouse {mouse}", href=f'/mouse/{mouse}'), "value": f'/mouse/{mouse}'} for mouse in mouse_data]
            ) if mouse_data else [{"label": "No data available", "value": "None"}],
            value="Home" if mouse_data else "None",
            style={'width': '300px', 'margin': '0 auto'}
        )
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),

    # Page container for multi-page routing
    dash.page_container,

    # Footer image
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'}),

    # Store component to persist state
    dcc.Store(id='app-state', storage_type='session')
])

# Example callback for another page element (if needed)
@app.callback(
    Output('page-dropdown', 'value'),
    [Input('page-dropdown', 'value')]
)
def update_page(value):
    return value

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            a {
                color: inherit;
                text-decoration: none;
            }
            .dash-dropdown .Select-menu-outer .VirtualizedSelectSelectedOption > a {
                pointer-events: none;
            }
            .dash-dropdown .Select-menu-outer .VirtualizedSelectOption > a {
                width: 100%;
                height: 100%;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)