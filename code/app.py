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
import pickle

# Determine the base path (works both for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")
data_dir = os.path.abspath(data_dir)

cache_file = "mouse_cache.pkl"  # File to store cache data

# Try to load cached data from disk
try:
    with open(cache_file, "rb") as f:
        cache = pickle.load(f)
    print("Cache loaded successfully.")
except (FileNotFoundError, EOFError):
    cache = {}  # Initialize an empty cache if no file exists

def load_data(force=False):
    """Load datasets dynamically and use cache to avoid redundant processing."""
    global mouse_data, mouse_folders, cache

    if force:
        # Clear the in-memory cache and delete the cache file
        cache = {}
        if os.path.exists(cache_file):
            os.remove(cache_file)
        print("Cache cleared; reprocessing all data.")

    mouse_data = {}
    # Detect available mouse folders
    mouse_folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    for mouse in mouse_folders:
        if mouse in cache and not force:  # Use cache if available and not forcing reprocess
            print(f"Loading cached data for: {mouse}")
            mouse_data[mouse] = cache[mouse]
        else:
            print(f"Processing data for: {mouse}")
            photometry_path = os.path.join(data_dir, mouse, "cfc_2046.csv")
            behavior_path = os.path.join(data_dir, mouse, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")

            if os.path.exists(photometry_path) and os.path.exists(behavior_path):
                photometry = PhotometryDataset(photometry_path)
                behavior = BehaviorDataset(behavior_path)
                photometry.normalize_signal()
                merged = MergeDatasets(photometry, behavior)

                mouse_data[mouse] = merged  # Store processed data
                cache[mouse] = merged  # Save to cache

    # Save updated cache to disk
    with open(cache_file, "wb") as f:
        pickle.dump(cache, f)
    print("Cache updated and saved.")

# Initial data load
load_data()

app = dash.Dash(__name__, assets_folder='../assets')

# Layout with a header, a dropdown (with the Reprocess button below it), and content below
app.layout = html.Div([
    # Header Image
    html.Div([
        html.Img(src='assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),

    # Dropdown for selecting mouse graphs and Reprocess Data button
    html.Div([
        dcc.Dropdown(
            id='mouse-dropdown',
            options=[{"label": f"Mouse {mouse}", "value": mouse} for mouse in mouse_folders] 
                     if mouse_folders else [{"label": "No data available", "value": "None"}],
            value=mouse_folders[0] if mouse_folders else "None",
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

    # Content that will display the mouse graphs
    html.Div(id='tab-content'),

    # Footer Image
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

@app.callback(
    [Output('mouse-dropdown', 'options'), Output('mouse-dropdown', 'value')],
    Input('reprocess-btn', 'n_clicks')
)
def update_dropdown(n_clicks):
    # Force reprocessing if the button has been clicked
    if n_clicks and n_clicks > 0:
        load_data(force=True)
    else:
        load_data(force=False)
    
    if not mouse_data:
        return [{"label": "No data available", "value": "None"}], "None"
    options = [{"label": f"Mouse {mouse}", "value": mouse} for mouse in mouse_data]
    # Select the first mouse by default
    return options, list(mouse_data.keys())[0]

# Callback to update the content based on the selected mouse
@app.callback(
    Output('tab-content', 'children'),
    [Input('mouse-dropdown', 'value'), Input('reprocess-btn', 'n_clicks')]
)
def update_tab(selected_mouse, n_clicks):
    if not selected_mouse or selected_mouse not in mouse_data:
        return "No data available."

    print(f"Loading data for: {selected_mouse}")

    merged = mouse_data[selected_mouse]  # Load from cache
    mergeddataset = merged.df
    duration = 3
    fps = merged.fps

    intervals = merged.get_freezing_intervals()
    epochs_acc = merged.get_epoch_data(intervals, 'ACC', duration=duration)
    epochs_acc_off = merged.get_epoch_data(intervals, 'ACC', duration=duration, type='off')
    epochs_adn = merged.get_epoch_data(intervals, 'ADN', duration=duration)
    epochs_adn_off = merged.get_epoch_data(intervals, 'ADN', duration=duration, type='off')

    # Generate Plots (using your pre-defined generate_plots function)
    acc, acc_interval_on, acc_interval_off = generate_plots(
        mergeddataset, intervals, fps, duration, epochs_acc, epochs_acc_off, name='ACC'
    )
    adn, adn_interval_on, adn_interval_off = generate_plots(
        mergeddataset, intervals, fps, duration, epochs_adn, epochs_adn_off, name='ADN'
    )

    return html.Div([
        html.Div([
            dcc.Graph(figure=acc),
            dcc.Graph(figure=adn),
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(figure=acc_interval_on),
            dcc.Graph(figure=adn_interval_on),
        ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(figure=acc_interval_off),
            dcc.Graph(figure=adn_interval_off),
        ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'})
    ])

def generate_plots(mergeddataset, intervals, fps, duration, epochs_acc_on, epochs_acc_off, name='ACC'):
    """Function to generate ACC and ADN plots with intervals."""
    fig = go.Figure(layout_yaxis_range=[-5, 5])
    interval_on = go.Figure(layout_yaxis_range=[-4, 4])
    interval_off = go.Figure(layout_yaxis_range=[-4, 4])

    x = np.arange(0, len(mergeddataset) / fps, 1 / fps)

    # Full signals
    fig.add_trace(go.Scatter(
        x=x, 
        y=mergeddataset[f'{name}.signal'], 
        mode='lines', 
        name=f'{name} Signal', 
        line=dict(color='gray', width=1, dash='solid'), 
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=x, 
        y=mergeddataset[f'{name}.control'], 
        mode='lines', 
        name=f'{name} Control', 
        line=dict(color='gray', width=1, dash='solid'), 
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=x, 
        y=mergeddataset[f'{name}.zdFF'], 
        mode='lines', 
        name=f'{name} zdFF', 
        line=dict(color='blue', width=2, dash='solid')
    ))

    fig.update_layout(title=f'{name} Signal, Control, and zdFF', xaxis_title='Index', yaxis_title='Value')

    # Add dummy traces for legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers', name=f'freezing bouts > {duration}s', 
        marker=dict(color='blue', size=7, symbol='square', opacity=0.2)
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers', name=f'freezing bouts < {duration}s', 
        marker=dict(color='lightblue', size=7, symbol='square', opacity=0.3)
    ))

    for on, off in intervals:
        on_sec = on / fps
        off_sec = off / fps
        fig.add_vrect(x0=on_sec, x1=off_sec, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # Create epochs for interval plots
    aggregate_on = []
    aggregate_off = []

    # Interval plotting for onsets
    for i, inter in enumerate(epochs_acc_on):
        x_epoch = np.arange(-duration, duration, 1 / fps)
        y_epoch = inter[2]
        interval_on.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'onset {i+1}', mode='lines', 
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_on.append(y_epoch)
        fig.add_vrect(
            x0=inter[1][0] / fps, x1=inter[1][1] / fps, fillcolor='blue', opacity=0.2, layer='below', line_width=0
        )

    # Interval plotting for offsets
    for i, inter in enumerate(epochs_acc_off):
        x_epoch = np.arange(-duration, duration, 1 / fps)
        y_epoch = inter[2]
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'offset {i+1}', mode='lines', 
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_off.append(y_epoch)

    # Compute mean & std across onset epochs
    aggregate_on = np.array(aggregate_on)
    mean_on = np.mean(aggregate_on, axis=0)
    std_on = np.std(aggregate_on, axis=0)
    interval_on.add_trace(go.Scatter(
        x=x_epoch, y=mean_on, mode='lines', name='mean signal', line=dict(color='blue', width=2, dash='solid')
    ))
    interval_on.add_trace(go.Scatter(
        x=x_epoch, y=mean_on + std_on, hoverinfo="skip", fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'), showlegend=False
    ))
    interval_on.add_trace(go.Scatter(
        x=x_epoch, y=mean_on - std_on, fill='tonexty', hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color='rgba(255,255,255,0)'), showlegend=False
    ))
    interval_on.add_vrect(x0=0, x1=duration, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # Compute mean & std across offset epochs
    aggregate_off = np.array(aggregate_off)
    mean_off = np.mean(aggregate_off, axis=0)
    std_off = np.std(aggregate_off, axis=0)
    interval_off.add_trace(go.Scatter(
        x=x_epoch, y=mean_off, mode='lines', name='mean signal', line=dict(color='blue', width=2, dash='solid')
    ))
    interval_off.add_trace(go.Scatter(
        x=x_epoch, y=mean_off + std_off, hoverinfo="skip", fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'), showlegend=False
    ))
    interval_off.add_trace(go.Scatter(
        x=x_epoch, y=mean_off - std_off, fill='tonexty', hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color='rgba(255,255,255,0)'), showlegend=False
    ))
    interval_off.add_vrect(x0=-duration, x1=0, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # Update interval layouts
    interval_on.update_layout(title='Signal around event onset', xaxis_title='Time (s)', yaxis_title='Signal')
    interval_off.update_layout(title='Signal around event offset', xaxis_title='Time (s)', yaxis_title='Signal')

    return fig, interval_on, interval_off

if __name__ == '__main__':
    # Give the server a moment to start before opening the browser
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)