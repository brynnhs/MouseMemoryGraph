import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import io
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets

app = dash.Dash(__name__)

# Store uploaded data globally
uploaded_photometry_df = None

def empty_figure():
    return go.Figure()

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))

app.layout = html.Div([
    html.Div([
        html.H4("Upload Photometry Data"),
        dcc.Upload(
            id='upload-photometry',
            children=html.Button('Upload CSV File'),
            multiple=False,
        ),
        html.Div(id='photometry-filename', style={'margin-top': '10px'}),

        html.H4("Upload Behavioral Data"),
        dcc.Upload(
            id='upload-behavior',
            children=html.Button('Upload CSV File'),
            multiple=False,
        ),
        html.Div(id='behavior-filename', style={'margin-top': '10px'}),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='acc-graph', figure=empty_figure()),
        dcc.Graph(id='adn-graph', figure=empty_figure()),
    ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([
        dcc.Graph(id='acc-interval-graph', figure=empty_figure()),
        dcc.Graph(id='adn-interval-graph', figure=empty_figure()),
    ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top'})
])

@app.callback(
    [Output('photometry-filename', 'children'),
     Output('acc-graph', 'figure'),
     Output('adn-graph', 'figure')],
    [Input('upload-photometry', 'contents')],
    [State('upload-photometry', 'filename')]
)
def update_photometry(contents, filename):
    global uploaded_photometry_df
    if not contents:
        return "No file uploaded", empty_figure(), empty_figure()
    
    df = parse_contents(contents)
    uploaded_photometry_df = df  # Store globally for later use
    photometry = PhotometryDataset(io.StringIO(df.to_csv(index=False)))
    photometry.normalize_signal()
    
    acc_fig = go.Figure([
        go.Scatter(x=photometry.df.index, y=photometry.df['ACC.signal'], mode='lines', name='ACC Signal'),
        go.Scatter(x=photometry.df.index, y=photometry.df['ACC.control'], mode='lines', name='ACC Control'),
        go.Scatter(x=photometry.df.index, y=photometry.df['ACC.zdFF'], mode='lines', name='ACC zdFF', line=dict(color='blue', width=2))
    ])
    acc_fig.update_layout(title='ACC Signal, Control, and zdFF')
    
    adn_fig = go.Figure([
        go.Scatter(x=photometry.df.index, y=photometry.df['ADN.signal'], mode='lines', name='ADN Signal'),
        go.Scatter(x=photometry.df.index, y=photometry.df['ADN.control'], mode='lines', name='ADN Control'),
        go.Scatter(x=photometry.df.index, y=photometry.df['ADN.zdFF'], mode='lines', name='ADN zdFF', line=dict(color='blue', width=2))
    ])
    adn_fig.update_layout(title='ADN Signal, Control, and zdFF')
    
    return f"Uploaded: {filename}", acc_fig, adn_fig

@app.callback(
    [Output('behavior-filename', 'children'),
     Output('acc-interval-graph', 'figure'),
     Output('adn-interval-graph', 'figure')],
    [Input('upload-behavior', 'contents')],
    [State('upload-behavior', 'filename')]
)
def update_behavior(contents, filename):
    global uploaded_photometry_df
    acc_interval_fig = empty_figure()
    adn_interval_fig = empty_figure()
    
    if not contents or uploaded_photometry_df is None:
        return "No file uploaded or photometry data missing", acc_interval_fig, adn_interval_fig
    
    df = parse_contents(contents)
    behavior = BehaviorDataset(io.StringIO(df.to_csv(index=False)))
    photometry = PhotometryDataset(io.StringIO(uploaded_photometry_df.to_csv(index=False)))
    merged = MergeDatasets(photometry, behavior)
    mergeddataset = merged.df
    
    fps = 100
    onsets = mergeddataset[mergeddataset['freezing'].diff() == 1].index
    offsets = mergeddataset[mergeddataset['freezing'].diff() == -1].index
    epochs = [(int(on-fps*1.5), int(on+fps*1.5)) for on, off in zip(onsets, offsets)]
    
    for inter in epochs:
        if inter[0] < 0 or inter[1] > len(mergeddataset):
            continue
        x = np.arange(-fps*1.5, fps*1.5)
        y_acc = mergeddataset['ACC.signal'][inter[0]:inter[1]]
        y_adn = mergeddataset['ADN.signal'][inter[0]:inter[1]]
        acc_interval_fig.add_trace(go.Scatter(x=x, y=y_acc, mode='lines', opacity=0.5))
        adn_interval_fig.add_trace(go.Scatter(x=x, y=y_adn, mode='lines', opacity=0.5))
    
    return f"Uploaded: {filename}", acc_interval_fig, adn_interval_fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

