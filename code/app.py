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
import pickle

# ----------------------------------------------------------------
# Data Loading & Caching
# ----------------------------------------------------------------
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")
data_dir = os.path.abspath(data_dir)
cache_file = "mouse_cache.pkl"

try:
    with open(cache_file, "rb") as f:
        cache = pickle.load(f)
    print("Cache loaded successfully.")
except (FileNotFoundError, EOFError):
    cache = {}

mouse_data = {}
mouse_folders = []

def load_data():
    """Load datasets dynamically and use cache to avoid redundant processing."""
    global mouse_data, mouse_folders
    mouse_data = {}
    mouse_folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    for mouse in mouse_folders:
        if mouse in cache:
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
                mouse_data[mouse] = merged
                cache[mouse] = merged

    with open(cache_file, "wb") as f:
        pickle.dump(cache, f)
    print("Cache updated and saved.")

# Initial data load
load_data()

# ----------------------------------------------------------------
# App Initialization
# ----------------------------------------------------------------
app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True)

# ----------------------------------------------------------------
# Layout
# ----------------------------------------------------------------
app.layout = html.Div([
    # Header Image
    html.Div([
        html.Img(src='assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),

    # Dropdown & Reprocess Button
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

    # Main content area for the mouse graphs
    html.Div(id='tab-content'),

    # ----------------------------------------------------------------
    # Color Editor Panel for Full-Signal Graphs
    # ----------------------------------------------------------------
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
                value=0,
                style={'width': '250px', 'margin': '0 auto'}
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="acc-color-picker",
                value={"hex": "#FF0000"},
                size=150
            )
        ], style={'width': '300px', 'margin': '20px auto', 'text-align': 'center'}),

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
                value=0,
                style={'width': '250px', 'margin': '0 auto'}
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="adn-color-picker",
                value={"hex": "#FF0000"},
                size=150
            )
        ], style={'width': '300px', 'margin': '20px auto', 'text-align': 'center'})
    ], style={'border': '1px solid #ccc', 'padding': '10px', 'width': '320px',
              'margin': '20px auto', 'text-align': 'center'}),

    # ----------------------------------------------------------------
    # Color Editor Panel for Interval Graphs
    #
    # We assume up to 10 lines in each interval figure:
    #  - 0..8 => onset i or offset i
    #  - 9 => mean line
    # ----------------------------------------------------------------
    html.Div([
        html.H3("Color Editor for Interval Onset/Offset Graphs"),

        html.Div([
            html.H4("ACC Onset"),
            html.Label("Select Trace:"),
            dcc.Dropdown(
                id="acc-on-trace-selector",
                options=[{"label": f"Onset {i+1}", "value": i} for i in range(9)] +
                        [{"label": "Mean Onset", "value": 9}],
                value=9,  # default to mean
                style={'width': '250px', 'margin': '0 auto'}
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="acc-on-color-picker",
                value={"hex": "#00FF00"},
                size=150
            )
        ], style={'width': '300px', 'margin': '20px auto', 'text-align': 'center'}),

        html.Div([
            html.H4("ACC Offset"),
            html.Label("Select Trace:"),
            dcc.Dropdown(
                id="acc-off-trace-selector",
                options=[{"label": f"Offset {i+1}", "value": i} for i in range(9)] +
                        [{"label": "Mean Offset", "value": 9}],
                value=9,
                style={'width': '250px', 'margin': '0 auto'}
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="acc-off-color-picker",
                value={"hex": "#00FF00"},
                size=150
            )
        ], style={'width': '300px', 'margin': '20px auto', 'text-align': 'center'}),

        html.Div([
            html.H4("ADN Onset"),
            html.Label("Select Trace:"),
            dcc.Dropdown(
                id="adn-on-trace-selector",
                options=[{"label": f"Onset {i+1}", "value": i} for i in range(9)] +
                        [{"label": "Mean Onset", "value": 9}],
                value=9,
                style={'width': '250px', 'margin': '0 auto'}
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="adn-on-color-picker",
                value={"hex": "#00FF00"},
                size=150
            )
        ], style={'width': '300px', 'margin': '20px auto', 'text-align': 'center'}),

        html.Div([
            html.H4("ADN Offset"),
            html.Label("Select Trace:"),
            dcc.Dropdown(
                id="adn-off-trace-selector",
                options=[{"label": f"Offset {i+1}", "value": i} for i in range(9)] +
                        [{"label": "Mean Offset", "value": 9}],
                value=9,
                style={'width': '250px', 'margin': '0 auto'}
            ),
            html.Label("Pick a Color:"),
            daq.ColorPicker(
                id="adn-off-color-picker",
                value={"hex": "#00FF00"},
                size=150
            )
        ], style={'width': '300px', 'margin': '20px auto', 'text-align': 'center'})

    ], style={'border': '1px solid #ccc', 'padding': '10px', 'width': '320px',
              'margin': '20px auto', 'text-align': 'center'}),

    # Footer Image
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

