import os
import sys
import dash
import dash_daq as daq
import numpy as np
import pandas as pd
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
from dash_local_react_components import load_react_component

# Import visualization functions
from visualize import generate_average_plot, generate_plots
# Import utility for condition assignments mapping (e.g., {'mouse1': 1, 'mouse2': 3, ...})
from utils import load_assignments

dash.register_page(__name__, path='/average')
app = dash.get_app()

# Determine the base path
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../../data")
data_dir = os.path.abspath(data_dir)

# Global container for mouse data:
mouse_data = {}

def load_raw_data():
    """Load raw merged data for all mice and store in mouse_data."""
    global mouse_data
    mouse_data = {}
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

# Load condition assignments mapping: mouse id -> condition group
condition_assignments = load_assignments()

# Load the GroupSelection component
GroupSelection = load_react_component(app, "components", "GroupSelection.js")

layout = html.Div([
    # Include the group selection dropdown (MultiSelect)
    html.Div([
        GroupSelection(id='group-selection', value=[])  # Initially, no groups selected
    ], style={'width': '100%', 'text-align': 'left', 'margin-bottom': '20px'}),
    
    # Numeric inputs for the epoch window
    html.Div([
        html.Label("Seconds Before Event:"),
        dcc.Input(
            id="seconds-before",
            type="number",
            placeholder="Enter seconds before (e.g. 2)",
            value=2,
            style={'margin-left': '10px', 'margin-right': '20px'}
        ),
        html.Label("Seconds After Event:"),
        dcc.Input(
            id="seconds-after",
            type="number",
            placeholder="Enter seconds after (e.g. 2)",
            value=2,
            style={'margin-left': '10px'}
        )
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    
    html.Div(id='tab-content'),
])

@callback(
    Output('tab-content', 'children'),
    [Input('seconds-before', 'value'),
     Input('seconds-after', 'value'),
     Input('group-selection', 'value')]
)
def update_graph(seconds_before, seconds_after, selected_groups):
    print(selected_groups)
    # Default to all groups if none selected.
    if not selected_groups:
        selected_groups = []

    # Reload condition assignments mapping: mouse id -> group
    assignments = load_assignments()

    # Initialize dictionaries for each sensor and epoch type.
    acc_on_dict = {}
    acc_off_dict = {}
    adn_on_dict = {}
    adn_off_dict = {}
    fps = None

    # Process each mouse if its condition is selected.
    for mouse, merged in mouse_data.items():
        mouse_group = assignments.get(mouse)
        if mouse_group not in selected_groups:
            continue

        intervals = merged.get_freezing_intervals()
        if fps is None:
            fps = merged.fps
        acc_epochs_on = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after)
        acc_epochs_off = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off')
        adn_epochs_on = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after)
        adn_epochs_off = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off')
        
        # Append epochs to the proper group in the dictionaries.
        acc_on_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in acc_epochs_on])
        acc_off_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in acc_epochs_off])
        adn_on_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in adn_epochs_on])
        adn_off_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in adn_epochs_off])
    
    # If no data was collected, show a message.
    if fps is None:
        return html.Div("No data available for the selected condition groups.")
    
    # Generate the average plots using dictionaries.
    acc_on_fig, acc_off_fig = generate_average_plot("ACC", acc_on_dict, acc_off_dict, seconds_before, seconds_after, fps)
    adn_on_fig, adn_off_fig = generate_average_plot("ADN", adn_on_dict, adn_off_dict, seconds_before, seconds_after, fps)
    
    content = html.Div([
        html.Div([
            dcc.Graph(id='accavgon', figure=acc_on_fig),
            dcc.Graph(id='adnavgon', figure=adn_on_fig)
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(id='accavgoff', figure=acc_off_fig),
            dcc.Graph(id='adnavgoff', figure=adn_off_fig)
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            html.H3("Averaged Data Color Settings"),
            dcc.Dropdown(
                id='average-plot-dropdown',
                options=[
                    {'label': 'ACC Onset', 'value': 'accavgon'},
                    {'label': 'ACC Offset', 'value': 'accavgoff'},
                    {'label': 'ADN Onset', 'value': 'adnavgon'},
                    {'label': 'ADN Offset', 'value': 'adnavgoff'}
                ],
                value='accavgon',
                placeholder="Select an average plot"
            ),
            dcc.Dropdown(
                id='average-trace-dropdown',
                options=[],
                value=None,
                placeholder="Select a trace"
            ),
            daq.ColorPicker(
                id='average-color-picker',
                label='Pick a color for the Average Tab',
                value={'rgb': dict(r=0, g=0, b=255, a=0)}
            )
        ], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'})
    ])
    return content