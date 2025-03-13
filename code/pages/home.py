import dash
from dash import html, dcc
from dash.dependencies import Input, Output

dash.register_page(__name__, path='/')
app = dash.get_app()

layout = html.Div([
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
            'Submit',
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
    ],style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '10px 0',
            'backgroundColor': 'white'
        }
    ),
    dcc.Store(id='selected-folder'),
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
    })
], style={'padding': '20px'})

@app.callback(
    Output('selected-folder', 'data'),
    [Input('submit-path', 'n_clicks'),
     Input('input-path', 'value')],
)
def update_selected_folder(n_clicks, input):
    return input
