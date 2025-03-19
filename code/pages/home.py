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
    dcc.Store(id='selected-event', data=None),  # Store to hold the currently selected event
    
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
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'padding': '10px',
        'margin': '10px 0'
    }),
], style={'padding': '20px'})


@app.callback(
    [Output('event-store', 'data', allow_duplicate=True),
     Output('selected-event', 'data'),
     Output('add-interval', 'disabled'),
     Output('add-interval', 'className')],
    [Input('event-selection', 'value')],
    [State('event-store', 'data')],
    prevent_initial_call=True
)
def update_event_store(selected_event, current_store):
    if selected_event:
        if not selected_event in current_store.keys():
            current_store[selected_event] = [(0, 0)]
        return current_store, selected_event, False, 'button-enabled'
    return current_store, None, True, 'button-disabled'

@app.callback(
    [Output('selected-event-output', 'children')],
    [Input('selected-event', 'data'),
     Input('add-interval', 'n_clicks')],
    [State('event-store', 'data')],
    prevent_initial_call=True
)
def update_selected_event_output(selected_event, n_clicks, event_store):
        data = event_store[selected_event]

        if n_clicks:
            data.append((0,0))
            event_store[selected_event] = data

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
            data=event_store[selected_event]
        ),

@app.callback(
    Output('event-store', 'data'),
    [Input('interval-table', 'data'),
     Input('selected-event', 'data')],
    [State('event-store', 'data')],
    prevent_initial_call=True
)
def update_interval_table(interval_data, selected_event, event_store):
    if selected_event and interval_data:
        event_store[selected_event] = interval_data
    return event_store  

# Callback to populate EventSelection options from event-store
@app.callback(
    Output('event-selection', 'options'),
    [Input('event-store', 'data')]
)
def populate_event_selection_options(event_store):
    if event_store:
        # Convert event-store keys to dropdown options
        return [{'label': key, 'value': key, 'text': key} for key in event_store.keys()]
    return []

@app.callback(
    Output('selected-folder', 'data'),
    [Input('submit-path', 'n_clicks'),
     Input('input-path', 'value')],
)
def update_selected_folder(n_clicks, input):
    return input