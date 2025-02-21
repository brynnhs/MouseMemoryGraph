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

dash_app = dash.Dash(__name__)

uploaded_photometry_df = None
uploaded_behavior_df = None

def empty_figure():
    return go.Figure()

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))

dash_app.layout = html.Div([
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

@dash_app.callback(
    [Output('photometry-filename', 'children'),
     Output('behavior-filename', 'children'),
     Output('acc-graph', 'figure'),
     Output('adn-graph', 'figure'),
     Output('acc-interval-graph', 'figure'),
     Output('adn-interval-graph', 'figure')],
    [Input('upload-photometry', 'contents'),
     Input('upload-behavior', 'contents')],
    [State('upload-photometry', 'filename'),
     State('upload-behavior', 'filename')]
)
def update_graphs(photometry_contents, behavior_contents, photometry_filename, behavior_filename):
    global uploaded_photometry_df
    acc_fig, adn_fig = empty_figure(), empty_figure()
    acc_interval_fig, adn_interval_fig = empty_figure(), empty_figure()
    
    if photometry_contents:
        df = parse_contents(photometry_contents)
        uploaded_photometry_df = df
        photometry = PhotometryDataset(io.StringIO(df.to_csv(index=False)))
        photometry.normalize_signal()
        
        acc_fig.add_trace(go.Scatter(x=photometry.df.index, y=photometry.df['ACC.signal'], mode='lines', name='ACC Signal', line=dict(color='red', width=1, dash='solid'), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=photometry.df.index, y=photometry.df['ACC.control'], mode='lines', name='ACC Control', line=dict(color='green', width=1, dash='solid'), opacity=0.5))
        acc_fig.add_trace(go.Scatter(x=photometry.df.index, y=photometry.df['ACC.zdFF'], mode='lines', name='ACC zdFF', line=dict(color='blue', width=2, dash='solid')))
        acc_fig.update_layout(title='ACC Signal, Control, and zdFF')
        
        adn_fig.add_trace(go.Scatter(x=photometry.df.index, y=photometry.df['ADN.signal'], mode='lines', name='ADN Signal', line=dict(color='red', width=1, dash='solid'), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=photometry.df.index, y=photometry.df['ADN.control'], mode='lines', name='ADN Control', line=dict(color='green', width=1, dash='solid'), opacity=0.5))
        adn_fig.add_trace(go.Scatter(x=photometry.df.index, y=photometry.df['ADN.zdFF'], mode='lines', name='ADN zdFF', line=dict(color='blue', width=2, dash='solid')))
        adn_fig.update_layout(title='ADN Signal, Control, and zdFF')
    
    if behavior_contents and uploaded_photometry_df is not None:
        df = parse_contents(behavior_contents)
        behavior = BehaviorDataset(io.StringIO(df.to_csv(index=False)))
        photometry = PhotometryDataset(io.StringIO(uploaded_photometry_df.to_csv(index=False)))
        merged = MergeDatasets(photometry, behavior)
        mergeddataset = merged.df
        
        onsets = mergeddataset[mergeddataset['freezing'].diff() == 1].index
        offsets = mergeddataset[mergeddataset['freezing'].diff() == -1].index
        
        fps = 100
        epochs = [(int(on-fps*1.5), int(on+fps*1.5)) for on, off in zip(onsets, offsets)]
        aggregate_epoch_acc, aggregate_epoch_adn = [], []
        
        for inter in epochs:
            if inter[0] < 0 or inter[1] > len(mergeddataset):
                continue
            x = np.arange(-fps*1.5, fps*1.5)
            y_acc = mergeddataset['ACC.signal'][inter[0]:inter[1]]
            y_adn = mergeddataset['ADN.signal'][inter[0]:inter[1]]
            acc_interval_fig.add_trace(go.Scatter(
                x=x,
                y=y_acc,
                mode='lines',
                line=dict(color='gray', width=1, dash='solid'),
                opacity=0.5
            ))
            adn_interval_fig.add_trace(go.Scatter(
                x=x,
                y=y_adn,
                mode='lines',
                line=dict(color='gray', width=1, dash='solid'),
                opacity=0.5
            ))
            aggregate_epoch_acc.append(y_acc)
            aggregate_epoch_adn.append(y_adn)
        
        acc_interval_fig.add_trace(go.Scatter(
            x=x,
            y=np.mean(aggregate_epoch_acc, axis=0),
            mode='lines',
            line=dict(color='blue', width=2, dash='solid')
        ))
        adn_interval_fig.add_trace(go.Scatter(
            x=x,
            y=np.mean(aggregate_epoch_adn, axis=0),
            mode='lines',
            line=dict(color='blue', width=2, dash='solid')
        ))
    
    return photometry_filename if photometry_contents else "No file uploaded", behavior_filename if behavior_contents else "No file uploaded", acc_fig, adn_fig, acc_interval_fig, adn_interval_fig

if __name__ == '__main__':
    dash_app.run_server(debug=True, port=8050, host='0.0.0.0')