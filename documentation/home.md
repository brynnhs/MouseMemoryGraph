# Home Page Module Documentation

This document provides an overview and detailed explanation of the `home.py` module. The module defines the homepage of the Mouse Memory Graph App, including layout components, data stores, input elements, and callback functions to manage events and user interactions.

---

## 1. Overview

The `home.py` module serves as the homepage for the application. It:
- Registers the homepage route ("/") using Dash.
- Defines the layout of the page, including input fields for folder paths, buttons, and components to display and update event data.
- Loads a custom React component (`EventSelection`) for selecting events.
- Implements callbacks for updating event stores, modifying interval data, and handling folder submissions.

---

## 2. Dependencies and Imports

The module leverages the following libraries and components:
- **Dash:** The core framework for building web applications.
- **Dash HTML Components and Core Components (`html`, `dcc`):** Used to build the layout.
- **Dash Dependencies (`Input`, `Output`, `State`):** For creating reactive callbacks.
- **Dash Table:** Used to display and edit interval data in a table format.
- **dash_local_react_components:** Used to load custom React components (e.g., `EventSelection`).

Additionally, the module imports and registers its own page using `dash.register_page`.

---

## 3. Layout Structure

The homepage layout is defined within a single `html.Div` component that includes:
- **Data Stores:**  
  - `dcc.Store(id='selected-event')` to hold the currently selected event.
- **Folder Path Input and Submit Button:**  
  - An input field (`dcc.Input`) for the user to enter a folder path.
  - A submit button (`html.Button`) to trigger folder path submission.
- **Welcome Message and Folder Structure Information:**  
  - A header (`html.H1`) welcoming the user.
  - A paragraph (`html.P`) with navigation instructions.
  - An example folder structure presented inside a `<pre>` tag.
- **Event Selection Section:**  
  - The custom React component `EventSelection` is used to let the user choose an event.
  - A section to display the selected event and a button to add new intervals.
- **Styling:**  
  - Consistent use of white backgrounds, rounded borders, and padding to maintain a clean design.

---

## 4. Callbacks

The module defines several callback functions to handle user interactions:

### 4.1 Update Event Store

**Purpose:**  
Updates the event store data when a new event is selected via the `EventSelection` component.

**Details:**
- If the selected event is new, it adds an initial interval (defaulted to `(0, 0)`).
- It also updates the state of the "Add Interval" button (enabling or disabling it based on the event selection).

### 4.2 Update Selected Event Output

**Purpose:**  
Updates the display output for the selected event's interval data.  
**Details:**  
- When the "Add Interval" button is clicked, a new interval `(0, 0)` is appended.
- The interval data is rendered using a Dash DataTable with editable and deletable rows.

### 4.3 Update Interval Table

**Purpose:**  
Synchronizes changes in the interval table with the event store.

**Details:**  
- Any modifications in the table data update the corresponding event's interval data in the event store.

### 4.4 Populate Event Selection Options

**Purpose:**  
Generates dropdown options for the `EventSelection` component based on the keys from the event store.

**Details:**  
- Converts the keys from the event store into a list of options for the event selection dropdown.

### 4.5 Update Selected Folder

**Purpose:**  
Updates the stored folder path based on the user’s input and the submit button click.

---

## 5. Usage

To integrate and use the homepage module:
1. **Route Registration:**  
   The module registers itself as the home page with the path `'/'`.
2. **Launching the App:**  
   When the app is launched, this module's layout is rendered, presenting the user with input controls to specify folder paths and select events.
3. **Event Handling:**  
   The defined callbacks manage updates to event data, interval modifications, and folder submissions, ensuring a dynamic and interactive homepage experience.

---

## 6. Customization

Developers can extend or modify the homepage functionality by:
- Adjusting the layout to add more input fields or visual elements.
- Modifying callback logic to handle additional event types or interactions.
- Customizing the styling for a better user interface experience.

This documentation is intended to serve as a comprehensive reference for understanding and modifying the `home.py` module. For further customization, review the individual callback functions and layout components in the source code.