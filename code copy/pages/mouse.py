import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objs as go
import numpy as np

dash.register_page(__name__, path_template='/mouse/<id>')

layout = html.Div([
    html.H2('Mouse Dashboard'),
    dcc.Graph(id='mouse-graph'),
    dcc.Input(id='input-value', type='number', value=5),
    html.Button('Update Graph', id='update-button', n_clicks=0)
])

@callback(
    Output('mouse-graph', 'figure'),
    [Input('update-button', 'n_clicks')],
    [dash.dependencies.State('input-value', 'value')]
)
def update_graph(n_clicks, value):
    x = np.linspace(0, 10, 100)
    y = np.cos(x) * value
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))
    return fig