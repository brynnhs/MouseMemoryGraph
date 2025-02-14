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
                    name='ACC Signal'
                ),
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ACC.control'],
                    mode='lines',
                    name='ACC Control'
                )
            ],
            'layout': go.Layout(
                title='ACC Signal and Control',
                xaxis={'title': 'Index'},
                yaxis={'title': 'Value'}
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
                    name='ADN Signal'
                ),
                go.Scatter(
                    x=mergeddataset.index,
                    y=mergeddataset['ADN.control'],
                    mode='lines',
                    name='ADN Control'
                )
            ],
            'layout': go.Layout(
                title='ADN Signal and Control',
                xaxis={'title': 'Index'},
                yaxis={'title': 'Value'}
            )
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)