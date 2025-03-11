import os
import sys
import time
import webbrowser
import dash
import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
from dash_local_react_components import load_react_component

# Import visualization functions (from your separate file)
from visualize import generate_plots

dash.register_page(__name__, path_template='/mouse/<id>')

# Determine the base path (works both for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../../data")
data_dir = os.path.abspath(data_dir)

# Global container:
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

def layout(id=None, **other_unknown_query_strings):
    mouse = id
    return html.Div([
        dcc.Location(id='url'),
        html.H2(f'Mouse {mouse}'),
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
        html.Div(id='mouse-content')
    ])

@callback(
    Output('mouse-content', 'children'),
    [Input('seconds-before', 'value'),
     Input('seconds-after', 'value'),
     Input('url', 'pathname')],
)

def update_graph(seconds_before, seconds_after, pathname):
    mouse = pathname.split('/')[-1]
    if mouse not in mouse_data:
            return "No data available."
        
    merged = mouse_data[mouse]
    mergeddataset = merged.df
    fps = merged.fps
    
    intervals = merged.get_freezing_intervals()
    epochs_acc_on = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after)
    epochs_acc_off = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off')
    epochs_adn_on = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after)
    epochs_adn_off = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off')

    acc_avg_on = merged.get_epoch_average(intervals, 'ACC', before=seconds_before, after=seconds_after)
    adn_avg_on = merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after)
    acc_avg_off = merged.get_epoch_average(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off')
    adn_avg_off = merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off')
    
    acc_full, acc_interval_on, acc_interval_off, acc_change = generate_plots(
        mergeddataset, intervals, fps, seconds_before, seconds_after, epochs_acc_on, epochs_acc_off, 
        acc_avg_on, acc_avg_off,
        name='ACC'
    )
    adn_full, adn_interval_on, adn_interval_off, adn_change = generate_plots(
        mergeddataset, intervals, fps, seconds_before, seconds_after, epochs_adn_on, epochs_adn_off, 
        adn_avg_on, adn_avg_off,
        name='ADN'
    )
    
    content = html.Div([
        # ACC Section
        html.Div([
            html.H3("ACC"),
            dcc.Graph(id='acc', figure=acc_full),
            html.Div([
                dcc.Graph(id='accintervalon', figure=acc_interval_on, 
                            style={'width': '35%', 'display': 'inline-block'}),
                dcc.Graph(id='accintervaloff', figure=acc_interval_off, 
                            style={'width': '35%', 'display': 'inline-block'}),
                dcc.Graph(id='accchange', figure=acc_change,
                            style={'width': '30%', 'display': 'inline-block'})
            ], style={'display': 'flex', 'justify-content': 'space-around'})
        ], style={'margin-bottom': '40px'}),
        
        # ADN Section
        html.Div([
            html.H3("ADN"),
            dcc.Graph(id='adn', figure=adn_full),
            html.Div([
                dcc.Graph(id='adnintervalon', figure=adn_interval_on, 
                            style={'width': '35%', 'display': 'inline-block'}),
                dcc.Graph(id='adnintervaloff', figure=adn_interval_off, 
                            style={'width': '35%', 'display': 'inline-block'}),
                dcc.Graph(id='adnchange', figure=adn_change,
                            style={'width': '30%', 'display': 'inline-block'})
            ], style={'display': 'flex', 'justify-content': 'space-around'})
        ], style={'margin-bottom': '40px'}),
        
        # Color picker sections for ACC and ADN
        html.Div([
            html.Div([
                html.H3("ACC Color Settings"),
                dcc.Dropdown(
                    id='acc-plot-dropdown',
                    options=[
                        {'label': 'Full Signal', 'value': 'full'},
                        {'label': 'Interval On', 'value': 'interval_on'},
                        {'label': 'Interval Off', 'value': 'interval_off'},
                    ],
                    value='full',
                    placeholder="Select a plot"
                ),
                dcc.Dropdown(
                    id='acc-trace-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a trace"
                ),
                daq.ColorPicker(
                    id='acc-color-picker',
                    label='Pick a color for ACC',
                    value={'rgb': dict(r=128, g=128, b=128, a=0)}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'}),
            
            html.Div([
                html.H3("ADN Color Settings"),
                dcc.Dropdown(
                    id='adn-plot-dropdown',
                    options=[
                        {'label': 'Full Signal', 'value': 'full'},
                        {'label': 'Interval On', 'value': 'interval_on'},
                        {'label': 'Interval Off', 'value': 'interval_off'},
                    ],
                    value='full',
                    placeholder="Select a plot"
                ),
                dcc.Dropdown(
                    id='adn-trace-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a trace"
                ),
                daq.ColorPicker(
                    id='adn-color-picker',
                    label='Pick a color for ADN',
                    value={'rgb': dict(r=128, g=128, b=128, a=0)}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-around'})
    ], style={'display': 'flex', 'flex-direction': 'column'})
    
    return content