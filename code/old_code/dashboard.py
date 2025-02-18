import dash
from dash import dcc, html, Input, Output, State, ctx, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import base64
import io
from dataset import PhotometryDataset

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Photometry & Video Data Analysis"),
    
    dbc.Row([
        dbc.Col([
            html.H4("Upload Your Data (Drag & Drop)"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ', html.A('Select Files')
                ]),
                style={
                    'width': '100%', 'height': '100px', 'lineHeight': '100px',
                    'borderWidth': '2px', 'borderStyle': 'dashed',
                    'borderRadius': '5px', 'textAlign': 'center'
                },
                multiple=True
            ),
            html.Div(id='uploaded-data-info', style={'margin-top': '10px'})
        ], width=12),
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H4("Upload Photometry Data"),
            dcc.Upload(
                id='upload-photometry',
                children=html.Button('Upload CSV File'),
                multiple=False,
            ),
            html.Div(id='photometry-filename', style={'margin-top': '10px'})
        ], width=6),
        
        dbc.Col([
            html.H4("Upload Video Data (CSV)"),
            dcc.Upload(
                id='upload-video',
                children=html.Button('Upload CSV File'),
                multiple=False,
            ),
            html.Div(id='video-filename', style={'margin-top': '10px'})
        ], width=6),
    ]),
    
    html.Hr(),
    
    html.H3("Processed Photometry Data"),
    dcc.Graph(id='photometry-plot'),
    
    html.H3("Processed Video Data"),
    dcc.Graph(id='video-plot'),
])


@app.callback(
    Output('uploaded-data-info', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_uploaded_data(contents, filenames):
    if not contents:
        return "No files uploaded"
    
    file_list = [f"Uploaded: {name}" for name in filenames]
    return html.Ul([html.Li(file) for file in file_list])

@app.callback(
    Output('photometry-filename', 'children'),
    Output('photometry-plot', 'figure'),
    Input('upload-photometry', 'contents'),
    State('upload-photometry', 'filename')
)
def process_photometry(contents, filename):
    if not contents:
        return "No file uploaded", px.line()
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    column_map = {df.columns[1]: "ACC.control", df.columns[2]: "ACC.signal"}  # Adjust if needed
    dataset = PhotometryDataset(io.StringIO(decoded.decode('utf-8')), column_map=column_map, bin_size=0.1, cutoff=2.0, fps=30)
    
    processed_df = dataset.df  # Corrected to return the processed dataframe
    fig = px.line(processed_df, x='Time(s)', y=['ACC.signal', 'ACC.control'], title="Processed Photometry Signals")
    
    return f"Uploaded: {filename}", fig

@app.callback(
    Output('video-filename', 'children'),
    Output('video-plot', 'figure'),
    Input('upload-video', 'contents'),
    State('upload-video', 'filename')
)
def process_video_data(contents, filename):
    if not contents:
        return "No file uploaded", px.line()
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    fig = px.line(df, x=df.columns[0], y=df.columns[1:], title="Processed Video Data")
    
    return f"Uploaded: {filename}", fig

if __name__ == '__main__':
    app.run_server(debug=True)
