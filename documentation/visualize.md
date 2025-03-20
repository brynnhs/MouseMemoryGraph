# Visualize.py Documentation

This document provides an overview and detailed explanation of the `visualize.py` module, which is used to generate plots and visualizations for sensor data using Plotly and NumPy.

## 1. Overview

The `visualize.py` module includes functions to generate different types of plots:

- **Average Plots:** Creates average plots for ON and OFF epochs of sensor data, including group-specific and overall averages.
- **Detailed Plots:** Generates comprehensive visualizations of sensor signals including full signals, interval-based plots for event onsets/offsets, and changes in zdFF (delta fluorescence).
- **Separated Plots:** Produces isolated plots for individual sensors (e.g., ACC, ADN) with specific emphasis on freezing intervals and control adjustments.

These visualizations are used to analyze sensor performance, event-related changes, and behavioral correlations.

## 2. File Purpose

The primary objectives of the `visualize.py` module are:

- To provide functions that generate interactive plots for sensor data analysis using Plotly.
- To visualize averaged data over epochs, highlighting onset and offset events, as well as overall signal trends.
- To offer detailed views of sensor signals along with annotations for freezing intervals and event-related changes.

## 3. Dependencies and Imports

- **Plotly Graph Objects (`plotly.graph_objs`):**
  Used for creating interactive plots and visualizations.

- **NumPy (`numpy`):**
  Provides numerical operations and assists in generating data arrays for plotting (e.g., creating x-axis arrays).

- **Pastel Colors List:**
  A predefined list of pastel color codes is available for styling plots consistently.

## 4. Key Functions and Components

### 4.1 `generate_average_plot`

**Purpose:**

- Generates average plots for ON and OFF epochs for a given sensor.

**Behavior:**

- Accepts parameters such as the sensor name, epoch data (which can be either a dictionary for grouped data or a list), average values, and plotting parameters.
- For grouped epoch data (dictionary), it calculates both group-specific averages and an overall average (including standard deviation).
- Configures layout properties including titles, axis labels, and background colors.
- Returns four Plotly figure objects:
  - **fig_on:** Average plot for onset epochs.
  - **fig_off:** Average plot for offset epochs.
  - **avg_change_on:** Plot showing changes in zdFF for onset events.
  - **avg_change_off:** Plot showing changes in zdFF for offset events.

### 4.2 `generate_plots`

**Purpose:**

- Creates detailed plots for a sensor, including:
  - A full signals figure displaying raw sensor signals, control, and zdFF.
  - Interval plots for event onsets and offsets, highlighting the signal around these events.
  - A bar plot depicting changes in zdFF (averaged and with error bars) across events.

**Behavior:**

- Utilizes the merged dataset and event data to build multiple figures.
- Incorporates freezing interval shading and dummy traces to enhance plot legends and clarity.
- Adjusts the layout to ensure clear visualization of signals with appropriate scaling and background settings.
- Returns four Plotly figure objects representing the full signal, onset interval, offset interval, and zdFF change plots.

### 4.3 `generate_separated_plot`

**Purpose:**

- Generates a separated plot for a given sensor (e.g., 'ACC' or 'ADN'), focusing on individual sensor signal characteristics.

**Behavior:**

- Converts sensor signals and control values into percentages relative to the maximum absolute zdFF value.
- Applies a fixed offset subtraction to the control channel.
- Adds traces for the sensor signal, control, and dummy legend traces for freezing bouts.
- Highlights freezing intervals and event-specific intervals using vertical rectangles (vrects).
- Configures the plot layout, including axis ranges and background colors, to provide a clear view of the sensor data.
- Returns a single Plotly figure object with the separated visualization.

## 5. Usage Example

To utilize these functions in your analysis pipeline:

1. **Import the Module:**
   ```python
   import visualize
   ```

2. **Prepare Your Data:**
   Ensure you have the necessary data (e.g., epoch data, merged datasets, freezing intervals) and parameters (sensor name, fps, time windows).

3. **Generate a Plot:**
   For example, to create an average plot for a sensor:
   ```python
   fig_on, fig_off, avg_change_on, avg_change_off = visualize.generate_average_plot(
       sensor='ACC', 
       epochs_on=epochs_on_data, 
       epochs_off=epochs_off_data, 
       avg_on=avg_on_data, 
       avg_off=avg_off_data, 
       before=1, 
       after=2, 
       fps=30, 
       color_map={ 'Group1': '#FFB3BA', 'Group2': '#BAFFC9' }, 
       color_overrides={}
   )
   ```

4. **Display the Figure:**
   Use Plotly's `show()` method or integrate the figure into a Dash app to visualize the results.

## 6. Customization

- **Color Mapping:**
  The functions accept `color_map` and `color_overrides` parameters to customize the color schemes used for different groups or traces.

- **Layout Adjustments:**
  Plotly's layout settings (e.g., background colors, axis titles, legend configurations) can be easily modified within the functions to suit specific visualization needs.

- **Epoch Handling:**
  The functions are designed to handle both grouped (dictionary) and ungrouped (list) epoch data, allowing flexible data input formats.

---

This documentation serves as a reference for developers and analysts working with sensor data visualizations in the MouseMemoryGraph project. It outlines the functionality provided by the `visualize.py` module and offers guidance on how to extend or integrate these visualizations into broader data analysis workflows.
