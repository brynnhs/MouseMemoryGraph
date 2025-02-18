import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from scipy.interpolate import interp1d

# Load data
def load_photometry_data(file_path):
    df = pd.read_csv(file_path).rename(columns={
        "AIn-1 - Dem (AOut-1)": "ACC control",
        "AIn-1 - Dem (AOut-2)": "ACC 465",
        "AIn-2 - Dem (AOut-1)": "ADN control",
        "AIn-2 - Dem (AOut-2)": "ADN 465"
    })
    return df.dropna()

# Bin data at 10ms (100Hz)
def bin_data(df, bin_size=0.01):
    df["Time_bin"] = df["Time(s)"].round(2)  # Create a new column for binning
    df_binned = df.groupby("Time_bin").agg({  # Aggregate using mean
        "ACC control": "mean",
        "ACC 465": "mean",
        "ADN control": "mean",
        "ADN 465": "mean"
    }).reset_index()
    
    df_binned.rename(columns={"Time_bin": "Time(s)"}, inplace=True)  # Rename back
    return df_binned

# Apply low-pass filter at 1.7Hz
def low_pass_filter(data, cutoff=1.7, fs=100):
    nyquist = 0.5 * fs
    norm_cutoff = cutoff / nyquist
    b, a = butter(2, norm_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

# Normalize signals using dF/F
def normalize_signal(df, baseline_duration=180):
    baseline_idx = df[df["Time(s)"] <= baseline_duration].index
    for col in ["ACC control", "ACC 465", "ADN control", "ADN 465"]:
        baseline_median = df.loc[baseline_idx, col].median()
        df[col] = (df[col] - baseline_median) / baseline_median
    return df

# Epoch data every 4 seconds
def epoch_data(df, epoch_length=4):
    epochs = []
    time_bins = np.arange(0, df["Time(s)"].max(), epoch_length)
    
    for start_time in time_bins:
        epoch = df[(df["Time(s)"] >= start_time) & (df["Time(s)"] < start_time + epoch_length)].copy()
        if not epoch.empty:
            epoch["Epoch"] = len(epochs)  # Assign an epoch number
            epochs.append(epoch)
    
    return epochs

# Compute grand average epoch
def grand_average_epoch(epochs, epoch_length=4, target_fs=100):
    """
    Compute the grand average of all 4-second epochs.
    Ensures all epochs are aligned and resampled to a common time grid.
    
    Parameters:
    - epochs: list of DataFrames containing individual epochs
    - epoch_length: length of each epoch in seconds
    - target_fs: target sampling frequency (default 100 Hz)
    
    Returns:
    - grand_avg: DataFrame containing the grand average of all epochs
    """
    num_samples = epoch_length * target_fs  # Fixed number of samples per epoch
    time_grid = np.linspace(0, epoch_length, num_samples)  # Standardized time grid

    interpolated_epochs = []

    for epoch in epochs:
        # Normalize time within each epoch
        epoch["Relative Time"] = epoch["Time(s)"] - epoch["Time(s)"].iloc[0]
        
        # Interpolate each column to the standard time grid
        interpolated_data = {}
        for col in ["ACC control", "ACC 465", "ADN control", "ADN 465"]:
            interp_func = interp1d(epoch["Relative Time"], epoch[col], kind="linear", fill_value="extrapolate")
            interpolated_data[col] = interp_func(time_grid)
        
        interpolated_epochs.append(pd.DataFrame(interpolated_data, index=time_grid))

    # Compute grand average across all epochs
    grand_avg = pd.concat(interpolated_epochs).groupby(level=0).mean()
    return grand_avg

# Main function to process, epoch, and plot photometry signals
def process_and_plot(file_path, time_limit=10):
    df = load_photometry_data(file_path)
    df = bin_data(df)
    
    for col in ["ACC control", "ACC 465", "ADN control", "ADN 465"]:
        df[col] = low_pass_filter(df[col])
    
    df = normalize_signal(df)
    
    # Epoch the data
    epochs = epoch_data(df, epoch_length=4)
    grand_avg = grand_average_epoch(epochs)
    
    # Plot Grand Average with Corrected X-Axis (4 seconds)
    plt.figure(figsize=(12, 6))
    plt.plot(grand_avg.index, grand_avg["ACC control"], label="ACC control (Grand Avg)", alpha=0.7)
    plt.plot(grand_avg.index, grand_avg["ACC 465"], label="ACC 465 (Grand Avg)", alpha=0.7)
    plt.plot(grand_avg.index, grand_avg["ADN control"], label="ADN control (Grand Avg)", alpha=0.7)
    plt.plot(grand_avg.index, grand_avg["ADN 465"], label="ADN 465 (Grand Avg)", alpha=0.7)
    plt.xlabel("Time (s)")
    plt.ylabel("dF/F")
    plt.title("Grand Average of 4-Second Epochs")
    plt.legend()
    plt.xlim([0, 4])  # Force x-axis to show full 4 seconds
    plt.show()

# Example usage
if __name__ == "__main__":
    file_path = "/Users/brynnharrisshanks/Documents/GitHub/MouseMemoryGraph/data/cfc_2046.csv"
    process_and_plot(file_path)

