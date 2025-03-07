import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve1d
from scipy.signal import butter, filtfilt
from scipy.interpolate import interp1d
import sys
import os

class PhotometryDataset():
    """
    Class for loading and processing photometry data
    
    Args:
        file_path (str): Path to the photometry data file
        column_map (dict): Dictionary mapping original column names to signal and control names.
            The control (405nm) should be named ".control" and the signal (465nm) should be named ".signal"
        ttl_col (str): Column name for TTL signal
        bin_size (float): Size of the time bins for data binning in seconds
        cutoff (float): Cutoff frequency for low-pass filter
        fps (int): Sampling frequency of the data in Hz
    """
    def __init__(self,
                 file_path,
                 column_map={"channel1_410": "ACC.control",
                             "channel2_410": "ACC.signal",
                             "channel1_470": "ADN.control",
                             "channel2_470": "ADN.signal"},
                 ttl_col='DI/O-1',
                 bin_size=0.01,
                 cutoff=1.7,
                 fps=100):
        
        self.df = pd.read_csv(file_path).rename(columns=column_map)
        self.df = self.df.dropna()  # this will shift the time
        self.column_map = column_map
        self.ttl_col = ttl_col

        self.bin_size = bin_size
        self.cutoff = cutoff
        self.fps = fps

        self.df = self.bin_data(self.df, column_map, bin_size=self.bin_size)

        # Apply low-pass filter to each signal
        for col in column_map.values():
            self.df[col] = self.low_pass_filter(self.df[col])

    def bin_data(self, df, column_map, bin_size=0.01):
        """
        Bin data at specified time interval.
        """
        agg = {self.ttl_col: 'min'}  # aggregate using mean
        for col in column_map.values():
            agg[col] = "mean"

        df["Time_bin"] = df["Time(s)"].round(2)  # Create a new column for binning
        df_binned = df.groupby("Time_bin").agg(agg).reset_index()
        df_binned.rename(columns={"Time_bin": "Time(s)"}, inplace=True)  # Rename back

        return df_binned

    def low_pass_filter(self, data, cutoff=1.7, fs=100):
        """
        Apply low-pass filter to data using Butterworth filter.
        """
        nyquist = 0.5 * fs
        norm_cutoff = cutoff / nyquist
        b, a = butter(2, norm_cutoff, btype='low', analog=False)

        return filtfilt(b, a, data) 
    
    def smooth_signal(self, x, window_len=10, window='flat'):
        """
        Smooth the data using a window with requested size.

        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the beginning and end part of the output signal.
        (Code adapted from https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html)
        """
        if x.ndim != 1:
            raise(ValueError, "smooth only accepts 1 dimension arrays.")
        if x.size < window_len:
            raise(ValueError, "Input vector needs to be bigger than window size.")
        if window_len < 3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise(ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
        
        s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]
        if window == 'flat':  # Moving average
            w = np.ones(window_len, 'd')
        else:
            w = eval('np.' + window + '(window_len)')

        y = np.convolve(w/w.sum(), s, mode='valid')
        return y[(int(window_len/2)-1):-int(window_len/2)]
    
    def linear_baseline(self, signal):
        x = np.arange(len(signal))  # Create x-values (indices of the signal)
        coeffs = np.polyfit(x, signal, deg=1)  # Fit a linear function (degree 1)
        baseline = np.polyval(coeffs, x)  # Evaluate the polynomial at x
        return baseline
    
    def normalize_signal(self):   
        """
        Normalize signals using a linear baseline correction.
        """
        # go through the columns and take each pair of signal and control
        columns = list(self.column_map.values())
        # find all unique prefixes
        region = list(set([col.split(".")[0] for col in columns]))
        df_normalized = self.df.copy()

        for reg in region:
            raw_signal = self.smooth_signal(self.df[reg + ".signal"])
            raw_control = self.smooth_signal(self.df[reg + ".control"])

            # Compute linear baselines
            s_base = self.linear_baseline(raw_signal)
            c_base = self.linear_baseline(raw_control)

            remove = 0
            control = (raw_control[remove:] - c_base[remove:])
            signal = (raw_signal[remove:] - s_base[remove:])  

            z_control = (control - np.median(control)) / np.std(control)
            z_signal = (signal - np.median(signal)) / np.std(signal)

            zdFF = (z_signal - z_control)
            df_normalized[reg + ".zdFF"] = zdFF
            df_normalized[reg + ".signal"] = z_signal
            df_normalized[reg + ".control"] = z_control
        
        self.df = df_normalized
        return df_normalized


