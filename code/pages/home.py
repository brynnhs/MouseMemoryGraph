import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_table
from dash_local_react_components import load_react_component

dash.register_page(__name__, path='/')
app = dash.get_app()

# Load the EventSelection React component globally
EventSelection = load_react_component(app, "components", "EventSelection.js")

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='selected-event', data=None),  # Store to hold the currently selected event
    dcc.Store(id='hidden-event-store', data={}),  # Store to hold all events and their intervals
    html.Div([
        html.H1("Welcome to the Mouse Memory Graph App"),
        html.P("This is the homepage of the app. Use the dropdown menu to navigate to different mouse data pages."),
        html.H2("Expected Folder Structure"),
        html.Pre("""
        data/
        ├── mouse1/
        │   ├── mouse1.csv
        │   └── Behavior.csv
        ├── mouse2/
        │   ├── mouse2.csv
        │   └── Behavior.csv
        └── ...
        """)
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'padding': '10px',
        'margin': '10px 0'
    }),
    html.Div([
        dcc.Input(
            id='input-path',
            type='text',
            persistence=True,
            placeholder='Enter folder path',
            style={
                'width': '80%',
                'height': '40px',
                'lineHeight': '40px',
                'borderWidth': '1px',
                'borderStyle': 'solid',
                'borderRadius': '10px',
                'marginRight': '10px',
                'padding': '0 10px'
            }
        ),
        html.Button(
            'Process',
            id='submit-path',
            n_clicks=0,
            style={
                'height': '40px',
                'lineHeight': '40px',
                'borderWidth': '1px',
                'borderStyle': 'solid',
                'borderRadius': '10px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'padding': '0 20px'
            }
        )
    ], style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '10px',
        'textAlign': 'center',
        'margin': '10px 0',
        'backgroundColor': 'white'
    }),
    dcc.Loading(
        type="circle",
        children=[
        html.Div([
            EventSelection(id='event-selection'),
            html.Div(id='selected-event-output', style={'margin': '10px 0'}),
            html.Button(
                'Add Interval',
                id='add-interval',
                disabled=True,
                n_clicks=0,
                className='button-disabled' if True else 'button-enabled',  # Default to disabled
                style={
                    'height': '40px',
                    'lineHeight': '40px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '10px',
                    'padding': '0 20px'
                }
            ),
            html.Button(
                'Save Event',
                id='save-event',
                n_clicks=0,
                style={
                    'height': '40px',
                    'lineHeight': '40px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '10px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'padding': '0 20px'
                })
        ], style={
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'padding': '10px',
            'margin': '10px 0'
        })])
], style={'padding': '20px'})


@app.callback(
    [Output('selected-event', 'data'),
     Output('add-interval', 'disabled'),
     Output('add-interval', 'className')],
    [Input('event-selection', 'value')],
    prevent_initial_call=True
)
def update_event_store(selected_event):
    if selected_event:
        return selected_event, False, 'button-enabled'
    return None, True, 'button-disabled'

