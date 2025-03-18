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

from utils import load_assignments, save_assignments
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

# Global container for mouse condition assignments
mouse_assignments = load_assignments()

dash.register_page(__name__, path_template='/mouse/<id>')
app = dash.get_app()

# Determine the base path (works both for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))


# Load the GroupDropdown React component globally
GroupDropdown = load_react_component(app, "components", "GroupDropdown.js")
EventRender = load_react_component(app, "components", "EventRender.js")

# Cache for data loading
@lru_cache(maxsize=10)
def load_raw_data(
    data_dir, 
    mouse, 
    events=None
    ):
    """Load raw merged data for a specific mouse and cache the result."""
    # Convert events dictionary to a hashable type (tuple of sorted key-value pairs)
    events = tuple(sorted(events.items())) if events else None

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
        if events:
            for name, intervals in dict(events).items():  # Convert back to dict for processing
                merged.add_event(name, intervals)
        return merged.to_dict()
    return None

def layout(
        id=None, 
        **other_unknown_query_strings
        ):
    mouse = id
    return html.Div([
        html.Div([
        dcc.Location(id='url'),
        html.H2(f'Mouse {mouse}'),
        html.Div([
            html.Div([
                GroupDropdown(id='group-dropdown', value=1)
            ], style={'margin-bottom': '10px'}),
            html.Div([
                html.Label("Filter out epochs:"),
                daq.BooleanSwitch(id='boolean-switch', on=True, color='lightblue'),
                html.Div(id='boolean-switch-output')
            ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            html.Div([EventRender(id='event-selection-mouse', value='freezing')], style={'margin-bottom': '10px'}),
            html.Div([
                html.Label("Seconds Before Event:"),
                dcc.Input(
                    id="seconds-before",
                    type="number",
                    placeholder="Enter seconds before (e.g. 2)",
                    value=2,
                    style={'margin-left': '10px', 'margin-right': '20px'}
                ),
            ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            html.Div([
                html.Label("Seconds After Event:"),
                dcc.Input(
                    id="seconds-after",
                    type="number",
                    placeholder="Enter seconds after (e.g. 2)",
                    value=2,
                    style={'margin-left': '10px'}
                ),
            ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            # Axis Step Settings
                 html.Div([
                     html.Label("X-Axis Step:"),
                     dcc.Input(
                         id="x-axis-step",
                         type="number",
                         placeholder="X-Axis Step",
                         value=None,
                         style={'margin-left': '10px', 'margin-right': '20px'}
                     ),
                     html.Label("Y-Axis Step:"),
                     dcc.Input(
                         id="y-axis-step",
                         type="number",
                         placeholder="Y-Axis Step",
                         value=None,
                         style={'margin-left': '10px'}
                     )
                 ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
                 # Graph and Axis Titles
                 html.Div([
                     html.Label("Graph Title:"),
                     dcc.Input(
                         id="graph-title",
                         type="text",
                         placeholder="Enter graph title",
                         value=None,
                         style={'margin-left': '10px', 'margin-right': '20px'}
                     ),
                     html.Label("X-Axis Title:"),
                     dcc.Input(
                         id="x-axis-title",
                         type="text",
                         placeholder="Enter x-axis title",
                         value=None,
                         style={'margin-left': '10px', 'margin-right': '20px'}
                     ),
                     html.Label("Y-Axis Title:"),
                     dcc.Input(
                         id="y-axis-title",
                         type="text",
                         placeholder="Enter y-axis title",
                         value=None,
                         style={'margin-left': '10px'}
                     )
                 ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'})
        ], style={
            'display': 'flex', 
            'flex-direction': 'row', 
            'align-items': 'center',
            'justify-content': 'space-around', 
            'margin-bottom': '20px',
            'background-color': 'white',
            'border-radius': '10px',
            'padding': '20px'
        }),
        ], style={'align-items': 'center', 'justify-content': 'center'}),
        html.Div(id='mouse-content')
    ])

# Callback to populate EventSelection options from event-store
@app.callback(
    Output('event-selection-mouse', 'options'),
    [Input('event-store', 'data')]
)
def populate_event_selection_options(
    event_store
    ):
    if event_store:
        # Convert event-store keys to dropdown options
        options = list(event_store.keys())
    else:
        options = []
    return [{'label': key, 'value': key, 'text': key} for key in options]

@callback(
    Output('mouse-data-store', 'data'),
    [Input('mouse-data-store', 'data'), 
     Input('url', 'pathname'), 
     Input('selected-folder', 'data'), 
     Input('event-store', 'data')]
)
def load_mouse_data(
    data, 
    pathname, 
    folder, 
    events
    ):
    mouse = pathname.split('/')[-1]
    if not data:
        data = {}

    # Safely convert events to a hashable type
    try:
        events_hashable = tuple(sorted(events.items())) if isinstance(events, dict) else None
    except AttributeError:
        events_hashable = None

    # Check if data[mouse] exists and is not None before accessing its attributes
    if mouse in data.keys() and data[mouse] is not None and events_hashable == data[mouse].get('events'):
        print('Found mouse data in store:', mouse)
        return data
    else:
        print('load_mouse_data', pathname, folder)
        mouse_data = load_raw_data(folder, mouse, events_hashable)
        data[mouse] = mouse_data
        return data

@callback(
    Output('mouse-content', 'children'),
    [Input('mouse-data-store', 'data'),
     Input('seconds-before', 'value'),
     Input('seconds-after', 'value'),
     Input('url', 'pathname'),
     Input('boolean-switch', 'on'),
     Input('event-selection-mouse', 'value'),
     Input('x-axis-step', 'value'),
     Input('y-axis-step', 'value'),
     Input('graph-title', 'value'),
     Input('x-axis-title', 'value'),
     Input('y-axis-title', 'value')],
)

def update_graph(
     mouse_data, 
     seconds_before, 
     seconds_after, 
     pathname, 
     on, 
     selected_event,
     x_axis_step,
     y_axis_step,
     graph_title,
     x_axis_title,
     y_axis_title
    ):

    if not mouse_data:
            return "No data available."
    print('selected_event:', selected_event)
    mouse = pathname.split('/')[-1]
    mouse_data = mouse_data[mouse]
    merged = MergeDatasets.from_dict(mouse_data)
    fps = merged.fps
    
    # Precompute intervals and epochs
    intervals = merged.get_freezing_intervals() if selected_event == 'freezing' else merged.get_freezing_intervals(0, selected_event)
    freezing_intervals = merged.get_freezing_intervals()
    epoch_data = {
        'ACC': {
            'on': merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, filter=on),
            'off': merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off', filter=on)
        },
        'ADN': {
            'on': merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, filter=on),
            'off': merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off', filter=on)
        }
    }

    # Use ThreadPoolExecutor for parallel figure generation
    with ThreadPoolExecutor() as executor:
        acc_future = executor.submit(generate_plots, merged, merged.df, freezing_intervals, fps, seconds_before, seconds_after,
                                     epoch_data['ACC']['on'], epoch_data['ACC']['off'],
                                     merged.get_epoch_average(intervals, 'ACC', before=seconds_before, after=seconds_after, filter=on),
                                     merged.get_epoch_average(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off', filter=on),
                                     selected_event,
                                     name='ACC')
        adn_future = executor.submit(generate_plots, merged, merged.df, freezing_intervals, fps, seconds_before, seconds_after,
                                     epoch_data['ADN']['on'], epoch_data['ADN']['off'],
                                     merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after, filter=on),
                                     merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off', filter=on),
                                     selected_event,
                                     name='ADN')

        acc_full, acc_interval_on, acc_interval_off, acc_change = acc_future.result()
        adn_full, adn_interval_on, adn_interval_off, adn_change = adn_future.result()

    # Update axis steps and layout titles for all figures (not x axis for bar plots)
    figure_list = [
        acc_full, acc_interval_on, acc_interval_off, 
        adn_full, adn_interval_on, adn_interval_off, 
    ]
    for fig in figure_list:
        if x_axis_step:
            fig.update_xaxes(dtick=x_axis_step)
    
    figure_list = figure_list + [acc_change, adn_change]
    
    for fig in figure_list:
        if y_axis_step:
            fig.update_yaxes(dtick=y_axis_step)
        if graph_title:
            fig.update_layout(title=graph_title)
        if x_axis_title:
            fig.update_layout(xaxis_title=x_axis_title)
        if y_axis_title:    
            fig.update_layout(yaxis_title=y_axis_title)
    
    
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
        ], style={
            'margin-bottom': '40px',
            'background-color': 'white',
            'border-radius': '10px'}
        ),
        
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
        ], style={
            'margin-bottom': '40px',
            'background-color': 'white',
            'border-radius': '10px'}
        ),
        
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

# Combined callback for handling both dropdown changes and URL updates.
@app.callback(
    Output('group-dropdown', 'value'),
    [Input('group-dropdown', 'value'),
     Input('url', 'pathname')],
    [State('group-dropdown', 'value')]
)
def manage_mouse_assignment(
     new_value, 
     pathname, 
     current_value
    ):
    ctx = dash.callback_context
    if not ctx.triggered:
        # On initial load, use the stored assignment.
        mouse_id = pathname.split('/')[-1]
        return mouse_assignments.get(mouse_id, 'default_group')
    triggered_id = ctx.triggered[0]['prop_id']
    if triggered_id.startswith('group-dropdown'):
        # User changed the dropdown value.
        mouse_id = pathname.split('/')[-1]
        mouse_assignments[mouse_id] = new_value
        save_assignments(mouse_assignments)
        return new_value
    elif triggered_id.startswith('url'):
        # URL changed; load the saved assignment.
        mouse_id = pathname.split('/')[-1]
        return mouse_assignments.get(mouse_id, 'default_group')
    return current_value