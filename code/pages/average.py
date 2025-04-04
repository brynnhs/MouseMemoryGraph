import os
import sys
import dash
import dash_daq as daq
import numpy as np
import pandas as pd
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from code.dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
from dash_local_react_components import load_react_component
from dash import callback_context

# Import visualization functions
from code.visualize import generate_average_plot, generate_plots
# Import utility for condition assignments mapping (e.g., {'mouse1': 1, 'mouse2': 3, ...})
from code.utils import load_assignments

dash.register_page(__name__, path='/average')
app = dash.get_app()

color_map = {
    'Recent': '#FFB3BA',
    'Remote': '#FFDFBA',
    'Control': '#FFFFBA'
}

# Determine the base path
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

def load_raw_data(data_dir, mouse, events):
    """Load raw merged data for all mice and store in mouse_data."""
    mouse_data = {}
    photometry_path = os.path.join(data_dir, mouse, f"{mouse.split('_')[0]}_recording.csv.csv")
    behavior_path = os.path.join(data_dir, mouse, f"{mouse.split('_')[0]}_behavior.csv.csv")
    print('Loading data', mouse)
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
            # Ensure events are added only once
            added_events = set()
            for name, intervals in events.items():
                if name not in added_events:
                    merged.add_event(name, intervals)
                    added_events.add(name)
        return merged.to_dict()

# Load condition assignments mapping: mouse id -> condition group
condition_assignments = load_assignments()

# Load the GroupSelection component
GroupSelection = load_react_component(app, "components", "GroupSelection.js")
EventRender = load_react_component(app, "components", "EventRender.js")

