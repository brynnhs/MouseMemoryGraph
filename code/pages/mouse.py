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
from visualize import generate_plots, generate_separated_plot

from utils import load_assignments, save_assignments
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

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

    photometry_path = os.path.join(data_dir, mouse, f"{mouse}_recording.csv")
    behavior_path = os.path.join(data_dir, mouse, f"{mouse}_behavior.csv")
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
                GroupDropdown(id='group-dropdown', value='000000')
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
            'padding': '20px',
            'flex-wrap': 'wrap'
        }),
        ], style={'align-items': 'center', 'justify-content': 'center'}),
        # Add the loading spinner here
        dcc.Loading(
            id="loading-spinner",
            type="circle",  # Spinner type (circle, dot, etc.)
            children=html.Div(id='mouse-content'),  # Wrap the content in the loading spinner
            style={'margin-top': '20px'},
            overlay_style={'height': '500px'}
        )
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

# Callback to populate GroupDropdown options from group-store
@app.callback(
    Output('group-dropdown', 'options'),
    [Input('group-store', 'data')]
)
def populate_group_dropdown_options(
    group_store
    ):
    if group_store:
        # Convert group-store keys to dropdown options
        options = list(group_store.values())
    else:
        options = []
    return [{'label': key['group'], 'value': key['group'], 'text': key['group'], 'color': key['color']} for key in options]


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
     [State('event-colors', 'data')]
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
     y_axis_title,
     event_colors
    ):

    if not mouse_data:
            return "No data available."
    mouse = pathname.split('/')[-1]
    mouse_data = mouse_data[mouse]
    merged = MergeDatasets.from_dict(mouse_data)
    mergeddataset = merged.df
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
                                     event_colors,
                                     name='ACC')
        adn_future = executor.submit(generate_plots, merged, merged.df, freezing_intervals, fps, seconds_before, seconds_after,
                                     epoch_data['ADN']['on'], epoch_data['ADN']['off'],
                                     merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after, filter=on),
                                     merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off', filter=on),
                                     selected_event,
                                     event_colors,
                                     name='ADN')

        acc_full, acc_interval_on, acc_interval_off, acc_change = acc_future.result()
        adn_full, adn_interval_on, adn_interval_off, adn_change = adn_future.result()

    acc_separated = generate_separated_plot(merged, 'ACC', 200,
                                             merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, filter=on),
                                             mergeddataset, fps, freezing_intervals, seconds_after, selected_event, event_colors)
    adn_separated = generate_separated_plot(merged, 'ADN', 200,
                                             merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, filter=on),
                                             mergeddataset, fps, freezing_intervals, seconds_after, selected_event, event_colors)

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
            dcc.Graph(id='acc_separated', figure=acc_separated),
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
            dcc.Graph(id='adn_separated', figure=adn_separated),
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
        html.Div([
            # ACC Color Picker Section
            html.Div([
                html.H3("ACC Color Picker"),
                html.Label("Select Graph:"),
                dcc.Dropdown(
                    id='acc-graph-dropdown',
                    options=[
                        {'label': 'Full Signal', 'value': 'full'},
                        {'label': 'Interval On', 'value': 'interval_on'},
                        {'label': 'Interval Off', 'value': 'interval_off'},
                        {'label': 'Average Change', 'value': 'avg_change'},
                        {'label': 'Separated Plot', 'value': 'separated'},
                    ],
                    value='full',
                    placeholder="Select a graph"
                ),
                html.Br(),
                html.Label("Select Trace:"),
                dcc.Dropdown(
                    id='acc-trace-dropdown',
                    options=[],  # to be populated dynamically via callbacks
                    value=None,
                    placeholder="Select a trace"
                ),
                html.Br(),
                html.Label("Select Color:"),
                daq.ColorPicker(
                    id='acc-color-picker',
                    value={'rgb': {'r': 128, 'g': 128, 'b': 128, 'a': 1}}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'}),
            # ADN Color Picker Section
            html.Div([
                html.H3("ADN Color Picker"),
                html.Label("Select Graph:"),
                dcc.Dropdown(
                    id='adn-graph-dropdown',
                    options=[
                        {'label': 'Full Signal', 'value': 'full'},
                        {'label': 'Interval On', 'value': 'interval_on'},
                        {'label': 'Interval Off', 'value': 'interval_off'},
                        {'label': 'Average Change', 'value': 'avg_change'},
                        {'label': 'Separated Plot', 'value': 'separated'},
                    ],
                    value='full',
                    placeholder="Select a graph"
                ),
                html.Br(),
                html.Label("Select Trace:"),
                dcc.Dropdown(
                    id='adn-trace-dropdown',
                    options=[],  # to be populated dynamically via callbacks
                    value=None,
                    placeholder="Select a trace"
                ),
                html.Br(),
                html.Label("Select Color:"),
                daq.ColorPicker(
                    id='adn-color-picker',
                    value={'rgb': {'r': 128, 'g': 128, 'b': 128, 'a': 1}}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-around'})
    ], style={'display': 'flex', 'flex-direction': 'column'})
    
    return content

# Combined callback for handling both dropdown changes and URL updates.
@app.callback(
    Output('group-dropdown', 'value'),
    [Input('group-store', 'data'),
     Input('url', 'pathname')]
)
def manage_mouse_assignment(mouse_assignments, pathname):
    """
    Populate the dropdown with the stored assignment for the mouse when the page loads.
    """
    if not mouse_assignments:
        return None  # No assignment exists, so nothing is selected
    mouse_id = pathname.split('/')[-1]
    stored_assignment = mouse_assignments.get(mouse_id, {})
    return stored_assignment.get('group')  # Return the group if it exists, otherwise None

@app.callback(
    Output('group-store', 'data'),
    [Input('group-store', 'data'),
     Input('group-dropdown', 'value'),
     Input('group-dropdown', 'currentColor'),
     Input('url', 'pathname')],
)
def update_mouse_assignment(mouse_assignments, new_value, color, pathname):
    """
    Update the group-store with the selected group and color for the current mouse.
    """
    mouse_id = pathname.split('/')[-1]
    if not mouse_assignments:
        mouse_assignments = {}
    if new_value and color:  # Only update if a new value is selected
        mouse_assignments[mouse_id] = {'group': new_value, 'color': color}

    return mouse_assignments

@app.callback(
    Output('acc-trace-dropdown', 'options'),
    [
        Input('acc-graph-dropdown', 'value'),
        Input('acc', 'figure'),
        Input('accintervalon', 'figure'),
        Input('accintervaloff', 'figure'),
        Input('accchange', 'figure'),
        Input('acc_separated', 'figure')
    ]
)
def update_acc_trace_options(
    selected_graph,
    fig_full,
    fig_interval_on,
    fig_interval_off,
    fig_change,
    fig_separated
):
    """
    Decide which figure to pull trace data from based on selected_graph.
    Then create a list of options (label/value) from that figure's traces.
    """
    if selected_graph == 'full':
        fig = fig_full
    elif selected_graph == 'interval_on':
        fig = fig_interval_on
    elif selected_graph == 'interval_off':
        fig = fig_interval_off
    elif selected_graph == 'avg_change':
        fig = fig_change
    elif selected_graph == 'separated':
        fig = fig_separated
    else:
        fig = fig_full

    if not fig or 'data' not in fig:
        return []

    options = []
    for i, trace in enumerate(fig['data']):
        trace_name = trace.get('name', f"Trace {i+1}")
        options.append({'label': trace_name, 'value': i})
    return options


@app.callback(
    Output('adn-trace-dropdown', 'options'),
    [
        Input('adn-graph-dropdown', 'value'),
        Input('adn', 'figure'),
        Input('adnintervalon', 'figure'),
        Input('adnintervaloff', 'figure'),
        Input('adnchange', 'figure'),
        Input('adn_separated', 'figure')
    ]
)
def update_adn_trace_options(
    selected_graph,
    fig_full,
    fig_interval_on,
    fig_interval_off,
    fig_change,
    fig_separated
):
    shapes = None
    if selected_graph == 'full':
        fig = fig_full
        shapes = fig.get('layout', {}).get('shapes', [])
    elif selected_graph == 'interval_on':
        fig = fig_interval_on
    elif selected_graph == 'interval_off':
        fig = fig_interval_off
    elif selected_graph == 'avg_change':
        fig = fig_change
    elif selected_graph == 'separated':
        fig = fig_separated
    else:
        fig = fig_full

    if not fig or 'data' not in fig:
        return []

    options = []
    for i, trace in enumerate(fig['data']):
        trace_name = trace.get('name', f"Trace {i+1}")
        options.append({'label': trace_name, 'value': i})
    #if shapes:
    #    # get all unique names for shapes
    #    shape_names = set([shape.get('name', 'None') for shape in shapes])
    #    for i, shape_name in enumerate(shape_names):
    #        options.append({'label': f"{shape_name}", 'value': shape_name})

    return options


@app.callback(
    [
      Output('acc', 'figure'),
      Output('accintervalon', 'figure'),
      Output('accintervaloff', 'figure'),
      Output('accchange', 'figure'),
      Output('acc_separated', 'figure')
    ],
    [Input('acc-color-picker', 'value'),
     Input('acc-graph-dropdown', 'value'),
     Input('acc-trace-dropdown', 'value')],
    [
      State('acc', 'figure'),
      State('accintervalon', 'figure'),
      State('accintervaloff', 'figure'),
      State('accchange', 'figure'),
      State('acc_separated', 'figure')
    ]
)
def update_acc_color(color_value, selected_graph, selected_trace,
                     fig_full, fig_interval_on, fig_interval_off,
                     fig_change, fig_separated):
    if selected_trace is None or color_value is None:
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    rgb = color_value.get('rgb', {})
    r = rgb.get('r', 0)
    g = rgb.get('g', 0)
    b = rgb.get('b', 0)
    a = rgb.get('a', 1)
    new_color = f"rgba({r},{g},{b},{a})"

    if selected_graph == 'full':
        if fig_full and 'data' in fig_full and len(fig_full['data']) > selected_trace:
            if 'line' in fig_full['data'][selected_trace]:
                fig_full['data'][selected_trace]['line']['color'] = new_color
            else:
                fig_full['data'][selected_trace]['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'interval_on':
        if fig_interval_on and 'data' in fig_interval_on and len(fig_interval_on['data']) > selected_trace:
            if 'line' in fig_interval_on['data'][selected_trace]:
                fig_interval_on['data'][selected_trace]['line']['color'] = new_color
            else:
                fig_interval_on['data'][selected_trace]['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'interval_off':
        if fig_interval_off and 'data' in fig_interval_off and len(fig_interval_off['data']) > selected_trace:
            if 'line' in fig_interval_off['data'][selected_trace]:
                fig_interval_off['data'][selected_trace]['line']['color'] = new_color
            else:
                fig_interval_off['data'][selected_trace]['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'avg_change':
        if fig_change and 'data' in fig_change and len(fig_change['data']) > selected_trace:
            trace = fig_change['data'][selected_trace]
            if trace.get('type') == 'box':
                # Update both the marker (dots) and line (box outline) colors
                trace['marker']['color'] = new_color
                trace['line']['color'] = new_color
                # Set fillcolor to same hue but with a fixed alpha (e.g., 0.2)
                import re
                match = re.match(r"rgba\((\d+),(\d+),(\d+),([\d.]+)\)", new_color)
                if match:
                    r_val, g_val, b_val, alpha = match.groups()
                    fillcolor = f"rgba({r_val},{g_val},{b_val},0.2)"
                    trace['fillcolor'] = fillcolor
                else:
                    trace['fillcolor'] = new_color
            elif trace.get('type') in ['bar']:
                trace['marker']['color'] = new_color
            elif 'line' in trace:
                trace['line']['color'] = new_color
            elif 'marker' in trace:
                trace['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'separated':
        if fig_separated and 'data' in fig_separated and len(fig_separated['data']) > selected_trace:
            trace = fig_separated['data'][selected_trace]
            if 'line' in trace:
                trace['line']['color'] = new_color
            elif 'marker' in trace:
                trace['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    else:
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated


@app.callback(
    [
      Output('adn', 'figure'),
      Output('adnintervalon', 'figure'),
      Output('adnintervaloff', 'figure'),
      Output('adnchange', 'figure'),
      Output('adn_separated', 'figure')
    ],
    [Input('adn-color-picker', 'value'),
     Input('adn-graph-dropdown', 'value'),
     Input('adn-trace-dropdown', 'value')],
    [
      State('adn', 'figure'),
      State('adnintervalon', 'figure'),
      State('adnintervaloff', 'figure'),
      State('adnchange', 'figure'),
      State('adn_separated', 'figure')
    ]
)
def update_adn_color(color_value, selected_graph, selected_trace,
                     fig_full, fig_interval_on, fig_interval_off,
                     fig_change, fig_separated):
    if selected_trace is None or color_value is None:
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    rgb = color_value.get('rgb', {})
    r = rgb.get('r', 0)
    g = rgb.get('g', 0)
    b = rgb.get('b', 0)
    a = rgb.get('a', 1)
    new_color = f"rgba({r},{g},{b},{a})"

    if selected_graph == 'full':
        if type(selected_trace) == str:
            if fig_full and 'layout' in fig_full and 'shapes' in fig_full['layout']:
                for shape in fig_full['layout']['shapes']:
                    if shape.get('name') == selected_trace:
                        shape['line']['color'] = new_color
                        shape['fillcolor'] = new_color
        else:
            if fig_full and 'data' in fig_full and len(fig_full['data']) > selected_trace:
                if 'line' in fig_full['data'][selected_trace]:
                    fig_full['data'][selected_trace]['line']['color'] = new_color
                else:
                    fig_full['data'][selected_trace]['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'interval_on':
        if fig_interval_on and 'data' in fig_interval_on and len(fig_interval_on['data']) > selected_trace:
            if 'line' in fig_interval_on['data'][selected_trace]:
                fig_interval_on['data'][selected_trace]['line']['color'] = new_color
            else:
                fig_interval_on['data'][selected_trace]['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'interval_off':
        if fig_interval_off and 'data' in fig_interval_off and len(fig_interval_off['data']) > selected_trace:
            if 'line' in fig_interval_off['data'][selected_trace]:
                fig_interval_off['data'][selected_trace]['line']['color'] = new_color
            else:
                fig_interval_off['data'][selected_trace]['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'avg_change':
        if fig_change and 'data' in fig_change and len(fig_change['data']) > selected_trace:
            trace = fig_change['data'][selected_trace]
            if trace.get('type') == 'box':
                trace['marker']['color'] = new_color
                trace['line']['color'] = new_color
                import re
                match = re.match(r"rgba\((\d+),(\d+),(\d+),([\d.]+)\)", new_color)
                if match:
                    r_val, g_val, b_val, alpha = match.groups()
                    fillcolor = f"rgba({r_val},{g_val},{b_val},0.2)"
                    trace['fillcolor'] = fillcolor
                else:
                    trace['fillcolor'] = new_color
            elif trace.get('type') in ['bar']:
                trace['marker']['color'] = new_color
            elif 'line' in trace:
                trace['line']['color'] = new_color
            elif 'marker' in trace:
                trace['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    elif selected_graph == 'separated':
        if fig_separated and 'data' in fig_separated and len(fig_separated['data']) > selected_trace:
            trace = fig_separated['data'][selected_trace]
            if 'line' in trace:
                trace['line']['color'] = new_color
            elif 'marker' in trace:
                trace['marker']['color'] = new_color
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated

    else:
        return fig_full, fig_interval_on, fig_interval_off, fig_change, fig_separated