import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve1d
from scipy.signal import butter, filtfilt
from scipy.interpolate import interp1d

class PhotometryDataset():
    """
    Class for loading and processing photometry data
    
    Args:
        file_path (str): Path to the photometry data file
        column_map (dict): Dictionary mapping original column names to signal and control names.
            The control (405nm) should be named ".control" and the signal (465nm) should be named ".signal"

        bin_size (float): Size of the time bins for data binning in seconds
        cutoff (float): Cutoff frequency for low-pass filter
        fps (int): Sampling frequency of the data in Hz
    """
    def __init__(self,
                 file_path,
                 column_map={"AIn-1 - Dem (AOut-1)": "ACC.control",
                             "AIn-1 - Dem (AOut-2)": "ACC.signal",
                             "AIn-2 - Dem (AOut-1)": "ADN.control",
                             "AIn-2 - Dem (AOut-2)": "ADN.signal"},
                 ttl_col='AOut-1',
                 bin_size=0.01,
                 cutoff=1.7,
                 fps=100):
        
        self.df = pd.read_csv(file_path).rename(columns=column_map)
        self.df = self.df.dropna() #this will shift the time
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
        Bin data at specified time interval
        """
        agg = {self.ttl_col: 'min'} # aggregate using mean
        for col in column_map.values():
            agg[col] = "mean"

        df["Time_bin"] = df["Time(s)"].round(2)  # Create a new column for binning
        df_binned = df.groupby("Time_bin").agg(agg).reset_index()
        
        df_binned.rename(columns={"Time_bin": "Time(s)"}, inplace=True)  # Rename back

        return df_binned

    def low_pass_filter(self, data, cutoff=1.7, fs=100):
        """
        Apply low-pass filter to data using Butterworth filter
        """
        nyquist = 0.5 * fs
        norm_cutoff = cutoff / nyquist
        b, a = butter(2, norm_cutoff, btype='low', analog=False)

        return filtfilt(b, a, data) 
    
    def smooth_signal(self, x, window_len=10,window='flat'):

        """smooth the data using a window with requested size.
        
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        The code taken from: https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
        
        input:
            x: the input signal 
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                    'flat' window will produce a moving average smoothing.

        output:
            the smoothed signal        
        """

        if x.ndim != 1:
            raise(ValueError, "smooth only accepts 1 dimension arrays.")
        if x.size < window_len:
            raise(ValueError, "Input vector needs to be bigger than window size.")
        if window_len<3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise(ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
        
        s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]

        if window == 'flat': # Moving average
            w=np.ones(window_len,'d')
        else:
            w=eval('np.'+window+'(window_len)')

        y=np.convolve(w/w.sum(),s,mode='valid')

        return y[(int(window_len/2)-1):-int(window_len/2)]
    
    def linear_baseline(self, signal):
        x = np.arange(len(signal))  # Create x-values (indices of the signal)
        coeffs = np.polyfit(x, signal, deg=1)  # Fit a linear function (degree 1)
        baseline = np.polyval(coeffs, x)  # Evaluate the polynomial at x
        return baseline
    
    def normalize_signal(self):   
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

            remove=0
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
    Class for loading and processing behavioral data
    
    Args:
        file_path (str): Path to the behavior data file
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
        use mean velocity over window_width to detect freezing if below threshold
        """
        head_freezing = np.zeros(len(velocity))
        for i in range(window_width, len(velocity)):
            if velocity[max(i-(window_width//2), 0):min(i+(window_width//2), len(velocity))].mean() < threshold:
                head_freezing[i] = 1
        kernel = np.ones(10)
        head_freezing = convolve1d(head_freezing, kernel, mode='constant')
        return head_freezing > 2
    

class MergeDatasets():
    """
    Class for merging photometry and behavior data
    
    Args:
        photometry (PhotometryDataset): Photometry dataset
        behavior (BehaviorDataset): Behavior dataset
    """
    def __init__(self, photometry, behavior):

        # check that 'Time(s)' is in both dataframes with assert
        assert 'Time(s)' in photometry.df.columns, "Time(s) not in photometry dataframe"
        assert 'Time(s)' in behavior.df.columns, "Time(s) not in behavior dataframe"

        # check that AOut-1 is in photometry dataframe
        assert 'AOut-1' in photometry.df.columns, "AOut-1 not in photometry dataframe"

        # merge dataframes on 'Time(s)' and round to 2 decimal places
        photometry.df['Time(s)'] = photometry.df['Time(s)'].round(2)
        behavior.df['Time(s)'] = behavior.df['Time(s)'].round(2)

        self.df = pd.merge(photometry.df, behavior.df, on="Time(s)", how="outer")
        self.fps = min(photometry.fps, behavior.fps)

        # drop rows with NaN values
        self.df = self.df.dropna()

        # get rid of rows with 'AOut-1' == 0
        self.df = self.df[self.df['AOut-1'] != 0]
        self.df = self.df.reset_index()

    def get_freezing_intervals(self):
        onsets = self.df[self.df['freezing'].diff() == 1].index
        offsets = self.df[self.df['freezing'].diff() == -1].index
        intervals = list(zip(onsets, offsets))
        return intervals
    
    def get_epoch_data(self, intervals, column, duration=1, type='on'):
        """
        Get photometry data for each epoch with a specified duration in seconds

        - filter out all intervals that are shorter than the specified duration
        - filter out all overlapping intervals
        """
        frames = int(duration * self.fps)
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
        intervals = [intervals[i] for i in range(len(intervals)) if diff[i] > 2 * frames]

        if type == 'on':
            epochs = [((int(on-frames), int(on+frames)), intervals[i]) for i,(on, off) in enumerate(intervals)  if off - on > frames]
        elif type == 'off':
            epochs = [((int(off-frames), int(off+frames)), intervals[i]) for i,(on, off) in enumerate(intervals)  if off - on > frames]
        else:
            # throw an error
            print("Type not recognized")
        #filter out epochs that are out of bounds
        epochs = [((beg, end), inter) for (beg, end), inter in epochs if beg > 0 and end < max]
        epochs = [[(beg, end), inter, self.df[column+'.zdFF'][beg:end]] for (beg, end), inter in epochs]
        
        return epochs

    
    
photometry = PhotometryDataset("/Users/julian/Documents/daten/STUDIUM Master/FabLab 2025/raw data - 04 Feb/cfc_2046.csv")
behavior = BehaviorDataset("/Users/julian/Documents/daten/STUDIUM Master/FabLab 2025/Codebase/MouseMemoryGraph/data/a2024-11-01T14_30_53DLC_resnet50_fearbox_optoJan27shuffle1_100000.csv")

df = photometry.normalize_signal()
print(df.head())
print(df['Time(s)'])
print(behavior.df.head())

merged = MergeDatasets(photometry, behavior)
print(merged.df.head())

#start an end time
print(merged.df['Time(s)'].iloc[0], merged.df['Time(s)'].iloc[-1])

intervals = merged.get_freezing_intervals()
print(intervals)
epochs = merged.get_epoch_data(intervals, 'ACC', type='off')
print(epochs)

