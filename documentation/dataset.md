# Dataset Module Documentation

This documentation provides a detailed overview of the `dataset.py` module, which is responsible for loading, processing, and merging photometry and behavioral datasets. It explains the design, functionality, and integration of the main components, as well as the dynamic data loading used to manage datasets from multiple subjects (mice).

---

## 1. Overview

This module performs several critical tasks:
- **Photometry Data Processing:** Loads raw photometry data, applies time binning, and processes signals using low-pass filtering, smoothing, and normalization via linear baseline correction.
- **Behavioral Data Processing:** Loads behavioral data, processes coordinate values, calculates velocity, and detects freezing behavior using movement thresholds.
- **Data Merging:** Merges photometry and behavioral datasets on a common time axis to facilitate combined analysis.
- **Dynamic Data Loading:** Automatically detects and loads data from multiple mouse folders, enabling scalable analysis across subjects.

---

## 2. Dependencies and Imports

The module leverages several external libraries for data processing and analysis:

- **Pandas (`pd`):** For reading CSV files, data manipulation, and merging datasets.
- **NumPy (`np`):** For numerical operations and array manipulation.
- **Matplotlib (`plt`):** Primarily imported for plotting if needed.
- **SciPy:** Specifically:
  - `scipy.ndimage.convolve1d` for convolution operations.
  - `scipy.signal.butter` and `scipy.signal.filtfilt` for applying low-pass filters.
  - `scipy.interpolate.interp1d` for interpolation tasks.
- **System and OS Modules (`sys`, `os`):** For handling file paths, detecting the execution context (script vs. frozen executable), and managing dynamic data loading.

---

## 3. Module Structure

The file is organized into several key sections:
- **Dynamic Data Loading:** At the end of the file, the module dynamically determines the base path (depending on whether it is running as a script or an executable) and auto-detects mouse folders within a designated data directory.
- **Class Definitions:** The core classes for processing photometry and behavioral data are defined and documented in detail.
  
## 4. Key Classes and Components

### 4.1 PhotometryDataset

**Purpose:**  
This class is designed for loading and processing photometry data. It performs several preprocessing steps including:
- **Time Binning:** Groups data into fixed time intervals.
- **Low-Pass Filtering:** Removes high-frequency noise using a Butterworth filter.
- **Signal Smoothing:** Applies a smoothing function to reduce transients.
- **Normalization:** Normalizes the photometry signals using linear baseline correction, resulting in computed `zdFF` values.

**Key Methods:**
- `__init__`: Loads the CSV file, renames columns, bins data, and applies low-pass filtering.
- `bin_data`: Groups data based on a rounded time column.
- `low_pass_filter`: Applies a Butterworth filter to a data series.
- `smooth_signal`: Smooths a one-dimensional array using a specified window.
- `linear_baseline`: Computes a linear baseline using polynomial fitting.
- `normalize_signal`: Normalizes signals via baseline correction and standardization.

### 4.2 BehaviorDataset

**Purpose:**  
This class handles the loading and processing of behavioral data. Its main functions include:
- Converting coordinate data to numerical values.
- Applying convolution to smooth positional data.
- Calculating velocity based on differences in positions.
- Detecting freezing behavior based on computed velocity thresholds.

**Key Methods:**
- `__init__`: Loads the CSV file, processes coordinate columns, calculates velocity, and determines freezing episodes.
- `calculate_velocity`: Computes velocity from differences in x and y coordinates.
- `detect_freezing`: Determines freezing intervals using a moving window average of velocity.

### 4.3 MergeDatasets

**Purpose:**  
This class merges photometry and behavioral datasets based on a common time column, enabling synchronized analysis of both data types.

**Key Methods:**
- `__init__`: Merges photometry and behavioral data on the "Time(s)" column, aligning both datasets in time.
- `get_freezing_intervals`: Identifies intervals of freezing by detecting changes in the freezing indicator and merging nearby intervals.
- `get_epoch_data`: Extracts time epochs around specific events for further analysis.
- `get_epoch_average`: Computes average signals before and after each event.
- `add_event`: Incorporates additional behavioral events into the merged dataset.
- `to_dict` and `from_dict`: Enable conversion between a dictionary representation and a `MergeDatasets` instance.

---

## 5. Usage and Integration

- **Photometry Processing:**  
  Create an instance of `PhotometryDataset` by providing the CSV file path and, if needed, custom parameters for column mapping and filtering.
  
- **Behavioral Analysis:**  
  Use `BehaviorDataset` to load behavior data, compute velocity, and detect freezing events.
  
- **Data Merging:**  
  Instantiate `MergeDatasets` with the processed photometry and behavior datasets. The merged dataset can then be used for extracting epochs, computing averages, or other analyses relevant to behavioral events.

- **Dynamic Data Loading:**  
  The module automatically detects and loads data from multiple mouse folders, making it suitable for large-scale studies.

---

## 6. Extensibility

The module is designed to be extensible:
- Additional signal processing methods can be incorporated into `PhotometryDataset`.
- More sophisticated behavioral metrics or event detection methods can be added to `BehaviorDataset`.
- Custom merging strategies or epoch extraction routines can be implemented in `MergeDatasets`.

Developers are encouraged to extend these classes to fit the specific needs of their analyses.