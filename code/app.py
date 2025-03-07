import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
import os
import dash_daq as daq
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
import sys
import time
import webbrowser

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
    for mouse in mouse_folders:
        photometry_path = os.path.join(data_dir, mouse, f"{mouse}.csv")
        behavior_path = os.path.join(data_dir, mouse, "Behavior.csv")
        if os.path.exists(photometry_path) and os.path.exists(behavior_path):
            photometry = PhotometryDataset(photometry_path, column_map={"channel1_410": "ACC.control",
                             "channel1_470": "ACC.signal",
                             "channel2_410": "ADN.control",
                             "channel2_470": "ADN.signal"})
            behavior = BehaviorDataset(behavior_path)
            photometry.normalize_signal()
            merged = MergeDatasets(photometry, behavior)

            mouse_data[mouse] = merged
    print(f"Loaded raw data for {len(mouse_data)} mice: {list(mouse_data.keys())}")

# Initial load of raw data
load_raw_data()

app = dash.Dash(__name__, assets_folder='../assets')

app.layout = html.Div([
    # Header image
    html.Div([
        html.Img(src='assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),
    
    # Dropdown and reprocess button
    html.Div([
        dcc.Dropdown(
            id='mouse-dropdown',
            options=(
                [{"label": "Averaged Data", "value": "average"}] +
                [{"label": f"Mouse {mouse}", "value": mouse} for mouse in mouse_data]
            ) if mouse_data else [{"label": "No data available", "value": "None"}],
            # Default selection is "Averaged Data" if data exist
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
    
    html.Div([
        html.Div([
                dcc.Input(id="input-interval-before", type="number", placeholder="Time before event", min=0, value=3),
                dcc.Input(id="input-interval-after", type="number", placeholder="Time after event", min=0, value=3),
                html.Div(id="number-out")
            ], style={'display': 'inline-block', 'vertical-align': 'top'}),
        # Main content area for graphs
        html.Div(id='tab-content'),
    ], 
    # align vertically
    style={'display': 'flex', 'flex-direction': 'column'}
    ),
    
    # Footer image
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

def generate_average_plot(sensor, epochs_on, epochs_off, duration, fps):
    """Generate average epoch plots (onset and offset) for a given sensor."""
    x = np.arange(-duration, duration, 1/fps)
    # Onset average plot
    fig_on = go.Figure()
    if epochs_on:
        arr = np.array(epochs_on)
        mean_on = np.mean(arr, axis=0)
        std_on = np.std(arr, axis=0)
        fig_on.add_trace(go.Scatter(x=x, y=mean_on, mode='lines', name='Mean'))
        fig_on.add_trace(go.Scatter(
            x=x, y=mean_on+std_on,
            mode='lines',
            fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            hoverinfo="skip"
        ))
        fig_on.add_trace(go.Scatter(
            x=x, y=mean_on-std_on,
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            hoverinfo="skip"
        ))
    fig_on.update_layout(title=f'{sensor} Onset Average Epoch', xaxis_title='Time (s)', yaxis_title='Signal')
    
    # Offset average plot
    fig_off = go.Figure()
    if epochs_off:
        arr = np.array(epochs_off)
        mean_off = np.mean(arr, axis=0)
        std_off = np.std(arr, axis=0)
        fig_off.add_trace(go.Scatter(x=x, y=mean_off, mode='lines', name='Mean'))
        fig_off.add_trace(go.Scatter(
            x=x, y=mean_off+std_off,
            mode='lines',
            fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            hoverinfo="skip"
        ))
        fig_off.add_trace(go.Scatter(
            x=x, y=mean_off-std_off,
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            hoverinfo="skip"
        ))
    fig_off.update_layout(title=f'{sensor} Offset Average Epoch', xaxis_title='Time (s)', yaxis_title='Signal')
    
    return fig_on, fig_off

def generate_plots(mergeddataset, intervals, fps, duration, epochs_acc_on, epochs_acc_off, name='ACC'):
    """Generate detailed plots for a given sensor."""
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
    fig.update_layout(title=f'{name} Signal, Control, and zdFF', xaxis_title='Time (s)', yaxis_title='Value')
    
    # Dummy traces for legend
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
    
    aggregate_on = []
    aggregate_off = []
    
    # Plot epochs for onsets
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
    
    # Plot epochs for offsets
    for i, inter in enumerate(epochs_acc_off):
        x_epoch = np.arange(-duration, duration, 1 / fps)
        y_epoch = inter[2]
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'offset {i+1}', mode='lines', 
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_off.append(y_epoch)
    
    # Compute mean & std for onsets
    aggregate_on = np.array(aggregate_on)
    mean_on = np.mean(aggregate_on, axis=0) if len(aggregate_on) > 0 else None
    if mean_on is not None:
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

    # Compute mean & std for offsets
    aggregate_off = np.array(aggregate_off)
    mean_off = np.mean(aggregate_off, axis=0) if len(aggregate_off) > 0 else None
    if mean_off is not None:
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
    
    interval_on.update_layout(title='Signal around event onset', xaxis_title='Time (s)', yaxis_title='Signal',
                                paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(10, 10, 10, 0.02)')
    interval_off.update_layout(title='Signal around event offset', xaxis_title='Time (s)', yaxis_title='Signal',
                                 paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(10, 10, 10, 0.02)')
    fig.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)')
    
    return fig, interval_on, interval_off

@app.callback(
    [Output('mouse-dropdown', 'options'), Output('mouse-dropdown', 'value')],
    Input('reprocess-btn', 'n_clicks')
)
def update_dropdown(n_clicks):
    global graph_cache
    if n_clicks and n_clicks > 0:
        load_raw_data()
        graph_cache = {}
        print("Raw data reloaded and processed graphs cache cleared.")

    if not mouse_data:
        return [{"label": "No data available", "value": "None"}], "None"
    
    # Build the dropdown options
    options = [{"label": "Averaged Data", "value": "average"}]
    
    for mouse_folder in mouse_data:
        # If the folder name starts with "mouse", remove that substring to get just the number
        # e.g. "mouse3" -> "3"
        if mouse_folder.lower().startswith("mouse"):
            suffix = mouse_folder[len("mouse"):]  # e.g. remove 'mouse' from 'mouse3'
            label = f"Mouse {suffix}"
        else:
            # Fallback if the folder doesn't start with 'mouse'
            label = f"Mouse {mouse_folder}"
        
        options.append({"label": label, "value": mouse_folder})

    return options, "average"

# Callback to update the main content based on the dropdown selection.
@app.callback(
    Output('tab-content', 'children'),
    [Input('mouse-dropdown', 'value'),
    Input("input-interval-before", "value"),
    Input("input-interval-after", "value")],
)
def update_tab(selected_value, before, after):
    print(f"Selected value: {selected_value} | Before: {before} | After: {after}")
    if not selected_value:
        return "No data available."
    
    # If "Averaged Data" is selected, generate aggregated plots.
    if selected_value == "average":
        # If cached content exists, return it
        if "average" in graph_cache:
            return graph_cache["average"]
        
        acc_on_all = []
        acc_off_all = []
        adn_on_all = []
        adn_off_all = []
        duration = 1  # seconds
        fps = None
        
        # Aggregate epoch data across all mice
        for mouse, merged in mouse_data.items():
            intervals = merged.get_freezing_intervals()
            if fps is None:
                fps = merged.fps
            acc_epochs = merged.get_epoch_data(intervals, 'ACC', duration=duration)
            acc_epochs_off = merged.get_epoch_data(intervals, 'ACC', duration=duration, type='off')
            adn_epochs = merged.get_epoch_data(intervals, 'ADN', duration=duration)
            adn_epochs_off = merged.get_epoch_data(intervals, 'ADN', duration=duration, type='off')
            
            for epoch in acc_epochs:
                acc_on_all.append(epoch[2])
            for epoch in acc_epochs_off:
                acc_off_all.append(epoch[2])
            for epoch in adn_epochs:
                adn_on_all.append(epoch[2])
            for epoch in adn_epochs_off:
                adn_off_all.append(epoch[2])
        
        # Generate average plots
        acc_on_fig, acc_off_fig = generate_average_plot("ACC", acc_on_all, acc_off_all, duration, fps)
        adn_on_fig, adn_off_fig = generate_average_plot("ADN", adn_on_all, adn_off_all, duration, fps)
        
        content = html.Div([
            html.Div([
                dcc.Graph(figure=acc_on_fig),
                dcc.Graph(figure=adn_on_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Div([
                dcc.Graph(figure=acc_off_fig),
                dcc.Graph(figure=adn_off_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'})
        ])
        
        # Cache and return
        graph_cache["average"] = content
        return content
    
    # Otherwise, if a specific mouse is selected, display its graphs.
    else:
        if selected_value not in mouse_data:
            return "No data available."
        
        # If we have cached content for this mouse, return it
        if selected_value in graph_cache:
            return graph_cache[selected_value]
        
        print(f"Loading data for: {selected_value}")
        merged = mouse_data[selected_value]
        mergeddataset = merged.df
        duration = before  # seconds
        fps = merged.fps
        
        intervals = merged.get_freezing_intervals()
        epochs_acc = merged.get_epoch_data(intervals, 'ACC', duration=duration)
        epochs_acc_off = merged.get_epoch_data(intervals, 'ACC', duration=duration, type='off')
        epochs_adn = merged.get_epoch_data(intervals, 'ADN', duration=duration)
        epochs_adn_off = merged.get_epoch_data(intervals, 'ADN', duration=duration, type='off')
        
        # Generate plots for this mouse
        acc, acc_interval_on, acc_interval_off = generate_plots(
            mergeddataset, intervals, fps, duration, epochs_acc, epochs_acc_off, name='ACC'
        )
        adn, adn_interval_on, adn_interval_off = generate_plots(
            mergeddataset, intervals, fps, duration, epochs_adn, epochs_adn_off, name='ADN'
        )
        
        content = html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(id='acc',figure=acc),
                    dcc.Graph(id='adn',figure=adn),
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
                html.Div([
                    dcc.Graph(id='accintervalon',figure=acc_interval_on),
                    dcc.Graph(id='adnintervalon',figure=adn_interval_on),
                ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'}),
                html.Div([
                    dcc.Graph(id='accintervaloff',figure=acc_interval_off),
                    dcc.Graph(id='adnintervaloff' , figure=adn_interval_off),
                ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'})
            ], style={'display': 'flex', 'flex-direction': 'row'}),
        ], 
        # make style to align vertically
        style={'display': 'flex', 'flex-direction': 'column'}
        )
        
        # Cache and return
        #graph_cache[selected_value] = content
        return content

@app.callback(
    Output('acc', 'children'),  # You can replace this with a different Output if needed
    Input('graph', 'click_legend')  # Captures clicks on legend items
)
def display_clicked_legend(legend_data):
    if legend_data is None:
        return "Click on a legend item to see its details."

    # Extract the trace name (legend item clicked)
    clicked_trace_name = legend_data['trace']['name']
    clicked_trace_id = legend_data['trace']['uid']  # Unique ID of the trace

    print(f"Clicked Legend: ID={clicked_trace_id}, Name={clicked_trace_name}")
    
    return f"Clicked Legend: ID={clicked_trace_id}, Name={clicked_trace_name}"


if __name__ == '__main__':
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)