import dash
from dash import dcc, html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Fresh Dash Test Page"),
    html.P("If you see this, Dash is working!")
])

if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)