layout = html.Div([
    dcc.Store(id='stored-figures', data={}),
    dcc.Store(id='color-overrides', data={}),
    # Include the group selection dropdown (MultiSelect)
    html.Div([
        GroupSelection(id='group-selection', value=[])  # Initially, no groups selected
    ], style={'width': '100%', 'text-align': 'left', 'margin-bottom': '20px'}),
    
    # Numeric inputs for the epoch window
    html.Div([
        html.Div([
            html.Label("Filter out epochs:"),
            daq.BooleanSwitch(id='boolean-switch', on=True, color='lightblue'),
            html.Div(id='boolean-switch-output')
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        html.Div([EventRender(id='event-selection-average', value='freezing')], style={'margin-bottom': '10px'}),
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
        # New: Axis Step Settings
         html.Div([
             html.Label("X-Axis Step:"),
             dcc.Input(
                 id="x-axis-step",
                 type="number",
                 placeholder="X-Axis Step",
                 min=0.05,
                 value=None,
                 style={'margin-left': '10px', 'margin-right': '20px'}
             ),
             html.Label("Y-Axis Step:"),
             dcc.Input(
                 id="y-axis-step",
                 type="number",
                 placeholder="Y-Axis Step",
                 min=0.05,
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
    html.Div(id='tab-content'),
    html.Div([
    html.H3("Averaged Data Color Settings"),
    dcc.Dropdown(
        id='average-plot-dropdown',
        options=[
            {'label': 'ACC Onset', 'value': 'accavgon'},
            {'label': 'ACC Offset', 'value': 'accavgoff'},
            {'label': 'ADN Onset', 'value': 'adnavgon'},
            {'label': 'ADN Offset', 'value': 'adnavgoff'},
            {'label': 'ACC Onset Change', 'value': 'accon_change'},
            {'label': 'ACC Offset Change', 'value': 'accoff_change'},
            {'label': 'ADN Onset Change', 'value': 'adnon_change'},
            {'label': 'ADN Offset Change', 'value': 'adnoff_change'}
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
        value={'rgb': dict(r=0, g=0, b=255, a=1)}
    )
], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'}),
])

# Callback to populate EventSelection options from event-store
@app.callback(
    Output('event-selection-average', 'options'),
    [Input('event-store', 'data')],
    [State('event-colors', 'data')]
)
def populate_event_selection_options(
    event_store,
    event_colors
    ):
    if event_store:
        # Convert event-store keys to dropdown options
        options = list(event_store.keys())
    else:
        options = []
    return [{'label': key, 'value': key, 'text': key, 'color': event_colors.get(key, None)
             } for key in options]

# Callback to populate GroupDropdown options from group-store
@app.callback(
    Output('group-selection', 'options'),
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
    return [{'key': key['group'], 'value': key['group'], 'text': key['group'], 'color': key['color']} for key in options]

@callback(
    Output('mouse-data-store', 'data'),
    [Input('selected-folder', 'data'), 
     Input('event-store', 'data'),
     Input('app-state', 'data')],
     [State('mouse-data-store', 'data')]
)

def load_mouse_data(folder, events, app_state, data):

    if not data:
        data = {}

    # Ensure app_state is not None
    if not app_state:
        return data
    # Ensure the callback only runs for the `/mouse/<id>` path
    mouse_data = app_state.get('mouse_data', {})

    for mouse in mouse_data:
        # Check if data[mouse] is None or if events do not match
        if mouse not in data.keys() or not data[mouse]: #or events != data[mouse].get('events', None):
            mouse_data = load_raw_data(folder, mouse, events)
            data[mouse] = mouse_data
        elif events and events != [] and events != {}:
            ctx = callback_context
            mouse_data = load_raw_data(folder, mouse, events)
            data[mouse] = mouse_data
        else:
            pass
    return data


@callback(
    Output('color-overrides', 'data'),
    [Input('average-color-picker', 'value')],
    [State('average-plot-dropdown', 'value'),
     State('average-trace-dropdown', 'value'),
     State('color-overrides', 'data')],
)
def update_color_overrides(selected_color, selected_plot, selected_trace, color_overrides):
    """Update the color map with the selected color for a specific trace."""
    if not selected_plot or not selected_trace or not selected_color:
        return color_overrides

    if not color_overrides:
        color_overrides = {}

    # Convert RGB to HEX
    rgb = selected_color['rgb']
    hex_color = f"#{rgb['r']:02X}{rgb['g']:02X}{rgb['b']:02X}"

    # Store color override by trace name
    color_overrides[selected_trace] = hex_color

    print(f"Updated color overrides: {color_overrides}")

    # Return updated `color-overrides`
    return color_overrides

@callback(
    Output('average-trace-dropdown', 'options'),
    [Input('average-plot-dropdown', 'value')],
    [State('stored-figures', 'data')]
)
def update_trace_dropdown(selected_plot, stored_figures):
    """Update trace selection based on the selected graph."""
    if not selected_plot or not stored_figures:
        return []

    fig = stored_figures.get(selected_plot)
    if not fig or 'data' not in fig:
        return []

    # Extract trace names
    trace_options = [{'label': trace.get('name', 'Unnamed Trace'), 'value': trace.get('name', 'Unnamed Trace')}
                     for trace in fig['data'] if trace.get('name')]

    return trace_options if trace_options else [{'label': 'No traces available', 'value': 'None'}]

@callback(
    [Output('tab-content', 'children'),
    Output('stored-figures', 'data')],
    [Input('mouse-data-store', 'data'),
     Input('group-store', 'data'),
     Input('seconds-before', 'value'),
     Input('seconds-after', 'value'),
     Input('x-axis-step', 'value'),
     Input('y-axis-step', 'value'),
     Input('group-selection', 'value'),
     Input('boolean-switch', 'on'),
     Input('color-overrides', 'data'),
     Input('event-selection-average', 'value')],
     [State('event-colors', 'data')]
)
def update_graph(mouse_data, 
                 assignments,
                 seconds_before, 
                 seconds_after, 
                 x_axis_step,
                 y_axis_step,
                 selected_groups, 
                 on, 
                 color_overrides, 
                 selected_event,
                 event_colors):
    print(event_colors)
    for mouse, group in assignments.items():
        if group['group'] not in color_map.keys():
            color_map[group['group']] = group['color']
    assignments = {mouse: group['group'] for mouse, group in assignments.items()}

    # Default to all groups if none selected.
    if not selected_groups:
        selected_groups = []

    print('color overrides in update_graph is', color_overrides)
    if color_overrides is None:
        color_overrides = {}

    # Initialize dictionaries for each sensor and epoch type.
    acc_on_dict, acc_off_dict, adn_on_dict, adn_off_dict = {}, {}, {}, {}

    acc_avg_on_dict, acc_avg_off_dict, adn_avg_on_dict, adn_avg_off_dict = {}, {}, {}, {}

    fps = None

    # Process each mouse if its condition is selected.
    for mouse, merged in mouse_data.items():
        if merged is None or mouse not in assignments:
            continue
        mouse_group = assignments.get(mouse)
        merged = MergeDatasets.from_dict(merged)
        if mouse_group not in selected_groups:
            continue

        # Precompute intervals and epochs
        intervals = merged.get_freezing_intervals() if selected_event == 'freezing' else merged.get_freezing_intervals(0, selected_event)
        color = None if selected_event == 'freezing' else event_colors[selected_event]

        if fps is None:
            fps = merged.fps
        acc_epochs_on = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, type='on', filter=on)
        acc_epochs_off = merged.get_epoch_data(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off', filter=on)
        adn_epochs_on = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, type='on', filter=on)
        adn_epochs_off = merged.get_epoch_data(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off', filter=on)

        acc_avg_on = merged.get_epoch_average(intervals, 'ACC', before=seconds_before, after=seconds_after, filter=on)
        adn_avg_on = merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after, filter=on)
        acc_avg_off = merged.get_epoch_average(intervals, 'ACC', before=seconds_before, after=seconds_after, type='off', filter=on)
        adn_avg_off = merged.get_epoch_average(intervals, 'ADN', before=seconds_before, after=seconds_after, type='off', filter=on)
        
        # Append epochs to the proper group in the dictionaries.
        acc_on_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in acc_epochs_on])
        acc_off_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in acc_epochs_off])
        adn_on_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in adn_epochs_on])
        adn_off_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in adn_epochs_off])

        acc_avg_on_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in acc_avg_on])
        adn_avg_on_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in adn_avg_on])
        acc_avg_off_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in acc_avg_off])
        adn_avg_off_dict.setdefault(mouse_group, []).extend([epoch[2] for epoch in adn_avg_off])
    
    # If no data was collected, show a message.
    if fps is None:
        return html.Div("No data available for the selected condition groups."), {}
    
    # Generate the average plots using dictionaries.
    acc_on_fig, acc_off_fig, acc_on_change, acc_off_change = generate_average_plot("ACC", acc_on_dict, acc_off_dict, acc_avg_on_dict, acc_avg_off_dict, seconds_before, seconds_after, fps, color_map, color, color_overrides)
    adn_on_fig, adn_off_fig, adn_on_change, adn_off_change = generate_average_plot("ADN", adn_on_dict, adn_off_dict, adn_avg_on_dict, adn_avg_off_dict, seconds_before, seconds_after, fps, color_map, color, color_overrides)
    
    # Update axis tick step for all figures
    for fig in [acc_on_fig, acc_off_fig, adn_on_fig, adn_off_fig, acc_on_change, acc_off_change, adn_on_change, adn_off_change]:
        if x_axis_step:
            fig.update_xaxes(dtick=x_axis_step)
        if y_axis_step:
            fig.update_yaxes(dtick=y_axis_step)

    content = html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='accavgon', figure=acc_on_fig),
                dcc.Graph(id='adnavgon', figure=adn_on_fig),

            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top', }),
            html.Div([
                dcc.Graph(id='accavgoff', figure=acc_off_fig),
                dcc.Graph(id='adnavgoff', figure=adn_off_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top',}),
            html.Div([
                dcc.Graph(id='accon_change', figure=acc_on_change),
                dcc.Graph(id='adnon_change', figure=adn_on_change),
                
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top', }),
            html.Div([
                dcc.Graph(id='accoff_change', figure=acc_off_change),
                dcc.Graph(id='adnoff_change', figure=adn_off_change)
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top',}),
        ], style={'background-color': 'white', 'border-radius': '10px'}),
    ])

    figures_data = {
        'accavgon': acc_on_fig,
        'accavgoff': acc_off_fig,
        'adnavgon': adn_on_fig,
        'adnavgoff': adn_off_fig,
        'accon_change': acc_on_change,
        'adnon_change': adn_on_change,
        'accoff_change': acc_off_change,
        'adnoff_change': adn_off_change
    }
    return content, figures_data