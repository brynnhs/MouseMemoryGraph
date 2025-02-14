import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash import dcc, html
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets

photometry = PhotometryDataset("/Users/julian/Documents/daten/STUDIUM Master/FabLab 2025/raw data - 04 Feb/cfc_2046.csv")
behavior = BehaviorDataset("/Users/julian/Documents/daten/STUDIUM Master/FabLab 2025/Codebase/MouseMemoryGraph/data/a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")

photometry.normalize_signal()

merged = MergeDatasets(photometry, behavior)

# Load your dataset
mergeddataset = merged.df

app = dash.Dash(__name__)

# Create the ACC graph
acc_fig = go.Figure()

acc_fig.add_trace(go.Scatter(
    x=mergeddataset.index,
    y=mergeddataset['ACC.signal'],
    mode='lines',
    name='ACC Signal',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

acc_fig.add_trace(go.Scatter(
    x=mergeddataset.index,
    y=mergeddataset['ACC.control'],
    mode='lines',
    name='ACC Control',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

acc_fig.add_trace(go.Scatter(
    x=mergeddataset.index,
    y=mergeddataset['ACC.zdFF'],
    mode='lines',
    name='ACC zdFF',
    line=dict(color='blue', width=2, dash='solid')
))

acc_fig.update_layout(
    title='ACC Signal, Control, and zdFF',
    xaxis_title='Index',
    yaxis_title='Value',
)

# from the freezing array find the onsets and offsets which is the change from 0 to 1 and 1 to 0

onsets = mergeddataset[mergeddataset['freezing'].diff() == 1].index
offsets = mergeddataset[mergeddataset['freezing'].diff() == -1].index
intervals = list(zip(onsets, offsets))

for on, off in intervals:
    acc_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)


# create intervals of 2s before and after event
fps = 100
epochs = [(int(on-fps*1.5), int(on+fps*1.5)) for on, off in intervals]

# plot the lines
acc_interval_fig = go.Figure()
aggregate_epoch = []
for inter in epochs:
    if inter[0] < 0 or inter[1] > len(mergeddataset):
        continue
    else:
        x = np.arange(-fps*1.5, fps*1.5)
        y = mergeddataset['ACC.signal'][inter[0]:inter[1]]
        acc_interval_fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            line=dict(color='gray', width=1, dash='solid'),
            opacity=0.5
        ))
        aggregate_epoch.append(y)

# plot the average and std of the epochs
aggregate_epoch = np.array(aggregate_epoch)
mean = np.mean(aggregate_epoch, axis=0)
std = np.std(aggregate_epoch, axis=0)

acc_interval_fig.add_trace(go.Scatter(
    x=x,
    y=mean,
    mode='lines',
    line=dict(color='blue', width=2, dash='solid')
))


# Create the ADN graph
adn_fig = go.Figure()

adn_fig.add_trace(go.Scatter(
    x=mergeddataset.index,
    y=mergeddataset['ADN.signal'],
    mode='lines',
    name='ADN Signal',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

adn_fig.add_trace(go.Scatter(
    x=mergeddataset.index,
    y=mergeddataset['ADN.control'],
    mode='lines',
    name='ADN Control',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

adn_fig.add_trace(go.Scatter(
    x=mergeddataset.index,
    y=mergeddataset['ADN.zdFF'],
    mode='lines',
    name='ADN zdFF',
    line=dict(color='blue', width=2, dash='solid')
))

adn_fig.update_layout(
    title='ADN Signal, Control, and zdFF',
    xaxis_title='Index',
    yaxis_title='Value',
)

for on, off in intervals:
    adn_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)


# plot the lines
adn_interval_fig = go.Figure()
aggregate_epoch = []
for inter in epochs:
    if inter[0] < 0 or inter[1] > len(mergeddataset):
        continue
    else:
        x = np.arange(-fps*1.5, fps*1.5)
        y = mergeddataset['ADN.signal'][inter[0]:inter[1]]
        adn_interval_fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            line=dict(color='gray', width=1, dash='solid'),
            opacity=0.5
        ))
        aggregate_epoch.append(y)

# plot the average and std of the epochs
aggregate_epoch = np.array(aggregate_epoch)
mean = np.mean(aggregate_epoch, axis=0)
std = np.std(aggregate_epoch, axis=0)

adn_interval_fig.add_trace(go.Scatter(
    x=x,
    y=mean,
    mode='lines',
    line=dict(color='blue', width=2, dash='solid')
))

acc_fig.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})
adn_fig.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})
acc_interval_fig.update_layout({
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'plot_bgcolor': 'rgba(10, 10, 10, 0.02)',
})
adn_interval_fig.update_layout({
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'plot_bgcolor': 'rgba(10, 10, 10, 0.02)',
})


# add the two figures to a dashboard
app.layout = html.Div([
    html.Div([
        dcc.Graph(figure=acc_fig),
        dcc.Graph(figure=adn_fig),
    ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([
        dcc.Graph(figure=acc_interval_fig),
        dcc.Graph(figure=adn_interval_fig),
    ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top'})
])

# make a layout for the dashboard 


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
