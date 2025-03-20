import os
import sys
import time
import webbrowser
import dash
import random
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash_local_react_components import load_react_component

pastel_colors = [
    "#FFB3BA",  # Light Pink
    "#FFDFBA",  # Peach
    "#FFFFBA",  # Light Yellow
    "#BAFFC9",  # Mint Green
    "#BAE1FF",  # Light Blue
    "#D7BDE2",  # Lavender
    "#FAD7A0",  # Pastel Orange
    "#F5B7B1",  # Soft Coral
    "#AED6F1",  # Sky Blue
    "#A9DFBF",  # Pastel Green
    "#F9E79F",  # Pale Yellow
    "#F5CBA7",  # Apricot
    "#D2B4DE",  # Soft Purple
    "#A3E4D7",  # Aqua
    "#F7DC6F",  # Lemon
    "#F1948A",  # Salmon
    "#D5DBDB",  # Light Gray
    "#FADBD8",  # Blush
    "#D4E6F1",  # Powder Blue
    "#D6EAF8"   # Ice Blue
]

def get_color_hex(color_value):
    """
    Given a color value from a ColorPicker, returns a hex string.
    Expects either a dict with a 'hex' key or one with an 'rgb' key.
    """
    if isinstance(color_value, dict):
        if 'hex' in color_value:
            return color_value['hex']
        elif 'rgb' in color_value:
            rgb = color_value['rgb']
            return '#{:02x}{:02x}{:02x}'.format(rgb.get('r', 0), rgb.get('g', 0), rgb.get('b', 0))
    return color_value  # fallback if not a dict

# Determine the base path (works both for script and executable)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))


def load_raw_data(data_dir):
    """Load raw merged data for all mice and store in mouse_data."""
    mouse_data = {}
    group_store = {}
    _color = {}
    # Detect available mouse folders
    mouse_folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    for mouse in mouse_folders:
            mouse_data[mouse] = []
            if '_' in mouse:
                group = mouse.split('_')[-1]
                if group in _color.values():
                    color = _color[group]
                else:
                    # pick random color
                    color = random.choice(pastel_colors)
                    _color[group] = color
                group_store[mouse] = {'group': group, 'color': color}

    return mouse_data, group_store


app = dash.Dash(__name__, use_pages=True, assets_folder='../assets')

# Load the GroupDropdown React component globally
GroupDropdown = load_react_component(app, "components", "GroupDropdown.js")

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    # Header image
    html.Div([
        html.Img(src='/assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),
    
    # Mouse selection dropdown (global navigation)
    html.Div([
        dcc.Dropdown(
            id='mouse-dropdown',
            clearable=False,
            searchable=False,
            options=(
                [{"label": dcc.Link(children=[
                    html.Span([html.Img(src='/assets/home.png', style={'height': '20px', 'margin-right': '5px', 'vertical-align': 'middle'})]),
                    "Homepage"
                    ], href="/"), "value": "/"}]),
            value="/", 
            style={'width': '300px', 'margin': '0 auto'}
        )
    ], id='dropdown', style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px', 'margin-top': '20px'}),

    # Page container for multi-page routing
    dash.page_container,

    # Footer image
    html.Div([
        html.Img(src='assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'}),

    # Store component to persist state
    dcc.Store(id='app-state', data={}, storage_type='session'),
    dcc.Store(id='selected-folder', storage_type='session'),
    dcc.Store(id='mouse-data-store', storage_type='session'),
    dcc.Store(id='event-store', data={}, storage_type='session'),
    dcc.Store(id='event-colors', data={}, storage_type='session'),
    dcc.Store(id='group-store', data={}, storage_type='session'),
])

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            a {
                color: inherit;
                text-decoration: none;
            }
            .dash-dropdown .Select-menu-outer .VirtualizedSelectSelectedOption > a {
                pointer-events: none;
            }
            .dash-dropdown .Select-menu-outer .VirtualizedSelectOption > a {
                width: 100%;
                height: 100%;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

@app.callback(
    [Output('app-state', 'data'),
     Output('group-store', 'data', allow_duplicate=True),
     Output('submit-path', 'n_clicks')],
    [Input('submit-path', 'n_clicks')],
    [State('app-state', 'data'),
    State('input-path', 'value')],
    prevent_initial_call=True
)
def update_app_state(n_clicks, data, input_value):
    # if already data in the app state, return it
    if n_clicks > 0 and input_value:
        mouse_data, group_store = load_raw_data(input_value)
        return {'mouse_data': mouse_data}, group_store, 0
    elif data:
        if n_clicks > 0:
            return data, dash.no_update, 0
        return dash.no_update, dash.no_update, 0
    return {}, dash.no_update, 0

@app.callback(
    Output('mouse-dropdown', 'options'),
    Input('app-state', 'data')
)
def update_dropdown_options(data):
    if data:
        mouse_data = data.get('mouse_data', {})
        options = (
            [{"label": dcc.Link(children=[
                html.Span([html.Img(src='/assets/home.png', style={'height': '20px', 'margin-right': '5px', 'vertical-align': 'middle'})]),
                "Homepage"
                ], href="/"), "value": "/"}] +
            [{"label": dcc.Link(children=[
                html.Span([html.Img(src='/assets/average.png', style={'height': '20px', 'margin-right': '5px', 'vertical-align': 'middle'})]),
                "Grouped Data"
                ], href="/average"), "value": "/average"}] +
            [{"label": dcc.Link(children=[
                html.Span([html.Img(src='/assets/logo.png', style={'height': '20px', 'margin-right': '5px', 'vertical-align': 'middle'})]),
                "Mouse " + mouse
                ]
            , href=f'/mouse/{mouse}'), "value": f'/mouse/{mouse}'} for mouse in mouse_data]
        ) if mouse_data else [{"label": "No data available", "value": "None"}]
        return options
    return [{"label": "No data available", "value": "None"}]

@app.callback(
    Output('mouse-dropdown', 'value'),
    [Input('url', 'pathname')],
    [State('mouse-dropdown', 'options')]
)
def update_dropdown_value(pathname, options):
    values = [option['value'] for option in options]
    return pathname if pathname in values else "None"



if __name__ == '__main__':
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)