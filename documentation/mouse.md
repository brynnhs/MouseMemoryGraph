# 1. Base Path Determination: Set the root directory for loading data files.
The `base_path` variable is used to define the root directory where mouse data files are stored. This ensures that all file operations (such as loading CSV files for photometry and behavioral data) are correctly referenced regardless of the script’s execution location.

# 2. Data Loading and Caching: Loads and processes photometry and behavioral data for a given mouse, with caching for efficiency.
The `load_raw_data` function is responsible for retrieving photometry and behavioral data for a given mouse ID. To improve performance, it is decorated with `@lru_cache`, which stores previously loaded datasets in memory, reducing redundant file access. This caching is particularly useful when analyzing multiple mice within the same session.

# 3. Dynamic Page Layout: Defines the web page structure and user interface elements for mouse data visualization.
The `layout` function defines the interactive layout of the page using Dash components. It includes:
- **Dropdown menus** for selecting conditions and event types.
- **Graph placeholders** for visualizing photometry and behavioral data.
- **User input fields** to configure analysis parameters, such as time windows for event-related data extraction.
This modular approach allows for dynamic updates based on user selections.

# 4. Callbacks and Interactivity: Handles user interactions, updates graphs, and manages data assignments.

# 4.1 Populate Event Selection: Generates dropdown options for selecting events based on stored data.
This callback retrieves available events from the event store and populates the dropdown menu. Users can select an event (e.g., "freezing") to analyze its effect on neural activity.

# 4.2 Populate Group Dropdown: Loads available condition groups for selection.
This function retrieves group assignments (e.g., experimental vs. control groups) and presents them as options in the dropdown menu. Groups help categorize mice based on experimental conditions.

# 4.3 Load Mouse Data: Retrieves and caches data based on selected mouse ID.
This function loads photometry and behavioral data for a selected mouse. If the data is already cached, it is retrieved from memory; otherwise, it is loaded from disk and processed.

# 4.4 Update Graph: Generates and updates figures based on user-selected parameters.
This function updates the visualizations based on the selected mouse, condition, and event parameters. It regenerates plots using the latest user input values and ensures that all graphs remain synchronized with the dataset.

# 4.5 Manage Mouse Assignment: Updates the group assignment for a selected mouse.
This function updates the condition group associated with a particular mouse. It allows users to manually categorize mice into experimental groups within the app.

# 4.6 Update Trace Selection: Adjusts available trace options based on selected graph.
This function dynamically updates the trace selection dropdown based on the currently displayed graph. It ensures that only relevant traces are available for user modifications.

# 4.7 Update Trace Colors: Allows users to modify trace colors dynamically in the visualization.
This function enables users to change the color of specific traces in the graphs. This is useful for distinguishing between different groups or conditions in the dataset.

# 5. Concurrency and Caching: Utilizes threading and caching to improve performance when processing datasets.
The module leverages `ThreadPoolExecutor` to parallelize data processing tasks, such as computing event-related averages. This reduces processing time, particularly for large datasets.

# 6. Usage and Integration: Registers the module as a Dash page and connects it with other components.
This module is registered as a Dash page, allowing it to be dynamically loaded within the larger application. The `app.layout = layout` statement ensures that the UI is properly structured when the page is accessed.

# 7. Extensibility: Designed to accommodate additional data processing, visualization, and user interaction features.
Future improvements could include:
- Additional event types for behavioral analysis.
- More advanced filtering options for event selection.
- Customizable data preprocessing steps before visualization.