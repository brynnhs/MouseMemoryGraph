import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
import os
import json
from dash import dcc, html
from dash.dependencies import Input, Output
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets

# Define directories
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "../data")
cache_dir = os.path.join(base_dir, "cached_plots")

# Ensure cache directory exists
os.makedirs(cache_dir, exist_ok=True)

# Load datasets for multiple mice
mouse_data = {}
mouse_folders = ["mouse1", "mouse2"]

for mouse in mouse_folders:
    photometry_path = os.path.join(data_dir, mouse, "cfc_2046.csv")
    behavior_path = os.path.join(data_dir, mouse, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")
    
    if os.path.exists(photometry_path) and os.path.exists(behavior_path):
        photometry = PhotometryDataset(photometry_path)
        behavior = BehaviorDataset(behavior_path)
        photometry.normalize_signal()
        merged = MergeDatasets(photometry, behavior).df
        mouse_data[mouse] = merged

app = dash.Dash(__name__)

# Layout with Tabs
app.layout = html.Div([
    html.Div([
        html.Img(src='/assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),

    html.Div([
        dcc.Tabs(id="tabs", value="mouse1", vertical=True, children=[
            dcc.Tab(label=f"Mouse {mouse}", value=mouse) for mouse in mouse_data
        ], style={'width': '100%'})
    ], style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div(id='tab-content', style={'width': '80%', 'display': 'inline-block', 'padding-left': '20px'}),

    html.Div([
        html.Img(src='/assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

# Function to save figures as JSON
def save_figure(fig, filename):
    with open(filename, "w") as f:
        json.dump(fig.to_dict(), f)

# Function to load figures from JSON
def load_figure(filename):
    with open(filename, "r") as f:
        return go.Figure(go.Figure(json.load(f)))

# Callback to update figures based on selected mouse
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def update_tab(selected_mouse):
    if selected_mouse not in mouse_data:
        return "No data available."
    
    dataset = mouse_data[selected_mouse]

    acc_fig_path = os.path.join(cache_dir, f"{selected_mouse}_ACC.json")
    adn_fig_path = os.path.join(cache_dir, f"{selected_mouse}_ADN.json")
    acc_interval_fig_path = os.path.join(cache_dir, f"{selected_mouse}_ACC_interval.json")
    adn_interval_fig_path = os.path.join(cache_dir, f"{selected_mouse}_ADN_interval.json")

    if all(os.path.exists(path) for path in [acc_fig_path, adn_fig_path, acc_interval_fig_path, adn_interval_fig_path]):
        # Load cached figures
        acc_fig = load_figure(acc_fig_path)
        adn_fig = load_figure(adn_fig_path)
        acc_interval_fig = load_figure(acc_interval_fig_path)
        adn_interval_fig = load_figure(adn_interval_fig_path)
    else:
        # Generate new figures
        acc_fig = go.Figure()
        adn_fig = go.Figure()

        # Process freezing periods
        fps = 100
        min_freeze_duration = int(0.1 * fps)

        rolling_freezing = dataset['freezing'].rolling(window=min_freeze_duration, center=True).sum()
        dataset['freezing_clean'] = (rolling_freezing >= min_freeze_duration).astype(int)

        onsets = dataset[dataset['freezing_clean'].diff() == 1].index.tolist()
        offsets = dataset[dataset['freezing_clean'].diff() == -1].index.tolist()

        if len(onsets) > len(offsets):
            offsets.append(dataset.index[-1])  
        elif len(offsets) > len(onsets):
            onsets.insert(0, dataset.index[0])  

        intervals = list(zip(onsets, offsets))

        # Apply blue shading for freezing periods
        for on, off in intervals:
            acc_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
            adn_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

        # Plot ACC signals
        acc_fig.add_trace(go.Scatter(x=dataset.index, y=dataset['ACC.signal'], mode='lines', name='ACC Signal', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=dataset.index, y=dataset['ACC.control'], mode='lines', name='ACC Control', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=dataset.index, y=dataset['ACC.zdFF'], mode='lines', name='ACC zdFF', line=dict(color='blue', width=2, dash='solid')))

        acc_fig.update_layout(title='ACC Signal, Control, and zdFF', xaxis_title='Index', yaxis_title='Value')

        # Plot ADN signals
        adn_fig.add_trace(go.Scatter(x=dataset.index, y=dataset['ADN.signal'], mode='lines', name='ADN Signal', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=dataset.index, y=dataset['ADN.control'], mode='lines', name='ADN Control', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=dataset.index, y=dataset['ADN.zdFF'], mode='lines', name='ADN zdFF', line=dict(color='blue', width=2, dash='solid')))

        adn_fig.update_layout(title='ADN Signal, Control, and zdFF', xaxis_title='Index', yaxis_title='Value')

        # Generate interval plots
        acc_interval_fig = go.Figure()
        adn_interval_fig = go.Figure()
        epochs = [(int(on - fps * 1.5), int(on + fps * 1.5)) for on, off in intervals]

        for inter in epochs:
            if inter[0] < 0 or inter[1] > len(dataset):
                continue
            x = np.arange(-fps * 1.5, fps * 1.5)
            acc_interval_fig.add_trace(go.Scatter(x=x, y=dataset['ACC.signal'][inter[0]:inter[1]], mode='lines', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))
            adn_interval_fig.add_trace(go.Scatter(x=x, y=dataset['ADN.signal'][inter[0]:inter[1]], mode='lines', line=dict(color='gray', width=1, dash='solid'), opacity=0.5))

        # Save figures
        save_figure(acc_fig, acc_fig_path)
        save_figure(adn_fig, adn_fig_path)
        save_figure(acc_interval_fig, acc_interval_fig_path)
        save_figure(adn_interval_fig, adn_interval_fig_path)

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

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)