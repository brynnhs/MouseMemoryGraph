# MouseMemoryGraph Application Documentation

This document describes the design, structure, and functionality of the `app.py` file used in the MouseMemoryGraph project. It details the dependencies, key functions, layout, and execution flow of the Dash web application.

## 1. Overview

The `app.py` file sets up a multi-page Dash application that serves as the user interface for viewing and interacting with mouse data. It integrates various components including custom React components, a color conversion utility, and multiple callbacks for dynamic behavior.

## 2. File Purpose

- **Primary Objective:**  
  The file initializes and configures a Dash web application that:
  - Loads raw mouse data from a specified directory.
  - Provides navigation via a dropdown menu with options for a homepage, grouped data view, and individual mouse data pages.
  - Integrates custom React components (e.g., `GroupDropdown`) for enhanced UI elements.
  - Opens the application in a web browser and runs the server on port 8050.

- **Additional Utility:**  
  A helper function is provided to convert color picker values into hexadecimal color strings, accommodating both dictionary inputs with `hex` keys and those with `rgb` keys.

## 3. Dependencies and Imports

The file relies on several external libraries and modules:

- **Standard Python Modules:**
  - `os`, `sys`, `time`: For file system interactions, execution environment checks, and simple delays.
  - `webbrowser`: To automatically open the app in a browser.
  
- **Dash and Dash Components:**
  - `dash`, `dash.dcc`, `dash.html`: Core libraries to build the web interface.
  - `dash.dependencies`: For callback definitions using `Input`, `Output`, and `State`.
  
- **Third-Party Custom Component:**
  - `dash_local_react_components`: For loading and using a custom React component (`GroupDropdown`).

## 4. Key Functions and Components

### 4.1 `get_color_hex(color_value)`

- **Purpose:**  
  Converts a color value (obtained from a color picker) into a hexadecimal string.

- **Behavior:**  
  - If `color_value` is a dictionary and contains a `hex` key, it returns the corresponding hex string.
  - If the dictionary contains an `rgb` key, it converts the RGB components to a hex string.
  - If the input is not a dictionary, it returns the original value.

- **Usage:**  
  This function ensures that color values can be reliably used in CSS and other styling contexts.

### 4.2 `load_raw_data(data_dir)`

- **Purpose:**  
  Loads and organizes raw merged data for all mice from a given directory.

- **Behavior:**  
  - Scans the specified `data_dir` for subdirectories (each representing a mouse).
  - Initializes an empty list for each detected mouse folder.

- **Output:**  
  Returns a dictionary where each key is a mouse identifier and its value is an empty list (to be populated with data later).

## 5. Dash Application Structure

### 5.1 Application Initialization

- **Dash App Setup:**  
  The Dash application is instantiated with `use_pages=True` to enable multi-page routing. The assets are loaded from the `../assets` directory.

- **React Component:**  
  The custom `GroupDropdown` component is loaded globally using `load_react_component`.

### 5.2 Layout Design

The app layout is defined as a hierarchical structure composed of:

- **URL Routing:**  
  A `dcc.Location` component tracks the current URL.

- **Header Section:**  
  Displays a header image centered at the top.

- **Navigation Dropdown:**  
  A dropdown menu (`dcc.Dropdown`) provides navigation options:
  - **Homepage:**  
    Includes a home icon and links to the homepage (`/`).
  - **Grouped Data:**  
    Provides a link for grouped data view (`/average`).
  - **Individual Mouse Pages:**  
    Dynamically generated options for each mouse based on loaded data.

- **Page Container:**  
  Uses `dash.page_container` to display the appropriate page based on the current route.

- **Footer Section:**  
  Contains a footer image.

- **Persistent State:**  
  Multiple `dcc.Store` components are used to maintain session state for:
  - Application state (`app-state`)
  - Selected folder
  - Mouse data
  - Event data
  - Group data

### 5.3 Custom Index Template

A custom HTML index string is defined to:

- Include dynamic meta, title, favicon, CSS, and JavaScript configurations.
- Ensure links inherit styling without default decorations.
- Disable pointer events for selected dropdown options.

## 6. Callback Functions

The file contains several callbacks that define the interactive behavior of the app:

### 6.1 `update_app_state`

- **Triggers:**  
  - A click event on the element with ID `submit-path`.
  - Changes in the `app-state` store.

- **Purpose:**  
  - When a valid input path is provided and a click is registered, it loads the mouse data using `load_raw_data`.
  - If data already exists in the app state, it returns the current state.

- **Output:**  
  Updates the `app-state` with the loaded mouse data.

### 6.2 `update_dropdown_options`

- **Trigger:**  
  Changes in the `app-state` store.

- **Purpose:**  
  - Dynamically creates navigation options for the dropdown based on the available mouse data.
  - Includes static links for Homepage and Grouped Data along with dynamically generated links for each mouse.

- **Output:**  
  Provides an updated list of options for the `mouse-dropdown` component.

### 6.3 `update_dropdown_value`

- **Triggers:**  
  Changes in the URL path (`dcc.Location`) and the current dropdown options.

- **Purpose:**  
  - Sets the dropdown’s current value based on the current URL path.
  - Ensures the dropdown reflects a valid state (or defaults to "None" if the path isn’t recognized).

- **Output:**  
  Updates the dropdown's selected value.

## 7. Server Execution

- **Automatic Browser Launch:**  
  Before running the server, the script pauses briefly (using `time.sleep(1)`) and then opens the default web browser to the local server address (`http://127.0.0.1:8050/`).

- **Server Run:**  
  The app is started using `app.run_server` with debugging turned off and a specified port of 8050.

## 8. How to Run the Application

1. **Prerequisites:**  
   Ensure that Python is installed along with required packages:
   - Dash and its dependencies.
   - `dash_local_react_components` for custom components.

2. **Execution:**  
   Run the `app.py` file:
   ```bash
   python app.py
   ```
   This will automatically launch the application in your default web browser.

3. **Data Directory:**  
   The app expects a valid data directory containing mouse subdirectories. Provide the correct path when prompted (via the `submit-path` input).

## 9. Additional Considerations

- **Base Path Configuration:**  
  The code checks if the application is frozen (e.g., packaged as an executable) and adjusts the base path accordingly.

- **Session Management:**  
  The use of `dcc.Store` components ensures that the application state is maintained across user sessions.

- **Customization:**  
  The application layout and styling can be further customized by modifying the assets (CSS, images) and the custom React component as needed.

---

This documentation serves as a reference for developers and maintainers to understand and work with the `app.py` file in the MouseMemoryGraph project.
