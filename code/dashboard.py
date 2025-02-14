import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import plotly.graph_objs as go
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets

photometry = PhotometryDataset("/Users/julian/Documents/daten/STUDIUM Master/FabLab 2025/raw data - 04 Feb/cfc_2046.csv")
behavior = BehaviorDataset("/Users/julian/Documents/daten/STUDIUM Master/FabLab 2025/Codebase/MouseMemoryGraph/data/a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")

photometry.normalize_signal()

merged = MergeDatasets(photometry, behavior)

# Load your dataset
mergeddataset = merged.df

# Function to create freezing intervals
def create_freezing_shapes(df):
    shapes = []
    freezing_intervals = df[df['freezing'] == 1].index
    if not freezing_intervals.empty:
        start = freezing_intervals[0]
        for i in range(1, len(freezing_intervals)):
            if freezing_intervals[i] != freezing_intervals[i-1] + 1:
                shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=start,
            x1=freezing_intervals[-1],
            y0=0,
            y1=1,
            fillcolor='blue'
        ))
                start = freezing_intervals[i]
        shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=start,
            x1=freezing_intervals[-1],
            y0=0,
            y1=1,
            fillcolor='blue'
        ))
    return shapes

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Signal and Control Signal Dashboard'),

    dcc.Graph(
        id='ACC-graph',
        figure={
            'data': [
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ACC.signal'],
                    mode='lines',
                    name='ACC Signal',
                    line=dict(color='gray', width=1, dash='solid'),
                    opacity=0.5
                ),
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ACC.control'],
                    mode='lines',
                    name='ACC Control',
                    line=dict(color='gray', width=1, dash='solid'),
                    opacity=0.5
                ),
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ACC.zdFF'],
                    mode='lines',
                    name='ACC zdFF',
                    line=dict(color='blue', width=2, dash='solid')
                )
            ],
            'layout': go.Layout(
                title='ACC Signal, Control, and zdFF',
                xaxis={'title': 'Index'},
                yaxis={'title': 'Value'},
                shapes=create_freezing_shapes(mergeddataset)
            )
        }
    ),

    dcc.Graph(
        id='ADN-graph',
        figure={
            'data': [
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ADN.signal'],
                    mode='lines',
                    name='ADN Signal',
                    line=dict(color='gray', width=1, dash='solid'),
                    opacity=0.5
                ),
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ADN.control'],
                    mode='lines',
                    name='ADN Control',
                    line=dict(color='gray', width=1, dash='solid'),
                    opacity=0.5
                ),
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ADN.zdFF'],
                    mode='lines',
                    name='ADN zdFF',
                    line=dict(color='blue', width=2, dash='solid')
                )
            ],
            'layout': go.Layout(
                title='ADN Signal, Control, and zdFF',
                xaxis={'title': 'Index'},
                yaxis={'title': 'Value'},
                shapes=create_freezing_shapes(mergeddataset)
            )
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)