@app.callback(
    [Output('selected-event-output', 'children'),
     Output('add-interval', 'n_clicks'),
     Output('hidden-event-store', 'data', allow_duplicate=True)],
    [Input('selected-event', 'data'),
     Input('add-interval', 'n_clicks'),
     Input('hidden-event-store', 'data')],
     State('event-store', 'data'),
     prevent_initial_call=True
)
def update_selected_event_output(selected_event, n_clicks, hidden_event_store, event_store):
        # update hidden-event-store with event-store
        #if event_store:
        #    for key, value in event_store.items():
        #        hidden_event_store[key] = value
        if not selected_event:
            return 'No event selected', 0, hidden_event_store
        if selected_event in hidden_event_store.keys():
            data = hidden_event_store[selected_event]
        else:
            data = [(0, 0)]

        if n_clicks:
            data.append((0, 0))

        hidden_event_store[selected_event] = data

        return dash_table.DataTable(
            id='interval-table',
            columns=[
                {'name': 'Start Time (s)', 'id': 'start', 'type': 'numeric'},
                {'name': 'End Time (s)', 'id': 'end', 'type': 'numeric'}
            ],
            editable=True,
            row_deletable=True,
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'border': '1px solid #ccc'
            },
            style_header={
                'fontFamily': 'Arial, sans-serif',
                'backgroundColor': '#f4f4f4',
                'fontWeight': 'bold',
                'border': '1px solid #ccc',
            },
            style_data={
                'fontFamily': 'Arial, sans-serif',  # Set the default font
                'fontSize': '14px'  # Optional: Set a default font size
            },
            style_data_conditional=[
                {
                    'if': {'state': 'active'},  # When a cell is active
                    'backgroundColor': 'inherit',  # Keep the background color unchanged
                    'border': '3px solid #ccc'  # Keep the border consistent
                },
                {
                    'if': {'state': 'selected'},  # When a cell is selected
                    'backgroundColor': 'inherit',  # Keep the background color unchanged
                    'border': '3px solid #ccc'  # Keep the border consistent
                }
            ],
            style_as_list_view=True,
            data=data
        ), 0, hidden_event_store

@app.callback(
    Output('hidden-event-store', 'data', allow_duplicate=True),
    Input('interval-table', 'data'),
    [State('selected-event', 'data'), 
     State('hidden-event-store', 'data')],
    prevent_initial_call=True
)
def update_interval_table(interval_data, selected_event, event_store):
    if selected_event and interval_data:
        # Ensure selected_event is valid before updating event_store
        if selected_event not in [None, 'null']:
            event_store[selected_event] = interval_data
    return event_store

@app.callback(
    Output('hidden-event-store', 'data'),
    Input('url', 'pathname'),  # Trigger on page load
    State('event-store', 'data')
)
def sync_hidden_event_store_on_load(pathname, event_store):
    if pathname == '/':  # Ensure this only runs on the home page
        if event_store:
            return event_store  # Synchronize hidden-event-store with event-store
    return dash.no_update  # Prevent unnecessary updates

@app.callback(
    [Output('event-store', 'data'),
     Output('save-event', 'n_clicks')],
    [Input('save-event', 'n_clicks'),
     Input('hidden-event-store', 'data')],
     [State('event-store', 'data')],
    prevent_initial_call=True
)
def save_event(n_clicks, hidden_event_store, event_store):
    # Normalize the dictionaries for comparison
    def normalize_dict(d):
        return {k: sorted(v, key=lambda x: tuple(sorted(x.items()))) for k, v in d.items()}

    normalized_hidden = normalize_dict(hidden_event_store)
    normalized_event = normalize_dict(event_store)
    if normalized_hidden == normalized_event:
        return dash.no_update, 0  # Prevent unnecessary updates

    if n_clicks:
        if hidden_event_store == {}:
            return dash.no_update, 0
        event_store.update(hidden_event_store)
    else:
        return dash.no_update, 0
    
    return event_store, 0

# Callback to populate EventSelection options from event-store
@app.callback(
    Output('event-selection', 'options'),
    [Input('hidden-event-store', 'data'),
     Input('event-store', 'data'),
     Input('selected-event', 'data')]
)
def populate_event_selection_options(hidden_event_store, event_store, selected_event):
    if event_store:
        # Filter out 'null' and convert event-store keys to dropdown options
        return [{'label': key, 'value': key, 'text': key} for key in event_store.keys() if key != 'null']
    elif hidden_event_store:
        return [{'label': key, 'value': key, 'text': key} for key in hidden_event_store.keys() if key != 'null']
    return []

@app.callback(
    Output('selected-folder', 'data'),
    [Input('submit-path', 'n_clicks')],
     [State('input-path', 'value'),
      State('selected-folder', 'data')],
)
def update_selected_folder(n_clicks, input, selected_folder):
    print(f"input: {input}, selected_folder: {selected_folder}")
    if input == selected_folder:
        return dash.no_update
    return input