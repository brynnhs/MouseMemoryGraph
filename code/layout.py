from dash import html, dcc
from dash_local_react_components import load_react_component

def create_layout(app, mouse_data):
    # Load the custom React component for the group dropdown.
    GroupDropdown = load_react_component(app, "components", "GroupDropdown.js")
    
    # Prepare dropdown options based on available mouse_data.
    if mouse_data:
        options = [{"label": "Averaged Data", "value": "average"}] + [
            {"label": f"Mouse {mouse}", "value": mouse} for mouse in mouse_data
        ]
        default_value = "average"
    else:
        options = [{"label": "No data available", "value": "None"}]
        default_value = "None"
    
    layout = html.Div([
        # Header image
        html.Div([
            html.Img(src='assets/header.png', style={'width': '100%', 'height': 'auto'})
        ], style={'text-align': 'center', 'margin-bottom': '10px'}),
        
        # Mouse selection dropdown
        html.Div([
            dcc.Dropdown(
                id='mouse-dropdown',
                options=options,
                value=default_value,
                style={'width': '300px', 'margin': '0 auto'}
            )
        ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
        
        # Group dropdown using the custom React component
        html.Div([
            GroupDropdown(id='group-dropdown', value=1)
        ], style={'width': '100%', 'text-align': 'left', 'margin-bottom': '20px'}),
        
        # Numeric inputs for the epoch window
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
        
        # Main content area for graphs (populated by callbacks)
        html.Div(id='tab-content'),
        
        # Footer image
        html.Div([
            html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
        ], style={'text-align': 'center', 'margin-top': '10px'}),
        
        # Store component to persist state
        dcc.Store(id='app-state', storage_type='session')
    ])
    
    return layout