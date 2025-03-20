# 1. Overview: This module creates the Average page for visualizing sensor data averages using Dash.
# 2. Dependencies and Imports

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from utils import load_condition_assignments, load_mouse_data

# Function: load_raw_data
# Purpose: Load raw merged data for a given mouse from the photometry and behavior CSV files, normalize and merge them.
def load_raw_data(mouse_id):
    # Load condition assignments mapping: mouse id -> condition group
    condition_assignments = load_condition_assignments()

    # Layout: Defines the structure of the Average page including data stores, input controls, and graphs.
    app.layout = html.Div([
        # ... layout components ...
    ])

    # Callback: populate_event_selection_options
    # Purpose: Update event selection dropdown options based on the event-store data.
    @app.callback(...)
    def populate_event_selection_options(...):
        pass

    # Callback: populate_group_dropdown_options
    # Purpose: Update the group selection dropdown with options from the group-store data.
    @app.callback(...)
    def populate_group_dropdown_options(...):
        pass

    # Callback: load_mouse_data
    # Purpose: Load or update mouse data based on the selected folder, app state, and events.
    @app.callback(...)
    def load_mouse_data(...):
        pass

    # Callback: update_color_overrides
    # Purpose: Update the color mapping for specific traces based on the selected color from the color picker.
    @app.callback(...)
    def update_color_overrides(...):
        pass

    # Callback: update_trace_dropdown
    # Purpose: Update the trace dropdown options based on the selected average plot and stored figures.
    @app.callback(...)
    def update_trace_dropdown(...):
        pass

    # Callback: update_graph
    # Purpose: Generate average plots and update the page content and stored figures based on user inputs and loaded mouse data.
    @app.callback(...)
    def update_graph(...):
        pass