class BehaviorDataset():
    """
    Class for loading and processing behavioral data.
    
    Args:
        file_path (str): Path to the behavior data file.
    """
    def __init__(self,
                 file_path,
                 fps=30):
        
        dataframe = pd.read_csv(file_path, header=1)
        dataframe = dataframe.drop(dataframe.index[0])

        self.fps = fps

        dataframe['head_x'] = dataframe['head'].astype(float)
        dataframe['head_y'] = dataframe['head.1'].astype(float)
        dataframe['tail_x'] = dataframe['middle tail'].astype(float)
        dataframe['tail_y'] = dataframe['middle tail.1'].astype(float)
        dataframe['base_x'] = dataframe['base tail'].astype(float)
        dataframe['base_y'] = dataframe['base tail.1'].astype(float)

        kernel = np.ones(60)
        base_convolved_x = convolve1d(dataframe['base_x'], kernel, mode='constant')
        base_convolved_y = convolve1d(dataframe['base_y'], kernel, mode='constant')
        head_convolved_x = convolve1d(dataframe['head_x'], kernel, mode='constant')
        head_convolved_y = convolve1d(dataframe['head_y'], kernel, mode='constant')

        base_velocity = self.calculate_velocity(base_convolved_x, base_convolved_y)
        head_velocity = self.calculate_velocity(head_convolved_x, head_convolved_y)

        velocity = (base_velocity + head_velocity) / 2
        # add missing row   
        velocity = np.append(velocity, velocity[-1])

        # time in seconds
        dataframe['Time(s)'] = np.arange(0, len(dataframe)/fps, 1/fps)

        self.freezing = self.detect_freezing(velocity)
        dataframe['freezing'] = self.freezing
        self.df = dataframe

    def calculate_velocity(self, x, y):
        return np.sqrt(np.diff(x)**2 + np.diff(y)**2)
    
    def detect_freezing(self, velocity, window_width=5, threshold=6):
        """
        Use mean velocity over window_width to detect freezing if below threshold.
        """
        head_freezing = np.zeros(len(velocity))
        for i in range(window_width, len(velocity)):
            if velocity[max(i - (window_width//2), 0):min(i + (window_width//2), len(velocity))].mean() < threshold:
                head_freezing[i] = 1
        kernel = np.ones(10)
        head_freezing = convolve1d(head_freezing, kernel, mode='constant')
        return head_freezing > 2
    

class MergeDatasets():
    """
    Class for merging photometry and behavior data.
    
    Args:
        photometry (PhotometryDataset): Photometry dataset.
        behavior (BehaviorDataset): Behavior dataset.
    """
    def __init__(self, photometry, behavior):
        # check that 'Time(s)' is in both dataframes with assert
        assert 'Time(s)' in photometry.df.columns, "Time(s) not in photometry dataframe"
        assert 'Time(s)' in behavior.df.columns, "Time(s) not in behavior dataframe"

        # check that DI/O-1 is in photometry dataframe
        assert 'DI/O-1' in photometry.df.columns, "DI/O-1 not in photometry dataframe"

        # merge dataframes on 'Time(s)' and round to 2 decimal places
        photometry.df['Time(s)'] = photometry.df['Time(s)'].round(2)
        behavior.df['Time(s)'] = behavior.df['Time(s)'].round(2)

        self.df = pd.merge(photometry.df, behavior.df, on="Time(s)", how="outer")
        self.fps = min(photometry.fps, behavior.fps)
        # drop rows with NaN values
        self.df = self.df.dropna()
        # Optionally filter out rows where DI/O-1 is 0 (currently commented out)
        # self.df = self.df[self.df['DI/O-1'] != 0]
        self.df = self.df.reset_index(drop=True)

    def get_freezing_intervals(self, merge_range=1):
        """
        Get freezing intervals. Merge intervals that are within merge_range seconds of each other.
        """
        onsets = self.df[self.df['freezing'].diff() == 1].index
        offsets = self.df[self.df['freezing'].diff() == -1].index
        intervals = list(zip(onsets, offsets))

        # merge intervals that are within merge_range seconds of each other
        merged = [intervals[0]]
        threshold = merge_range * self.fps

        for start, end in intervals[1:]:
            last_start, last_end = merged[-1]
            # If the gap is less than threshold, merge the intervals
            if start - last_end < threshold:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))

        return merged
    
    def get_epoch_data(self, intervals, column, before=2, after=2, type='on'):
        """
        Get photometry data for each epoch defined by a window around an event.
        
        Args:
            intervals (list): List of (onset, offset) index pairs.
            column (str): Base name of the sensor (e.g. 'ACC' or 'ADN'). The method
                          will use the corresponding column '{column}.zdFF'.
            before (float): Seconds before the event to include.
            after (float): Seconds after the event to include.
            type (str): 'on' to use the onset of the interval, 'off' to use the offset.
            
        Returns:
            epochs (list): A list where each element is a list containing:
                - Tuple (beg, end): the start and end indices of the epoch.
                - Tuple (on, off): the original event interval.
                - The sensor data (as a pandas Series) for the epoch.
        """
        frames_before = int(before * self.fps)
        frames_after = int(after * self.fps)
        max = self.df.index[-1]

        # filter out epochs where the difference between their onsets is less than twice the epoch duration
        if type == 'on':
            diff = np.diff([on for on, off in intervals])
        elif type == 'off':
            diff = np.diff([off for on, off in intervals])
        else:
            # throw an error
            print("Type not recognized")

        diff = np.insert(diff, 0, 0)
        #intervals = [intervals[i] for i in range(len(intervals)) if diff[i] > 2 * frames]

        if type == 'on':
            epochs = [((int(on-frames_before), int(on+frames_after)), intervals[i]) for i,(on, off) in enumerate(intervals)  if off - on > frames_after]
        elif type == 'off':
            epochs = [((int(off-frames_before), int(off+frames_after)), intervals[i]) for i,(on, off) in enumerate(intervals)  if off - on > frames_before]
        else:
            # throw an error
            print("Type not recognized")
        #filter out epochs that are out of bounds
        epochs = [((beg, end), inter) for (beg, end), inter in epochs if beg > 0 and end < max]
        epochs = [[(beg, end), inter, self.df[column+'.zdFF'][beg:end]] for (beg, end), inter in epochs]
        
        return epochs

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

# The following lines are commented out; uncomment and adjust paths as needed
# for mouse in mouse_folders:
#     photometry_path = os.path.join(data_dir, mouse, "cfc_2046.csv")
#     behavior_path = os.path.join(data_dir, mouse, "a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")
# 
#     if os.path.exists(photometry_path) and os.path.exists(behavior_path):
#         photometry = PhotometryDataset(photometry_path)
#         behavior = BehaviorDataset(behavior_path)
#         photometry.normalize_signal()
#         merged = MergeDatasets(photometry, behavior).df
#         mouse_data[mouse] = merged  # Store the merged dataframe

# Print available mice for verification
# print(f"Loaded data for {len(mouse_data)} mice: {list(mouse_data.keys())}")

# Example usage:
# merged = MergeDatasets(photometry, behavior)
# intervals = merged.get_freezing_intervals()
# epochs = merged.get_epoch_data(intervals, 'ACC', before=2, after=2, type='off')