import pandas as pd
import numpy as np
import os
from scipy.ndimage import convolve1d
from scipy.signal import butter, filtfilt
import sys

class PhotometryDataset:
    """
    Class for loading and processing photometry data.
    """
    def __init__(self, file_path,
                 column_map={"AIn-1 - Dem (AOut-1)": "ACC.control",
                             "AIn-1 - Dem (AOut-2)": "ACC.signal",
                             "AIn-2 - Dem (AOut-1)": "ADN.control",
                             "AIn-2 - Dem (AOut-2)": "ADN.signal"},
                 ttl_col='AOut-1',
                 bin_size=0.01,
                 cutoff=1.7,
                 fps=100):
        
        self.df = pd.read_csv(file_path).rename(columns=column_map)
        self.df.dropna(inplace=True)
        self.column_map = column_map
        self.ttl_col = ttl_col
        self.bin_size = bin_size
        self.cutoff = cutoff
        self.fps = fps

        self.df = self.bin_data(self.df, column_map, bin_size=self.bin_size)
        
        for col in column_map.values():
            self.df[col] = self.low_pass_filter(self.df[col])

    def bin_data(self, df, column_map, bin_size=0.01):
        """Bin data at specified time interval."""
        agg = {self.ttl_col: 'min'}
        for col in column_map.values():
            agg[col] = "mean"

        df["Time_bin"] = df["Time(s)"].round(2)
        df_binned = df.groupby("Time_bin").agg(agg).reset_index()
        df_binned.rename(columns={"Time_bin": "Time(s)"}, inplace=True)
        return df_binned

    def low_pass_filter(self, data, cutoff=1.7, fs=100):
        """Apply low-pass filter to data using Butterworth filter."""
        nyquist = 0.5 * fs
        norm_cutoff = cutoff / nyquist
        b, a = butter(2, norm_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    def normalize_signal(self):
        """Normalize signals using baseline correction."""
        regions = list(set([col.split(".")[0] for col in self.column_map.values()]))
        df_normalized = self.df.copy()

        for reg in regions:
            raw_signal = self.df[reg + ".signal"]
            raw_control = self.df[reg + ".control"]

            z_control = (raw_control - np.median(raw_control)) / np.std(raw_control)
            z_signal = (raw_signal - np.median(raw_signal)) / np.std(raw_signal)
            zdFF = z_signal - z_control

            df_normalized[reg + ".zdFF"] = zdFF
            df_normalized[reg + ".signal"] = z_signal
            df_normalized[reg + ".control"] = z_control

        self.df = df_normalized
        return df_normalized

class BehaviorDataset:
    """
    Class for loading and processing behavioral data.
    """
    def __init__(self, file_path, fps=30):
        dataframe = pd.read_csv(file_path, header=1)
        dataframe = dataframe.drop(dataframe.index[0])

        self.fps = fps
        dataframe['Time(s)'] = np.arange(0, len(dataframe)/fps, 1/fps)
        self.df = dataframe
        self.df['freezing'] = self.detect_freezing(self.calculate_velocity(dataframe))

    def calculate_velocity(self, df):
        """Calculate movement velocity from head and tail positions."""
        head_velocity = np.sqrt(np.diff(df['head'].astype(float))**2 + np.diff(df['head.1'].astype(float))**2)
        tail_velocity = np.sqrt(np.diff(df['middle tail'].astype(float))**2 + np.diff(df['middle tail.1'].astype(float))**2)
        return np.append((head_velocity + tail_velocity) / 2, 0)

    def detect_freezing(self, velocity, window_width=5, threshold=6):
        """Detect freezing behavior based on velocity threshold."""
        freezing = np.zeros(len(velocity))
        for i in range(window_width, len(velocity)):
            if velocity[max(i-window_width//2, 0):min(i+window_width//2, len(velocity))].mean() < threshold:
                freezing[i] = 1
        return freezing

class MergeDatasets:
    """
    Class for merging photometry and behavior data.
    """
    def __init__(self, photometry, behavior):
        assert 'Time(s)' in photometry.df.columns, "Time(s) not in photometry dataframe"
        assert 'Time(s)' in behavior.df.columns, "Time(s) not in behavior dataframe"

        photometry.df['Time(s)'] = photometry.df['Time(s)'].round(2)
        behavior.df['Time(s)'] = behavior.df['Time(s)'].round(2)

        self.df = pd.merge(photometry.df, behavior.df, on="Time(s)", how="outer").dropna()

        # Remove unwanted rows
        if 'AOut-1' in self.df.columns:
            self.df = self.df[self.df['AOut-1'] != 0]

# --- Dynamic Data Loading for Multiple Mice ---

if getattr(sys, 'frozen', False):
    # Running as an executable
    base_path = sys._MEIPASS
else:
    # Running as a script
    base_path = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_path, "../data")  # Go to root of MouseMemoryGraph
data_dir = os.path.abspath(data_dir)

# Auto-detect all mouse folders
mouse_folders = [f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f))]

# Dictionary to store datasets
mouse_data = {}

for mouse in mouse_folders:
    photometry_path = os.path.join(data_dir, mouse, "cfc_2046.csv")
    behavior_path = os.path.join(data_dir, mouse, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")

    if os.path.exists(photometry_path) and os.path.exists(behavior_path):
        photometry = PhotometryDataset(photometry_path)
        behavior = BehaviorDataset(behavior_path)
        photometry.normalize_signal()
        merged = MergeDatasets(photometry, behavior).df
        mouse_data[mouse] = merged  # Store the merged dataframe

# Print available mice for verification
print(f"Loaded data for {len(mouse_data)} mice: {list(mouse_data.keys())}")