# ----------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------
@app.callback(
    [Output('mouse-dropdown', 'options'), Output('mouse-dropdown', 'value')],
    Input('reprocess-btn', 'n_clicks')
)
def update_dropdown(n_clicks):
    load_data()
    if not mouse_data:
        return [{"label": "No data available", "value": "None"}], "None"
    opts = [{"label": f"Mouse {m}", "value": m} for m in mouse_data]
    return opts, list(mouse_data.keys())[0]

@app.callback(
    Output('tab-content', 'children'),
    [Input('mouse-dropdown', 'value'), Input('reprocess-btn', 'n_clicks')]
)
def update_tab(selected_mouse, _):
    if not selected_mouse or selected_mouse not in mouse_data:
        return "No data available."

    print(f"Loading data for: {selected_mouse}")
    merged = mouse_data[selected_mouse]
    mergeddataset = merged.df
    duration = 3
    fps = merged.fps

    intervals = merged.get_freezing_intervals()
    epochs_acc = merged.get_epoch_data(intervals, 'ACC', duration=duration)
    epochs_acc_off = merged.get_epoch_data(intervals, 'ACC', duration=duration, type='off')
    epochs_adn = merged.get_epoch_data(intervals, 'ADN', duration=duration)
    epochs_adn_off = merged.get_epoch_data(intervals, 'ADN', duration=duration, type='off')

    acc, acc_interval_on, acc_interval_off = generate_plots(
        mergeddataset, intervals, fps, duration, epochs_acc, epochs_acc_off, name='ACC'
    )
    adn, adn_interval_on, adn_interval_off = generate_plots(
        mergeddataset, intervals, fps, duration, epochs_adn, epochs_adn_off, name='ADN'
    )

    return html.Div([
        html.Div([
            dcc.Graph(id="acc-graph", figure=acc),
            dcc.Graph(id="adn-graph", figure=adn)
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(id="acc-interval-on-graph", figure=acc_interval_on),
            dcc.Graph(id="adn-interval-on-graph", figure=adn_interval_on)
        ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(id="acc-interval-off-graph", figure=acc_interval_off),
            dcc.Graph(id="adn-interval-off-graph", figure=adn_interval_off)
        ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'})
    ])

def generate_plots(mergeddataset, intervals, fps, duration, epochs_acc_on, epochs_acc_off, name='ACC'):
    """Your original function for generating full-signal & interval plots."""
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

    # Freezing shading (fixed opacity)
    for on, off in intervals:
        on_sec = on / fps
        off_sec = off / fps
        fig.add_vrect(x0=on_sec, x1=off_sec, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # Onset/offset plots
    aggregate_on = []
    aggregate_off = []

    # Onset
    for i, inter in enumerate(epochs_acc_on):
        x_epoch = np.arange(-duration, duration, 1 / fps)
        y_epoch = inter[2]
        interval_on.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'onset {i+1}', mode='lines',
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_on.append(y_epoch)
        fig.add_vrect(x0=inter[1][0]/fps, x1=inter[1][1]/fps, fillcolor='blue', opacity=0.2, layer='below', line_width=0)

    # Offset
    for i, inter in enumerate(epochs_acc_off):
        x_epoch = np.arange(-duration, duration, 1 / fps)
        y_epoch = inter[2]
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'offset {i+1}', mode='lines',
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_off.append(y_epoch)

    # Onset: mean & std
    aggregate_on = np.array(aggregate_on)
    mean_on = np.mean(aggregate_on, axis=0)
    std_on = np.std(aggregate_on, axis=0)
    interval_on.add_trace(go.Scatter(
        x=x_epoch, y=mean_on, mode='lines', name='mean signal',
        line=dict(color='blue', width=2, dash='solid')
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

    # Offset: mean & std
    aggregate_off = np.array(aggregate_off)
    mean_off = np.mean(aggregate_off, axis=0)
    std_off = np.std(aggregate_off, axis=0)
    interval_off.add_trace(go.Scatter(
        x=x_epoch, y=mean_off, mode='lines', name='mean signal',
        line=dict(color='blue', width=2, dash='solid')
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

# ----------------------------------------------------------------
# Callbacks for Full-Signal Graph Color Editing
# ----------------------------------------------------------------
@app.callback(
    Output("acc-graph", "figure"),
    [Input("acc-trace-selector", "value"), Input("acc-color-picker", "value")],
    State("acc-graph", "figure")
)
def update_acc_color(trace_idx, color_val, current_fig):
    """Recolor the chosen ACC trace in the full-signal graph."""
    if not current_fig or color_val is None:
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
    """Recolor the chosen ADN trace in the full-signal graph."""
    if not current_fig or color_val is None:
        return dash.no_update
    chosen_color = color_val.get("hex", "#000000")
    current_fig["data"][trace_idx]["line"]["color"] = chosen_color
    return current_fig

# ----------------------------------------------------------------
# Callbacks for Interval Graphs Color Editing
# We assume each interval figure has up to 10 lines:
#   0..8 => onset i or offset i
#   9 => mean line
# ----------------------------------------------------------------
@app.callback(
    Output("acc-interval-on-graph", "figure"),
    [Input("acc-on-trace-selector", "value"), Input("acc-on-color-picker", "value")],
    State("acc-interval-on-graph", "figure")
)
def update_acc_on_color(trace_idx, color_val, current_fig):
    """Recolor the chosen trace in the ACC Onset figure."""
    if not current_fig or color_val is None:
        return dash.no_update
    if trace_idx < len(current_fig["data"]):
        chosen_color = color_val.get("hex", "#000000")
        current_fig["data"][trace_idx]["line"]["color"] = chosen_color
    return current_fig

@app.callback(
    Output("acc-interval-off-graph", "figure"),
    [Input("acc-off-trace-selector", "value"), Input("acc-off-color-picker", "value")],
    State("acc-interval-off-graph", "figure")
)
def update_acc_off_color(trace_idx, color_val, current_fig):
    """Recolor the chosen trace in the ACC Offset figure."""
    if not current_fig or color_val is None:
        return dash.no_update
    if trace_idx < len(current_fig["data"]):
        chosen_color = color_val.get("hex", "#000000")
        current_fig["data"][trace_idx]["line"]["color"] = chosen_color
    return current_fig

@app.callback(
    Output("adn-interval-on-graph", "figure"),
    [Input("adn-on-trace-selector", "value"), Input("adn-on-color-picker", "value")],
    State("adn-interval-on-graph", "figure")
)
def update_adn_on_color(trace_idx, color_val, current_fig):
    """Recolor the chosen trace in the ADN Onset figure."""
    if not current_fig or color_val is None:
        return dash.no_update
    if trace_idx < len(current_fig["data"]):
        chosen_color = color_val.get("hex", "#000000")
        current_fig["data"][trace_idx]["line"]["color"] = chosen_color
    return current_fig

@app.callback(
    Output("adn-interval-off-graph", "figure"),
    [Input("adn-off-trace-selector", "value"), Input("adn-off-color-picker", "value")],
    State("adn-interval-off-graph", "figure")
)
def update_adn_off_color(trace_idx, color_val, current_fig):
    """Recolor the chosen trace in the ADN Offset figure."""
    if not current_fig or color_val is None:
        return dash.no_update
    if trace_idx < len(current_fig["data"]):
        chosen_color = color_val.get("hex", "#000000")
        current_fig["data"][trace_idx]["line"]["color"] = chosen_color
    return current_fig

# ----------------------------------------------------------------
# Run the App
# ----------------------------------------------------------------
if __name__ == '__main__':
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=True, port=8050)