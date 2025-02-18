import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
import os
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
import sys
import time
import webbrowser

if getattr(sys, 'frozen', False):
    # Running as an executable
    base_path = sys._MEIPASS
else:
    # Running as a script
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")  # Go to root of MouseMemoryGraph
data_dir = os.path.abspath(data_dir)

# Function to dynamically load mouse data
def load_data():
    """ Function to scan and load datasets dynamically, including newly added mice """
    global mouse_data, mouse_folders
    mouse_data = {}
    
    # Dynamically detect available mouse folders
    mouse_folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    
    for mouse in mouse_folders:
        photometry_path = os.path.join(data_dir, mouse, "cfc_2046.csv")
        behavior_path = os.path.join(data_dir, mouse, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")

        if os.path.exists(photometry_path) and os.path.exists(behavior_path):
            photometry = PhotometryDataset(photometry_path)
            behavior = BehaviorDataset(behavior_path)
            photometry.normalize_signal()
            merged = MergeDatasets(photometry, behavior).df
            mouse_data[mouse] = merged

# Initial data load
load_data()

app = dash.Dash(__name__)

# Layout with Tabs on the left and Reprocess Button below
app.layout = html.Div([
    html.Div([
        html.Img(src='/assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),

    html.Div([
        html.Div([
            dcc.Tabs(id="tabs", value=mouse_folders[0] if mouse_folders else None, vertical=True),
            html.Button("Reprocess Data", id="reprocess-btn", n_clicks=0,
                        style={'width': '100%', 'margin-top': '10px', 'padding': '10px',
                               'background-color': 'red', 'color': 'white',
                               'border': 'none', 'cursor': 'pointer'})
        ], style={'width': '15%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Div(id='tab-content', style={'width': '80%', 'display': 'inline-block', 'padding-left': '20px'})
    ], style={'display': 'flex'}),

    html.Div([
        html.Img(src='/assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

# Callback to update tabs when reprocessing is triggered
@app.callback(
    [Output('tabs', 'children'), Output('tabs', 'value')],
    Input('reprocess-btn', 'n_clicks')
)
def update_tabs(n_clicks):
    """ Update the list of tabs when reprocessing is triggered """
    load_data()  # Reload all available mouse data, including new mice
    
    if not mouse_data:
        return ["No data available"], None
    
    tabs = [dcc.Tab(label=f"Mouse {mouse}", value=mouse) for mouse in mouse_data]
    return tabs, list(mouse_data.keys())[0]  # Ensure a mouse is selected

# Callback to update plots and handle reprocessing
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value'), Input('reprocess-btn', 'n_clicks')]
)
def update_tab(selected_mouse, n_clicks):
    if not selected_mouse or selected_mouse not in mouse_data:
        return "No data available."

    print(f"Processing data for: {selected_mouse}")

    mergeddataset = mouse_data[selected_mouse].copy()

    # Apply Rolling Window to Reduce Freezing Noise
    fps = 100
    min_freeze_duration = int(0.1 * fps)
    rolling_freezing = mergeddataset['freezing'].rolling(window=min_freeze_duration, center=True).sum()
    mergeddataset['freezing_clean'] = (rolling_freezing >= min_freeze_duration).astype(int)

    # Detect Onsets & Offsets
    onsets = mergeddataset[mergeddataset['freezing_clean'].diff() == 1].index.tolist()
    offsets = mergeddataset[mergeddataset['freezing_clean'].diff() == -1].index.tolist()

    # Ensure matching onsets and offsets
    if len(onsets) > len(offsets):
        offsets.append(mergeddataset.index[-1])
    elif len(offsets) > len(onsets):
        onsets.insert(0, mergeddataset.index[0])

    intervals = list(zip(onsets, offsets))

    # ✅ Generate Plots
    acc_fig, adn_fig, acc_interval_fig, adn_interval_fig = generate_plots(mergeddataset, intervals, fps)

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

def generate_plots(mergeddataset, intervals, fps):
    """ Function to generate ACC and ADN plots with intervals """
    acc_fig = go.Figure()
    adn_fig = go.Figure()
    acc_interval_fig = go.Figure()
    adn_interval_fig = go.Figure()

    # Apply freezing intervals to full-trace plots
    for on, off in intervals:
        acc_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
        adn_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # Full ACC signals
    acc_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ACC.signal'], mode='lines', name='ACC Signal', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    acc_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ACC.control'], mode='lines', name='ACC Control', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    acc_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ACC.zdFF'], mode='lines', name='ACC zdFF', line=dict(color='blue', width=2, dash='solid')))

    acc_fig.update_layout(title='ACC Signal, Control, and zdFF', xaxis_title='Index', yaxis_title='Value')

    # Full ADN signals
    adn_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ADN.signal'], mode='lines', name='ADN Signal', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    adn_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ADN.control'], mode='lines', name='ADN Control', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
    adn_fig.add_trace(go.Scatter(x=mergeddataset.index, y=mergeddataset['ADN.zdFF'], mode='lines', name='ADN zdFF', line=dict(color='blue', width=2, dash='solid')))

    adn_fig.update_layout(title='ADN Signal, Control, and zdFF', xaxis_title='Index', yaxis_title='Value')

    # Create epochs for interval plots
    epochs = [(int(on - fps * 1.5), int(on + fps * 1.5)) for on, off in intervals]
    aggregate_acc = []
    aggregate_adn = []

    # Interval plotting
    for inter in epochs:
        if inter[0] < 0 or inter[1] > len(mergeddataset):
            continue  # Ignore out-of-bounds epochs

        # Define x-axis for epoch (-1.5s to 1.5s)
        x = np.linspace(-1.5, 1.5, num=inter[1] - inter[0])

        # Extract and plot epochs
        y_acc = mergeddataset['ACC.signal'].iloc[inter[0]:inter[1]].values
        y_adn = mergeddataset['ADN.signal'].iloc[inter[0]:inter[1]].values

        acc_interval_fig.add_trace(go.Scatter(x=x, y=y_acc, mode='lines', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
        adn_interval_fig.add_trace(go.Scatter(x=x, y=y_adn, mode='lines', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))

        aggregate_acc.append(y_acc)
        aggregate_adn.append(y_adn)

    # Compute mean & standard deviation across epochs
    aggregate_acc = np.array(aggregate_acc)
    aggregate_adn = np.array(aggregate_adn)

    if len(aggregate_acc) > 0:
        mean_acc = np.mean(aggregate_acc, axis=0)
        acc_interval_fig.add_trace(go.Scatter(x=x, y=mean_acc, mode='lines', line=dict(color='blue', width=2, dash='solid')))

    if len(aggregate_adn) > 0:
        mean_adn = np.mean(aggregate_adn, axis=0)
        adn_interval_fig.add_trace(go.Scatter(x=x, y=mean_adn, mode='lines', line=dict(color='blue', width=2, dash='solid')))

    # Update layouts
    acc_interval_fig.update_layout(title='ACC Event-Aligned Intervals', xaxis_title='Time (s)', yaxis_title='Signal')
    adn_interval_fig.update_layout(title='ADN Event-Aligned Intervals', xaxis_title='Time (s)', yaxis_title='Signal')

    return acc_fig, adn_fig, acc_interval_fig, adn_interval_fig  # ✅ Correctly returning separate plots


if __name__ == '__main__':
    # Give the server a moment to start before opening the browser
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)