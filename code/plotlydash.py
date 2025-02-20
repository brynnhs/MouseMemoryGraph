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
fps = merged.fps
duration = 3
intervals = merged.get_freezing_intervals()
epochs_acc = merged.get_epoch_data(intervals, 'ACC', duration=duration)
epochs_acc_off = merged.get_epoch_data(intervals, 'ACC', duration=duration, type='off')
epochs_adn = merged.get_epoch_data(intervals, 'ADN', duration=duration)
epochs_adn_off = merged.get_epoch_data(intervals, 'ADN', duration=duration, type='off')

app = dash.Dash(__name__)

# Create the ACC graph
acc_fig = go.Figure()
x = np.arange(0, len(mergeddataset)/fps, 1/fps)
acc_fig.add_trace(go.Scatter(
    x=x,
    y=mergeddataset['ACC.signal'],
    mode='lines',
    name='ACC Signal',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

acc_fig.add_trace(go.Scatter(
    x=x,
    y=mergeddataset['ACC.control'],
    mode='lines',
    name='ACC Control',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

acc_fig.add_trace(go.Scatter(
    x=x,
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

# add dummy trace
acc_fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    name=f'freezing bouts > {duration}s',
    marker=dict(color='blue', size=7, symbol='square', opacity=0.2)
))

acc_fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    name=f'freezing bouts < {duration}s',
    marker=dict(color='lightblue', size=7, symbol='square', opacity=0.3)
))

# from the freezing array find the onsets and offsets which is the change from 0 to 1 and 1 to 0

for on, off in intervals:
    on = on / fps
    off = off / fps
    acc_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

# plot the lines
acc_interval_fig = go.Figure()
aggregate_epoch = []
for i, inter in enumerate(epochs_acc):
    x = np.arange(-duration, duration, 1/fps)
    y = inter[2]
    acc_interval_fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name=f'onset {i+1}',
        mode='lines',
        line=dict(color='gray', width=1, dash='solid'),
        opacity=0.5
    ))
    aggregate_epoch.append(y)
    acc_fig.add_vrect(x0=inter[1][0]/ fps, x1=inter[1][1]/ fps, fillcolor='blue', opacity=0.2, layer='below', line_width=0)

# plot the average and std of the epochs
aggregate_epoch = np.array(aggregate_epoch)
mean = np.mean(aggregate_epoch, axis=0)
std = np.std(aggregate_epoch, axis=0)
y_upper = mean + std
y_lower = mean - std

