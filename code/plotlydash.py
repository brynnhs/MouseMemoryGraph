import plotly.graph_objs as go
import pandas as pd
import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
from dataset import PhotometryDataset, BehaviorDataset, MergeDatasets
import os

# Define the base directory
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

# Load datasets for two mice
mouse_data = {}
mouse_folders = ["mouse1", "mouse2"]

for mouse in mouse_folders:
    photometry_path = os.path.join(data_dir, mouse, "cfc_2046.csv")
    behavior_path = os.path.join(data_dir, mouse, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")
    
    if os.path.exists(photometry_path) and os.path.exists(behavior_path):
        photometry = PhotometryDataset(photometry_path)
        behavior = BehaviorDataset(behavior_path)
        photometry.normalize_signal()
        merged = MergeDatasets(photometry, behavior).df
        mouse_data[mouse] = merged

app = dash.Dash(__name__)

# Layout with Tabs
tabs = dcc.Tabs(id="tabs", value="mouse1", children=[
    dcc.Tab(label=f"Mouse {mouse}", value=mouse) for mouse in mouse_data
])

app.layout = html.Div([
    # ✅ Banner Section (Header)
    html.Div([
        html.Img(src='/assets/header.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),

    # ✅ Main Dashboard Layout
    html.Div([
        html.Div([
            dcc.Tabs(id="tabs", value="mouse1", vertical=True, children=[
                dcc.Tab(label=f"Mouse {mouse}", value=mouse) for mouse in mouse_data
            ], style={'width': '100%'})  # Full width of sidebar
        ], style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'top'}),  # Sidebar style

        html.Div(id='tab-content', style={'width': '80%', 'display': 'inline-block', 'padding-left': '20px'})  # Main content
    ], style={'display': 'flex'}),

    # ✅ Footer Section (Image)
    html.Div([
        html.Img(src='/assets/footer.png', style={'width': '100%', 'height': 'auto'})
    ], style={'text-align': 'center', 'margin-top': '10px'})
])

# Callback to update figures based on selected mouse
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def update_tab(selected_mouse):
    if selected_mouse not in mouse_data:
        return "No data available."
    
    mergeddataset = mouse_data[selected_mouse]

    # ✅ Step 1: Loop Through Each Mouse's Data Individually
    for mouse_name, dataset in mouse_data.items():
        
        # Create the ACC graph
        acc_fig = go.Figure()
        # Create the ADN graph
        adn_fig = go.Figure()
        
        print(f"\nProcessing freezing data for: {mouse_name}")
        
        # ✅ Step 2: Ensure we only process one mouse at a time
        mergeddataset = dataset.copy()

        print(f"Total entries in dataset: {len(mergeddataset)}")
        print(f"First 10 timestamps: {mergeddataset['Time(s)'].head(10).tolist()}")

        # ✅ Step 3: Apply Rolling Window to Reduce Freezing Noise
        fps = 100  
        min_freeze_duration = int(0.1 * fps)  # 0.5 seconds threshold

        rolling_freezing = mergeddataset['freezing'].rolling(window=min_freeze_duration, center=True).sum()
        mergeddataset['freezing_clean'] = (rolling_freezing >= min_freeze_duration).astype(int)

        # ✅ Step 4: Detect Onsets & Offsets for This Mouse Only
        onsets = mergeddataset[mergeddataset['freezing_clean'].diff() == 1].index.tolist()
        offsets = mergeddataset[mergeddataset['freezing_clean'].diff() == -1].index.tolist()

        # Ensure matching onsets and offsets
        if len(onsets) > len(offsets):
            offsets.append(mergeddataset.index[-1])  
        elif len(offsets) > len(onsets):
            onsets.insert(0, mergeddataset.index[0])  

        intervals = list(zip(onsets, offsets))

        print(f"Final detected freezing intervals for {mouse_name}: {len(intervals)}")

        # ✅ Step 5: Apply Blue Shading for Freezing Periods (Per Mouse)
        for on, off in intervals:
            acc_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
            adn_fig.add_vrect(x0=on, x1=off, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)


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
            yaxis_title='Value'
        )

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
            yaxis_title='Value'
        )


        # Create intervals of 2s before and after event
        fps = 100
        epochs = [(int(on - fps * 1.5), int(on + fps * 1.5)) for on, off in intervals]

        # Plot the ACC interval responses
        acc_interval_fig = go.Figure()
        aggregate_epoch = []
        for inter in epochs:
            if inter[0] < 0 or inter[1] > len(mergeddataset):
                continue
            else:
                x = np.arange(-fps * 1.5, fps * 1.5)
                y = mergeddataset['ACC.signal'][inter[0]:inter[1]]
                acc_interval_fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    line=dict(color='gray', width=1, dash='solid'),
                    opacity=0.5
                ))
                aggregate_epoch.append(y)

        # Plot the average and std of the epochs
        aggregate_epoch = np.array(aggregate_epoch)
        mean = np.mean(aggregate_epoch, axis=0)

        acc_interval_fig.add_trace(go.Scatter(
            x=x,
            y=mean,
            mode='lines',
            line=dict(color='blue', width=2, dash='solid')
        ))

        # Plot the ADN interval responses
        adn_interval_fig = go.Figure()
        aggregate_epoch = []
        for inter in epochs:
            if inter[0] < 0 or inter[1] > len(mergeddataset):
                continue
            else:
                x = np.arange(-fps * 1.5, fps * 1.5)
                y = mergeddataset['ADN.signal'][inter[0]:inter[1]]
                adn_interval_fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    line=dict(color='gray', width=1, dash='solid'),
                    opacity=0.5
                ))
                aggregate_epoch.append(y)

        # Plot the average and std of the epochs
        aggregate_epoch = np.array(aggregate_epoch)
        mean = np.mean(aggregate_epoch, axis=0)

        adn_interval_fig.add_trace(go.Scatter(
            x=x,
            y=mean,
            mode='lines',
            line=dict(color='blue', width=2, dash='solid')
        ))

    return html.Div([
        html.Div([
            dcc.Graph(figure=acc_fig),
            dcc.Graph(figure=adn_fig),
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(figure=acc_interval_fig),
            dcc.Graph(figure=adn_interval_fig),
        ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top'})
    ])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)