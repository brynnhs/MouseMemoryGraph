import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
import os
from dash import dcc, html
from dash.dependencies import Input, Output, State
import sys
import time
import webbrowser
import dash_daq as daq
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets

# Determine the base path (works both for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")
data_dir = os.path.abspath(data_dir)

# Global containers:
# mouse_data will store the raw (merged) data for each mouse.
# graph_cache will store the processed figures.
mouse_data = {}
graph_cache = {}

def load_raw_data():
    """Load raw merged data for all mice and store in mouse_data."""
    global mouse_data
    mouse_data = {}
    
    # Detect available mouse folders
    mouse_folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    print("Found mouse folders:", mouse_folders)
    
    for folder in mouse_folders:
        photometry_path = os.path.join(data_dir, folder, "cfc_2046.csv")
        behavior_path = os.path.join(data_dir, folder, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")
        
        # Check if both CSV files exist
        photometry_exists = os.path.exists(photometry_path)
        behavior_exists = os.path.exists(behavior_path)
        print(f"Checking folder '{folder}': photometry={photometry_exists}, behavior={behavior_exists}")
        
        if photometry_exists and behavior_exists:
            # Load and merge
            photometry = PhotometryDataset(photometry_path)
            behavior = BehaviorDataset(behavior_path)
            photometry.normalize_signal()
            merged = MergeDatasets(photometry, behavior)
            # Store the merged data under the actual folder name
            mouse_data[folder] = merged
        else:
            print(f"  -> Skipping '{folder}' because required CSVs are missing.")
    
    print(f"Loaded raw data for {len(mouse_data)} valid folder(s): {list(mouse_data.keys())}")

# Initial load of raw data
load_raw_data()

app = dash.Dash(__name__, assets_folder='../assets')

# Main dashboard layout
app.layout = html.Div([
    # Header image
    html.Div([
        html.Img(src='assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),
    
    # Dropdown and reprocess button
    html.Div([
        dcc.Dropdown(
            id='mouse-dropdown',
            # Build the dropdown from the valid folders in mouse_data
            options=(
                [{"label": "Averaged Data", "value": "average"}] +
                [
                    {
                        "label": f"Mouse {folder[len('mouse'):]}" if folder.lower().startswith("mouse")
                                 else f"Mouse {folder}",
                        "value": folder
                    }
                    for folder in mouse_data
                ]
            ) if mouse_data else [{"label": "No data available", "value": "None"}],
            value="average" if mouse_data else "None",
            style={'width': '300px', 'margin': '0 auto'}
        ),
        html.Button(
            "Reprocess Data", 
            id="reprocess-btn", 
            n_clicks=0,
            style={
                'width': '150px', 
                'margin-top': '10px', 
                'padding': '10px',
                'background-color': 'red', 
                'color': 'white',
                'border': 'none', 
                'cursor': 'pointer'
            }
        )
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    
    # Main content area for graphs
    html.Div(id='tab-content'),
    
    # Color editor panel
    html.Div([
        html.H3("Color Editor for Full-Signal Graphs"),
        html.Div([
            html.H4("ACC Graph"),
            html.Label("Select Trace:"),
            dcc.Dropdown(
                id="acc-trace-selector",
                options=[
                    {"label": "ACC Signal", "value": 0},
                    {"label": "ACC Control", "value": 1},
                    {"label": "ACC zdFF", "value": 2}
                ],
                value=0
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="acc-color-picker",
                value={"hex": "#FF0000"}
            )
        ], style={'width': '300px', 'margin': '20px auto'}),
        html.Div([
            html.H4("ADN Graph"),
            html.Label("Select Trace:"),
            dcc.Dropdown(
                id="adn-trace-selector",
                options=[
                    {"label": "ADN Signal", "value": 0},
                    {"label": "ADN Control", "value": 1},
                    {"label": "ADN zdFF", "value": 2}
                ],
                value=0
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="adn-color-picker",
                value={"hex": "#FF0000"}
            )
        ], style={'width': '300px', 'margin': '20px auto'})
    ], style={'border': '1px solid #ccc', 'padding': '10px', 'width': '320px', 'margin': '20px auto', 'text-align': 'center'}),
    
    # Footer image
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

# Reprocess callback
@app.callback(
    [Output('mouse-dropdown', 'options'), Output('mouse-dropdown', 'value')],
    Input('reprocess-btn', 'n_clicks')
)
def update_dropdown(n_clicks):
    global graph_cache
    if n_clicks and n_clicks > 0:
        # Reload raw data and clear cached graphs
        load_raw_data()
        graph_cache = {}
        print("Raw data reloaded and processed graphs cache cleared.")
    
    if not mouse_data:
        return [{"label": "No data available", "value": "None"}], "None"
    
    options = (
        [{"label": "Averaged Data", "value": "average"}] +
        [
            {
                "label": f"Mouse {folder[len('mouse'):]}" if folder.lower().startswith("mouse")
                         else f"Mouse {folder}",
                "value": folder
            }
            for folder in mouse_data
        ]
    )
    return options, "average"

# Generate average plots (unchanged from your code)
def generate_average_plot(sensor, epochs_on, epochs_off, duration, fps):
    ...
    # same logic as before

# The main callback that builds the graph content
@app.callback(
    Output('tab-content', 'children'),
    [Input('mouse-dropdown', 'value')]
)
def update_tab(selected_value):
    if not selected_value or selected_value == "None":
        return "No data available."
    
    if selected_value == "average":
        # Return your averaged data visuals, or a message if no data
        if not mouse_data:
            return "No data available."
        # Or build your average plots here
        return "Placeholder for averaged data (or your real code)."
    
    if selected_value not in mouse_data:
        # If user picks a folder that doesn't have data loaded
        return f"No data available for '{selected_value}'. Check that CSV files exist."
    
    # If we do have data for the chosen mouse:
    merged = mouse_data[selected_value]
    mergeddataset = merged.df
    
    # Build your ACC/ADN figures exactly as you did before:
    # (We do a minimal example below for clarity.)

    acc_fig = go.Figure()
    acc_fig.add_trace(go.Scatter(
        x=mergeddataset.index,
        y=mergeddataset['ACC.signal'],
        mode='lines',
        name='ACC Signal',
        line=dict(color='gray', width=1),
        opacity=0.5
    ))
    acc_fig.add_trace(go.Scatter(
        x=mergeddataset.index,
        y=mergeddataset['ACC.control'],
        mode='lines',
        name='ACC Control',
        line=dict(color='gray', width=1),
        opacity=0.5
    ))
    acc_fig.add_trace(go.Scatter(
        x=mergeddataset.index,
        y=mergeddataset['ACC.zdFF'],
        mode='lines',
        name='ACC zdFF',
        line=dict(color='blue', width=2)
    ))
    acc_fig.update_layout(title='ACC Signal, Control, and zdFF')

    adn_fig = go.Figure()
    adn_fig.add_trace(go.Scatter(
        x=mergeddataset.index,
        y=mergeddataset['ADN.signal'],
        mode='lines',
        name='ADN Signal',
        line=dict(color='gray', width=1),
        opacity=0.5
    ))
    adn_fig.add_trace(go.Scatter(
        x=mergeddataset.index,
        y=mergeddataset['ADN.control'],
        mode='lines',
        name='ADN Control',
        line=dict(color='gray', width=1),
        opacity=0.5
    ))
    adn_fig.add_trace(go.Scatter(
        x=mergeddataset.index,
        y=mergeddataset['ADN.zdFF'],
        mode='lines',
        name='ADN zdFF',
        line=dict(color='blue', width=2)
    ))
    adn_fig.update_layout(title='ADN Signal, Control, and zdFF')
    
    return html.Div([
        dcc.Graph(id="acc-graph", figure=acc_fig),
        dcc.Graph(id="adn-graph", figure=adn_fig)
    ])

# Callbacks for color editing
@app.callback(
    Output("acc-graph", "figure"),
    [Input("acc-trace-selector", "value"), Input("acc-color-picker", "value")],
    State("acc-graph", "figure")
)
def update_acc_color(trace_idx, color_val, current_fig):
    if not current_fig:
        return dash.no_update
    chosen_color = color_val.get("hex", "#000000")
    current_fig["data"][trace_idx]["line"]["color"] = chosen_color
    return current_fig

@app.callback(
    Output("adn-graph", "figure"),
    [Input("adn-trace-selector", "value"), Input("adn-color-picker", "value")],
    State("adn-graph", "figure")
)
def update_adn_color(trace_idx, color_val, current_fig):
    if not current_fig:
        return dash.no_update
    chosen_color = color_val.get("hex", "#000000")
    current_fig["data"][trace_idx]["line"]["color"] = chosen_color
    return current_fig

if __name__ == '__main__':
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)