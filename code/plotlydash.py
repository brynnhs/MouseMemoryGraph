import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
import os

# Define the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "../data")

# Auto-detect all mouse folders
mouse_folders = [f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f))]

# Dictionary to store merged data for each mouse
mouse_data = {}

# Load datasets for all detected mice
for mouse in mouse_folders:
    photometry_path = os.path.join(data_dir, mouse, "cfc_2046.csv")
    behavior_path = os.path.join(data_dir, mouse, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")

    if os.path.exists(photometry_path) and os.path.exists(behavior_path):
        photometry = PhotometryDataset(photometry_path)
        behavior = BehaviorDataset(behavior_path)
        photometry.normalize_signal()
        merged = MergeDatasets(photometry, behavior).df
        mouse_data[mouse] = merged  # Store the merged dataframe

# Function to generate figures dynamically
def generate_figures(mergeddataset):
    """Returns ACC and ADN figures for a given dataset, including freezing behavior shading."""
    
    # Identify freezing onsets and offsets
    onsets = mergeddataset[mergeddataset['freezing'].diff() == 1].index
    offsets = mergeddataset[mergeddataset['freezing'].diff() == -1].index
    intervals = list(zip(onsets, offsets))

    # ACC Graph
    acc_fig = go.Figure()
    acc_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ACC.signal'], mode='lines',
                                 name='ACC Signal', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    acc_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ACC.control'], mode='lines',
                                 name='ACC Control', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    acc_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ACC.zdFF'], mode='lines',
                                 name='ACC zdFF', line=dict(color='blue', width=2, dash='solid')))
    acc_fig.update_layout(title='ACC Signal, Control, and zdFF', xaxis_title='Index', yaxis_title='Value')

    # Add freezing behavior shading
    for on, off in intervals:
        acc_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # ADN Graph
    adn_fig = go.Figure()
    adn_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ADN.signal'], mode='lines',
                                 name='ADN Signal', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    adn_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ADN.control'], mode='lines',
                                 name='ADN Control', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    adn_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ADN.zdFF'], mode='lines',
                                 name='ADN zdFF', line=dict(color='blue', width=2, dash='solid')))
    adn_fig.update_layout(title='ADN Signal, Control, and zdFF', xaxis_title='Index', yaxis_title='Value')

    # Add freezing behavior shading
    for on, off in intervals:
        adn_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    return acc_fig, adn_fig, intervals


# Function to generate epoch-averaged plots
def generate_epoch_figures(mergeddataset, intervals):
    """Generates epoch-averaged ACC and ADN responses around freezing behavior events."""
    
    fps = 100  # Sampling rate
    window = int(1.5 * fps)  # 1.5 seconds before and after
    epochs = [(int(on - window), int(on + window)) for on, _ in intervals]

    acc_interval_fig = go.Figure()
    adn_interval_fig = go.Figure()
    
    acc_aggregate_epoch = []
    adn_aggregate_epoch = []

    for inter in epochs:
        if inter[0] < 0 or inter[1] > len(mergeddataset):
            continue

        x = np.arange(-window, window)
        acc_y = mergeddataset['ACC.signal'][inter[0]:inter[1]]
        adn_y = mergeddataset['ADN.signal'][inter[0]:inter[1]]

        acc_interval_fig.add_trace(go.Scatter(
            x=x, y=acc_y, mode='lines', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
        adn_interval_fig.add_trace(go.Scatter(
            x=x, y=adn_y, mode='lines', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))

        acc_aggregate_epoch.append(acc_y)
        adn_aggregate_epoch.append(adn_y)

    # Compute and plot average ± std
    if acc_aggregate_epoch:
        acc_aggregate_epoch = np.array(acc_aggregate_epoch)
        acc_mean = np.mean(acc_aggregate_epoch, axis=0)
        acc_std = np.std(acc_aggregate_epoch, axis=0)

        acc_interval_fig.add_trace(go.Scatter(
            x=x, y=acc_mean, mode='lines', line=dict(color='blue', width=2, dash='solid')))

    if adn_aggregate_epoch:
        adn_aggregate_epoch = np.array(adn_aggregate_epoch)
        adn_mean = np.mean(adn_aggregate_epoch, axis=0)
        adn_std = np.std(adn_aggregate_epoch, axis=0)

        adn_interval_fig.add_trace(go.Scatter(
            x=x, y=adn_mean, mode='lines', line=dict(color='blue', width=2, dash='solid')))

    return acc_interval_fig, adn_interval_fig


# Initialize the Dash app
app = dash.Dash(__name__)

# Generate dynamic tab structure based on detected mice
app.layout = html.Div([
    dcc.Tabs(id="tabs", value=list(mouse_data.keys())[0] if mouse_data else None, children=[
        dcc.Tab(label=f"Mouse {mouse}", value=mouse) for mouse in mouse_data
    ]),
    html.Div(id='tab-content')
])


# Callback to update graphs based on selected tab
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def update_tab(selected_mouse):
    if selected_mouse and selected_mouse in mouse_data:
        acc_fig, adn_fig, intervals = generate_figures(mouse_data[selected_mouse])
        acc_interval_fig, adn_interval_fig = generate_epoch_figures(mouse_data[selected_mouse], intervals)

        return html.Div([
            html.Div([
                dcc.Graph(figure=acc_fig),
                dcc.Graph(figure=adn_fig),
            ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'}),
            
            html.Div([
                dcc.Graph(figure=acc_interval_fig),
                dcc.Graph(figure=adn_interval_fig),
            ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top'})
        ])
    return "No data available."

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='0.0.0.0')