acc_interval_fig.add_trace(go.Scatter(
    x=x,
    y=mean,
    mode='lines',
    name='mean signal',
    line=dict(color='blue', width=2, dash='solid')
))
acc_interval_fig.add_trace(go.Scatter(
        x=x,
        y=y_upper,
        #fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))
acc_interval_fig.add_trace(go.Scatter(
        x=x,
        y=y_lower,
        fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))

acc_interval_fig.add_vrect(x0=0, x1=duration, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

# plot the lines
acc_interval_fig_off = go.Figure()
aggregate_epoch = []
for i, inter in enumerate(epochs_acc_off):
    x = np.arange(-duration, duration, 1/fps)
    y = inter[2]
    acc_interval_fig_off.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        name=f'offset {i+1}',
        line=dict(color='gray', width=1, dash='solid'),
        opacity=0.5
    ))
    aggregate_epoch.append(y)

# plot the average and std of the epochs
aggregate_epoch = np.array(aggregate_epoch)
mean = np.mean(aggregate_epoch, axis=0)
std = np.std(aggregate_epoch, axis=0)
y_upper = mean + std
y_lower = mean - std

acc_interval_fig_off.add_trace(go.Scatter(
    x=x,
    y=mean,
    mode='lines',
    name='mean signal',
    line=dict(color='blue', width=2, dash='solid')
))
acc_interval_fig_off.add_trace(go.Scatter(
        x=x,
        y=y_upper,
        #fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))
acc_interval_fig_off.add_trace(go.Scatter(
        x=x,
        y=y_lower,
        fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))

acc_interval_fig_off.add_vrect(x0=-duration, x1=0, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

# Create the ADN graph
adn_fig = go.Figure()
x = np.arange(0, len(mergeddataset)/fps, 1/fps)
adn_fig.add_trace(go.Scatter(
    x=x,
    y=mergeddataset['ADN.signal'],
    mode='lines',
    name='ADN Signal',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

adn_fig.add_trace(go.Scatter(
    x=x,
    y=mergeddataset['ADN.control'],
    mode='lines',
    name='ADN Control',
    line=dict(color='gray', width=1, dash='solid'),
    opacity=0.5
))

adn_fig.add_trace(go.Scatter(
    x=x,
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

# add dummy trace
adn_fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    name=f'freezing bouts > {duration}s',
    marker=dict(color='blue', size=7, symbol='square', opacity=0.2)
))

adn_fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    name=f'freezing bouts < {duration}s',
    marker=dict(color='lightblue', size=7, symbol='square', opacity=0.3)
))

for on, off in intervals:
    on = on / fps
    off = off / fps
    adn_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)


# plot the lines
adn_interval_fig = go.Figure()
aggregate_epoch = []
for i, inter in enumerate(epochs_adn):
    x = np.arange(-duration, duration, 1/fps)
    y = inter[2]
    adn_interval_fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        name=f'onset {i+1}',
        line=dict(color='gray', width=1, dash='solid'),
        opacity=0.5
    ))
    aggregate_epoch.append(y)
    adn_fig.add_vrect(x0=inter[1][0]/ fps, x1=inter[1][1]/ fps, fillcolor='blue', opacity=0.2, layer='below', line_width=0)

# plot the average and std of the epochs
aggregate_epoch = np.array(aggregate_epoch)
mean = np.mean(aggregate_epoch, axis=0)
std = np.std(aggregate_epoch, axis=0)
y_upper = mean + std
y_lower = mean - std

adn_interval_fig.add_trace(go.Scatter(
    x=x,
    y=mean,
    mode='lines',
    name='mean signal',
    line=dict(color='blue', width=2, dash='solid')
))
adn_interval_fig.add_trace(go.Scatter(
        x=x,
        y=y_upper,
        #fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))
adn_interval_fig.add_trace(go.Scatter(
        x=x,
        y=y_lower,
        fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))
adn_interval_fig.add_vrect(x0=0, x1=duration, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

# plot the lines
adn_interval_fig_off = go.Figure()
aggregate_epoch = []
for i, inter in enumerate(epochs_adn_off):
    x = np.arange(-duration, duration, 1/fps)
    y = inter[2]
    adn_interval_fig_off.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        name=f'offset {i+1}',
        line=dict(color='gray', width=1, dash='solid'),
        opacity=0.5
    ))
    aggregate_epoch.append(y)

# plot the average and std of the epochs
aggregate_epoch = np.array(aggregate_epoch)
mean = np.mean(aggregate_epoch, axis=0)
std = np.std(aggregate_epoch, axis=0)
y_upper = mean + std
y_lower = mean - std


adn_interval_fig_off.add_trace(go.Scatter(
    x=x,
    y=mean,
    mode='lines',
    name='mean signal',
    line=dict(color='blue', width=2, dash='solid')
))
adn_interval_fig_off.add_trace(go.Scatter(
        x=x,
        y=y_upper,
        #fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))
adn_interval_fig_off.add_trace(go.Scatter(
        x=x,
        y=y_lower,
        fill='tonexty',
        hoverinfo="skip",
        fillcolor='rgba(0, 0, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False))
adn_interval_fig_off.add_vrect(x0=-duration, x1=0, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)


acc_fig.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'xaxis_title': 'Time (s)',
'yaxis_title': 'Normalized photometry signal',
})
acc_interval_fig_off.update_layout({
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'plot_bgcolor': 'rgba(10, 10, 10, 0.02)',
'xaxis_title': 'Time (s)',
'yaxis_title': 'Normalized photometry signal',
})
adn_fig.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'xaxis_title': 'Time (s)',
'yaxis_title': 'Normalized photometry signal',
})
acc_interval_fig.update_layout({
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'plot_bgcolor': 'rgba(10, 10, 10, 0.02)',
'xaxis_title': 'Time (s)',
'yaxis_title': 'Normalized photometry signal',
})
adn_interval_fig.update_layout({
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'plot_bgcolor': 'rgba(10, 10, 10, 0.02)',
'xaxis_title': 'Time (s)',
'yaxis_title': 'Normalized photometry signal',
})
adn_interval_fig_off.update_layout({
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'plot_bgcolor': 'rgba(10, 10, 10, 0.02)',
'xaxis_title': 'Time (s)',
'yaxis_title': 'Normalized photometry signal',
})

# add the two figures to a dashboard
app.layout = html.Div([
    html.Div([
        dcc.Graph(figure=acc_fig),
        dcc.Graph(figure=adn_fig),
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([
        dcc.Graph(figure=acc_interval_fig),
        dcc.Graph(figure=adn_interval_fig),
    ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([
        dcc.Graph(figure=acc_interval_fig_off),
        dcc.Graph(figure=adn_interval_fig_off),
    ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'})
])

# make a layout for the dashboard 


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
