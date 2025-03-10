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

from dash_local_react_components import load_react_component

# Determine the base path (works both for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")
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

app = dash.Dash(__name__, assets_folder='../assets', suppress_callback_exceptions=True)

# load component
GroupDropdown = load_react_component(app, "components", "GroupDropdown.js")

app.layout = html.Div([
    # Header image
    html.Div([
        html.Img(src='assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),
    
    # Dropdown (options are set from the loaded data)
    html.Div([
        dcc.Dropdown(
            id='mouse-dropdown',
            options=(
                [{"label": "Averaged Data", "value": "average"}] +
                [{"label": f"Mouse {mouse}", "value": mouse} for mouse in mouse_data]
            ) if mouse_data else [{"label": "No data available", "value": "None"}],
            value="average" if mouse_data else "None",
            style={'width': '300px', 'margin': '0 auto'}
        )
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    # NEW: Group dropdown for each mouse tab
    html.Div([
        GroupDropdown(id='group-dropdown', value=1)
    ], style={'width': '100%', 'text-align': 'left', 'margin-bottom': '20px'}),

    # NEW: Two numeric inputs for epoch window: seconds before and after event
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
    
    # Main content area for graphs
    html.Div(id='tab-content'),
    
    # Footer image
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'}),

    # Store component to persist state
    dcc.Store(id='app-state', storage_type='session')
])

def generate_average_plot(sensor, epochs_on, epochs_off, before, after, fps):
    """
    Generate mean ± std plots for ON and OFF epochs, for all mice combined.
    The window is from -before to +after.
    """
    x = np.arange(-before, after, 1/fps)
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
    fig_on.add_vrect(x0=-before, x1=0, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
    fig_on.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )
    
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
    fig_off.add_vrect(x0=0, x1=after, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
    fig_off.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )
    
    return fig_on, fig_off

def generate_plots(mergeddataset, intervals, fps, before, after, epochs_acc_on, epochs_acc_off, avg_on, avg_off, name='ACC'):
    """
    Generate detailed plots for the given sensor: 
      - The full signals figure 
      - The interval_on figure (with multiple onsets + mean) 
      - The interval_off figure (with multiple offsets + mean)
    The window for the epoch plots is from -before to +after.
    """
    fig = go.Figure(layout_yaxis_range=[-5, 5])
    interval_on = go.Figure(layout_yaxis_range=[-4, 4])
    interval_off = go.Figure(layout_yaxis_range=[-4, 4])
    avg_change = go.Figure()
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
        x=[None], y=[None], mode='markers', name=f'freezing bouts > {after}s', 
        marker=dict(color='blue', size=7, symbol='square', opacity=0.2)
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers', name=f'freezing bouts < {after}s', 
        marker=dict(color='lightblue', size=7, symbol='square', opacity=0.3)
    ))
    
    # Highlight intervals in the full figure
    for on, off in intervals:
        on_sec = on / fps
        off_sec = off / fps
        fig.add_vrect(x0=on_sec, x1=off_sec, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
    
    # Now build the interval_on and interval_off figures
    aggregate_on = []
    aggregate_off = []
    
    for i, inter in enumerate(epochs_acc_on):
        x_epoch = np.arange(-before, after, 1 / fps)
        y_epoch = inter[2]
        interval_on.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'onset {i+1}', mode='lines', 
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_on.append(y_epoch)
        fig.add_vrect(
            x0=inter[1][0] / fps, x1=inter[1][1] / fps, fillcolor='blue', opacity=0.2, layer='below', line_width=0
        )
    
    for i, inter in enumerate(epochs_acc_off):
        x_epoch = np.arange(-before, after, 1 / fps)
        y_epoch = inter[2]
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'offset {i+1}', mode='lines', 
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_off.append(y_epoch)
    
    # Compute mean & std for onsets
    aggregate_on = np.array(aggregate_on)
    if len(aggregate_on) > 0:
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
        interval_on.add_vrect(x0=0, x1=after, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # Compute mean & std for offsets
    aggregate_off = np.array(aggregate_off)
    if len(aggregate_off) > 0:
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
        interval_off.add_vrect(x0=-before, x1=0, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # Bar plot for the zdFF change
    if avg_on and avg_off:
        avg_change.add_trace(go.Scatter(
            x=np.ones_like(avg_on[:2]),
            y=avg_on[:2],
            marker_color='blue'
        ))
        avg_change.add_trace(go.Scatter(
            x=np.ones_like(avg_off[:2]) * 2,
            y=avg_off[:2],
            marker_color='lightblue'
        ))
        avg_change.update_layout(title=f'{name} zdFF Change', xaxis_title='Epoch', yaxis_title='zdFF')
    
    interval_on.update_layout(
        title='Signal around event onset',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    interval_off.update_layout(
        title='Signal around event offset',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )
    
    return fig, interval_on, interval_off, avg_change

#
# MAIN CALLBACK: Renders the layout for either "Averaged Data" or a specific mouse
#                and uses the user-provided "seconds-before" and "seconds-after" to define the epoch window.
#
@app.callback(
    Output('tab-content', 'children'),
    [Input('mouse-dropdown', 'value'),
     Input('seconds-before', 'value'),
     Input('seconds-after', 'value')]
)
def update_tab(selected_value, seconds_before, seconds_after):
    """
    If "Averaged Data" is selected, generate the aggregated plots with the chosen epoch window.
    Otherwise, show single-mouse plots with that same epoch window.
    """
    if not selected_value:
        return "No data available."
    
    if selected_value == "average":
        acc_on_all = []
        acc_off_all = []
        adn_on_all = []
        adn_off_all = []
        fps = None
        
        for mouse, merged in mouse_data.items():
            intervals = merged.get_freezing_intervals()
            if fps is None:
                fps = merged.fps
            acc_epochs_on = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after)
            acc_epochs_off = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off')
            adn_epochs_on = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after)
            adn_epochs_off = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off')
            
            for epoch in acc_epochs_on:
                acc_on_all.append(epoch[2])
            for epoch in acc_epochs_off:
                acc_off_all.append(epoch[2])
            for epoch in adn_epochs_on:
                adn_on_all.append(epoch[2])
            for epoch in adn_epochs_off:
                adn_off_all.append(epoch[2])
        
        # Build four average figures: ACC Onset, ACC Offset, ADN Onset, ADN Offset
        acc_on_fig, acc_off_fig = generate_average_plot("ACC", acc_on_all, acc_off_all, seconds_before, seconds_after, fps)
        adn_on_fig, adn_off_fig = generate_average_plot("ADN", adn_on_all, adn_off_all, seconds_before, seconds_after, fps)
        
        content = html.Div([
            html.Div([
                dcc.Graph(id='accavgon', figure=acc_on_fig),
                dcc.Graph(id='adnavgon', figure=adn_on_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Div([
                dcc.Graph(id='accavgoff', figure=acc_off_fig),
                dcc.Graph(id='adnavgoff', figure=adn_off_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
            
            # Color picker for the average tab
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
                    value={'rgb': dict(r=0, g=0, b=255, a=0)}  # default color
                )
            ], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'})
        ])
        return content
    
    else:
        if selected_value not in mouse_data:
            return "No data available."
        
        merged = mouse_data[selected_value]
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
            
            # Optionally, include your color picker sections here
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

#
# SINGLE-MOUSE: Dynamic trace dropdowns for ACC & ADN
#
@app.callback(
    [Output('acc-trace-dropdown', 'options'),
     Output('acc-trace-dropdown', 'value')],
    Input('acc-plot-dropdown', 'value'),
    [State('acc', 'figure'),
     State('accintervalon', 'figure'),
     State('accintervaloff', 'figure')]
)
def update_acc_trace_dropdown(selected_plot, full_fig, interval_on_fig, interval_off_fig):
    if selected_plot == 'full':
        fig = full_fig
    elif selected_plot == 'interval_on':
        fig = interval_on_fig
    else:
        fig = interval_off_fig
    
    if not fig or 'data' not in fig:
        return [], None
    
    options = []
    for trace in fig['data']:
        tname = trace.get('name', None)
        if tname:
            options.append({'label': tname, 'value': tname})
    default_val = options[0]['value'] if options else None
    return options, default_val

@app.callback(
    [Output('adn-trace-dropdown', 'options'),
     Output('adn-trace-dropdown', 'value')],
    Input('adn-plot-dropdown', 'value'),
    [State('adn', 'figure'),
     State('adnintervalon', 'figure'),
     State('adnintervaloff', 'figure')]
)
def update_adn_trace_dropdown(selected_plot, full_fig, interval_on_fig, interval_off_fig):
    if selected_plot == 'full':
        fig = full_fig
    elif selected_plot == 'interval_on':
        fig = interval_on_fig
    else:
        fig = interval_off_fig
    
    if not fig or 'data' not in fig:
        return [], None
    
    options = []
    for trace in fig['data']:
        tname = trace.get('name', None)
        if tname:
            options.append({'label': tname, 'value': tname})
    default_val = options[0]['value'] if options else None
    return options, default_val


#
# SINGLE-MOUSE: Color picker callbacks for ACC & ADN
#
@app.callback(
    [Output('acc', 'figure'),
     Output('accintervalon', 'figure'),
     Output('accintervaloff', 'figure')],
    [Input('acc-color-picker', 'value'),
     Input('acc-plot-dropdown', 'value'),
     Input('acc-trace-dropdown', 'value')],
    [State('acc', 'figure'),
     State('accintervalon', 'figure'),
     State('accintervaloff', 'figure')]
)
def update_acc_color(color_value, selected_plot, selected_trace, full_fig, interval_on_fig, interval_off_fig):
    updated_full = full_fig.copy() if full_fig else {}
    updated_on = interval_on_fig.copy() if interval_on_fig else {}
    updated_off = interval_off_fig.copy() if interval_off_fig else {}
    
    if not selected_trace or not color_value:
        return updated_full, updated_on, updated_off

    if selected_plot == 'full' and 'data' in updated_full:
        for trace in updated_full['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']
    
    elif selected_plot == 'interval_on' and 'data' in updated_on:
        for trace in updated_on['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']
    
    elif selected_plot == 'interval_off' and 'data' in updated_off:
        for trace in updated_off['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']
    
    return updated_full, updated_on, updated_off

@app.callback(
    [Output('adn', 'figure'),
     Output('adnintervalon', 'figure'),
     Output('adnintervaloff', 'figure')],
    [Input('adn-color-picker', 'value'),
     Input('adn-plot-dropdown', 'value'),
     Input('adn-trace-dropdown', 'value')],
    [State('adn', 'figure'),
     State('adnintervalon', 'figure'),
     State('adnintervaloff', 'figure')]
)
def update_adn_color(color_value, selected_plot, selected_trace, full_fig, interval_on_fig, interval_off_fig):
    updated_full = full_fig.copy() if full_fig else {}
    updated_on = interval_on_fig.copy() if interval_on_fig else {}
    updated_off = interval_off_fig.copy() if interval_off_fig else {}
    
    if not selected_trace or not color_value:
        return updated_full, updated_on, updated_off

    if selected_plot == 'full' and 'data' in updated_full:
        for trace in updated_full['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']
    
    elif selected_plot == 'interval_on' and 'data' in updated_on:
        for trace in updated_on['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']
    
    elif selected_plot == 'interval_off' and 'data' in updated_off:
        for trace in updated_off['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']
    
    return updated_full, updated_on, updated_off

#
# AVERAGE TAB: Dynamic trace dropdown & color callback
#
@app.callback(
    [Output('average-trace-dropdown', 'options'),
     Output('average-trace-dropdown', 'value')],
    Input('average-plot-dropdown', 'value'),
    [State('accavgon', 'figure'),
     State('accavgoff', 'figure'),
     State('adnavgon', 'figure'),
     State('adnavgoff', 'figure')]
)
def update_average_trace_dropdown(selected_plot, accavgon_fig, accavgoff_fig, adnavgon_fig, adnavgoff_fig):
    if selected_plot == 'accavgon':
        fig = accavgon_fig
    elif selected_plot == 'accavgoff':
        fig = accavgoff_fig
    elif selected_plot == 'adnavgon':
        fig = adnavgon_fig
    else:
        fig = adnavgoff_fig
    
    if not fig or 'data' not in fig:
        return [], None
    
    options = []
    for trace in fig['data']:
        tname = trace.get('name', None)
        if tname:
            options.append({'label': tname, 'value': tname})
    default_val = options[0]['value'] if options else None
    return options, default_val

@app.callback(
    [Output('accavgon', 'figure'),
     Output('accavgoff', 'figure'),
     Output('adnavgon', 'figure'),
     Output('adnavgoff', 'figure')],
    [Input('average-color-picker', 'value'),
     Input('average-plot-dropdown', 'value'),
     Input('average-trace-dropdown', 'value')],
    [State('accavgon', 'figure'),
     State('accavgoff', 'figure'),
     State('adnavgon', 'figure'),
     State('adnavgoff', 'figure')]
)
def update_average_color(color_value, selected_plot, selected_trace,
                         accavgon_fig, accavgoff_fig, adnavgon_fig, adnavgoff_fig):
    updated_acc_on = accavgon_fig.copy() if accavgon_fig else {}
    updated_acc_off = accavgoff_fig.copy() if accavgoff_fig else {}
    updated_adn_on = adnavgon_fig.copy() if adnavgon_fig else {}
    updated_adn_off = adnavgoff_fig.copy() if adnavgoff_fig else {}
    
    if not selected_trace or not color_value:
        return updated_acc_on, updated_acc_off, updated_adn_on, updated_adn_off

    if selected_plot == 'accavgon' and 'data' in updated_acc_on:
        for trace in updated_acc_on['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']

    elif selected_plot == 'accavgoff' and 'data' in updated_acc_off:
        for trace in updated_acc_off['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']

    elif selected_plot == 'adnavgon' and 'data' in updated_adn_on:
        for trace in updated_adn_on['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']

    elif selected_plot == 'adnavgoff' and 'data' in updated_adn_off:
        for trace in updated_adn_off['data']:
            if trace.get('name') == selected_trace:
                if 'line' in trace:
                    trace['line']['color'] = color_value['hex']

    return updated_acc_on, updated_acc_off, updated_adn_on, updated_adn_off

# Callback to print the selected group
@app.callback(
    Output('group-dropdown', 'value'),
    Input('group-dropdown', 'value')
)
def print_selected_group(selected_group):
    print(f"Selected group: {selected_group}")
    return selected_group

# Callback to update the app state
@app.callback(
    Output('app-state', 'data'),
    [Input('mouse-dropdown', 'value'),
     Input('group-dropdown', 'value')],
    State('app-state', 'data')
)
def update_app_state(selected_mouse, selected_group, data):
    print(data)
    if data is None:
        data = {
            'selected_mouse': None,
            'selected_group': {}
            }
    data['selected_mouse'] = selected_mouse
    data['selected_group'][selected_mouse] = selected_group
    print(f"Updated app state: {data}")
    return data

if __name__ == '__main__':
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)