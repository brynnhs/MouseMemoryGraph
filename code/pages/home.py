import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
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
])