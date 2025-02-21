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

# Determine the base path (works for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")
data_dir = os.path.abspath(data_dir)

# Global containers:
# mouse_data stores raw (merged) data per mouse.
# graph_cache caches generated figures.
mouse_data = {}
graph_cache = {}

def load_raw_data():
    """Load raw merged data for all mouse folders."""
    global mouse_data
    mouse_data = {}
    mouse_folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    print("Found mouse folders:", mouse_folders)
    for folder in mouse_folders:
        photometry_path = os.path.join(data_dir, folder, "cfc_2046.csv")
        behavior_path = os.path.join(data_dir, folder, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")
        if os.path.exists(photometry_path) and os.path.exists(behavior_path):
            photometry = PhotometryDataset(photometry_path)
            behavior = BehaviorDataset(behavior_path)
            photometry.normalize_signal()
            merged = MergeDatasets(photometry, behavior)
            mouse_data[folder] = merged
        else:
            print(f"Skipping '{folder}' because required CSV files are missing.")
    print(f"Loaded raw data for {len(mouse_data)} folder(s):", list(mouse_data.keys()))

# Initial load of raw data
load_raw_data()

app = dash.Dash(__name__, assets_folder='../assets')

# Main layout: header, dropdown/reprocess, dynamic graph content, color editor panel, and footer.
app.layout = html.Div([
    # Header
    html.Div([
        html.Img(src='assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),
    
    # Dropdown and Reprocess button
    html.Div([
        dcc.Dropdown(
            id='mouse-dropdown',
            options=(
                [{"label": "Averaged Data", "value": "average"}] +
                [
                    {"label": f"Mouse {folder[len('mouse'):]}" if folder.lower().startswith("mouse")
                     else f"Mouse {folder}", "value": folder}
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
    
    # Dynamic graph content: two columns
    html.Div(id='tab-content'),
    
    # Color editor panel (for full-signal graphs only)
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
    ], style={'border': '1px solid #ccc', 'padding': '10px', 'width': '320px',
              'margin': '20px auto', 'text-align': 'center'}),
    
    # Footer
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

# Callback to update the dropdown on reprocess.
@app.callback(
    [Output('mouse-dropdown', 'options'), Output('mouse-dropdown', 'value')],
    Input('reprocess-btn', 'n_clicks')
)
def update_dropdown(n_clicks):
    global graph_cache
    if n_clicks and n_clicks > 0:
        load_raw_data()
        graph_cache = {}
        print("Raw data reloaded and graph cache cleared.")
    if not mouse_data:
        return [{"label": "No data available", "value": "None"}], "None"
    options = (
        [{"label": "Averaged Data", "value": "average"}] +
        [
            {"label": f"Mouse {folder[len('mouse'):]}" if folder.lower().startswith("mouse")
             else f"Mouse {folder}", "value": folder}
            for folder in mouse_data
        ]
    )
    return options, "average"

# Callback to build graph content based on dropdown selection.
@app.callback(
    Output('tab-content', 'children'),
    [Input('mouse-dropdown', 'value')]
)
def update_tab(selected_value):
    if not selected_value or selected_value == "None":
        return "No data available."
    
    if selected_value == "average":
        if not mouse_data:
            return "No data available."
        # Compute averages across all mice (full-signal only)
        all_acc_signal, all_acc_control, all_acc_zdFF = [], [], []
        all_adn_signal, all_adn_control, all_adn_zdFF = [], [], []
        for mouse, merged in mouse_data.items():
            df = merged.df
            all_acc_signal.append(df['ACC.signal'].values)
            all_acc_control.append(df['ACC.control'].values)
            all_acc_zdFF.append(df['ACC.zdFF'].values)
            all_adn_signal.append(df['ADN.signal'].values)
            all_adn_control.append(df['ADN.control'].values)
            all_adn_zdFF.append(df['ADN.zdFF'].values)
        all_acc_signal = np.array(all_acc_signal)
        all_acc_control = np.array(all_acc_control)
        all_acc_zdFF = np.array(all_acc_zdFF)
        all_adn_signal = np.array(all_adn_signal)
        all_adn_control = np.array(all_adn_control)
        all_adn_zdFF = np.array(all_adn_zdFF)
        avg_acc_signal = np.mean(all_acc_signal, axis=0)
        avg_acc_control = np.mean(all_acc_control, axis=0)
        avg_acc_zdFF   = np.mean(all_acc_zdFF, axis=0)
        avg_adn_signal = np.mean(all_adn_signal, axis=0)
        avg_adn_control = np.mean(all_adn_control, axis=0)
        avg_adn_zdFF   = np.mean(all_adn_zdFF, axis=0)
        length = len(avg_acc_signal)
        index = np.arange(length)
        # Build averaged full-signal figures
        acc_fig = go.Figure()
        acc_fig.add_trace(go.Scatter(x=index, y=avg_acc_signal, mode='lines', name='ACC Signal',
                                     line=dict(color='gray', width=1), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=index, y=avg_acc_control, mode='lines', name='ACC Control',
                                     line=dict(color='gray', width=1), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=index, y=avg_acc_zdFF, mode='lines', name='ACC zdFF',
                                     line=dict(color='blue', width=2)))
        acc_fig.update_layout(title='Averaged ACC')
        adn_fig = go.Figure()
        adn_fig.add_trace(go.Scatter(x=index, y=avg_adn_signal, mode='lines', name='ADN Signal',
                                     line=dict(color='gray', width=1), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=index, y=avg_adn_control, mode='lines', name='ADN Control',
                                     line=dict(color='gray', width=1), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=index, y=avg_adn_zdFF, mode='lines', name='ADN zdFF',
                                     line=dict(color='blue', width=2)))
        adn_fig.update_layout(title='Averaged ADN')
        # For simplicity, we omit interval/epoch plots for averaged data.
        full_signal_div = html.Div([
            dcc.Graph(id="acc-graph", figure=acc_fig),
            dcc.Graph(id="adn-graph", figure=adn_fig)
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'})
        interval_div = html.Div([
            html.Div("Interval/Epoch plots not available for Averaged Data.", style={'text-align': 'center'})
        ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top'})
        return html.Div([full_signal_div, interval_div])
    
    else:
        if selected_value not in mouse_data:
            return f"No data available for '{selected_value}'."
        merged = mouse_data[selected_value]
        df = merged.df
        # Full-signal graphs
        acc_fig = go.Figure()
        acc_fig.add_trace(go.Scatter(x=df.index, y=df['ACC.signal'], mode='lines', name='ACC Signal',
                                     line=dict(color='gray', width=1), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=df.index, y=df['ACC.control'], mode='lines', name='ACC Control',
                                     line=dict(color='gray', width=1), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=df.index, y=df['ACC.zdFF'], mode='lines', name='ACC zdFF',
                                     line=dict(color='blue', width=2)))
        acc_fig.update_layout(title=f"ACC - {selected_value}")
        adn_fig = go.Figure()
        adn_fig.add_trace(go.Scatter(x=df.index, y=df['ADN.signal'], mode='lines', name='ADN Signal',
                                     line=dict(color='gray', width=1), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=df.index, y=df['ADN.control'], mode='lines', name='ADN Control',
                                     line=dict(color='gray', width=1), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=df.index, y=df['ADN.zdFF'], mode='lines', name='ADN zdFF',
                                     line=dict(color='blue', width=2)))
        adn_fig.update_layout(title=f"ADN - {selected_value}")
        
        # Interval/epoch graphs:
        onsets = df[df['freezing'].diff() == 1].index
        offsets = df[df['freezing'].diff() == -1].index
        intervals = list(zip(onsets, offsets))
        fps = merged.fps
        epochs = [(int(on - fps*1.5), int(on + fps*1.5)) for on, off in intervals]
        acc_interval_fig = go.Figure()
        acc_epoch_list = []
        for inter in epochs:
            if inter[0] < 0 or inter[1] > len(df):
                continue
            else:
                x_vals = np.arange(-fps*1.5, fps*1.5)
                y_vals = df['ACC.signal'][inter[0]:inter[1]]
                acc_interval_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines',
                                                      line=dict(color='gray', width=1), opacity=0.5))
                acc_epoch_list.append(y_vals)
        if acc_epoch_list:
            acc_epoch_array = np.array(acc_epoch_list)
            mean_epoch = np.mean(acc_epoch_array, axis=0)
            acc_interval_fig.add_trace(go.Scatter(x=x_vals, y=mean_epoch, mode='lines',
                                                  line=dict(color='blue', width=2)))
        adn_interval_fig = go.Figure()
        adn_epoch_list = []
        for inter in epochs:
            if inter[0] < 0 or inter[1] > len(df):
                continue
            else:
                x_vals = np.arange(-fps*1.5, fps*1.5)
                y_vals = df['ADN.signal'][inter[0]:inter[1]]
                adn_interval_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines',
                                                      line=dict(color='gray', width=1), opacity=0.5))
                adn_epoch_list.append(y_vals)
        if adn_epoch_list:
            adn_epoch_array = np.array(adn_epoch_list)
            mean_epoch = np.mean(adn_epoch_array, axis=0)
            adn_interval_fig.add_trace(go.Scatter(x=x_vals, y=mean_epoch, mode='lines',
                                                  line=dict(color='blue', width=2)))
        full_signal_div = html.Div([
            dcc.Graph(id="acc-graph", figure=acc_fig),
            dcc.Graph(id="adn-graph", figure=adn_fig)
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'})
        interval_div = html.Div([
            dcc.Graph(id="acc-interval-graph", figure=acc_interval_fig),
            dcc.Graph(id="adn-interval-graph", figure=adn_interval_fig)
        ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top'})
        return html.Div([full_signal_div, interval_div])

# Callback to update the ACC full-signal graph color.
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

# Callback to update the ADN full-signal graph color.
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