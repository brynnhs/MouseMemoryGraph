import pandas as pd
import matplotlib.pyplot as plt

# Load data
def load_photometry_data(file_path):
    df = pd.read_csv(file_path).rename(columns={
        "AIn-1 - Dem (AOut-1)": "ACC control",
        "AIn-1 - Dem (AOut-2)": "ACC 465",
        "AIn-2 - Dem (AOut-1)": "ADN control",
        "AIn-2 - Dem (AOut-2)": "ADN 465"
    })
    return df.dropna()  # Drop NaN values for cleaner visualization

# Plot photometry signals
def plot_photometry_signals(df, time_limit=10):
    subset = df[df["Time(s)"] <= time_limit]
    
    # Plot ACC signals
    plt.figure(figsize=(12, 6))
    plt.plot(subset["Time(s)"], subset["ACC control"], label="ACC control", alpha=0.7)
    plt.plot(subset["Time(s)"], subset["ACC 465"], label="ACC 465", alpha=0.7)
    plt.xlabel("Time (s)")
    plt.ylabel("Signal Intensity")
    plt.title("ACC Signals Over First 10 Seconds")
    plt.legend()
    plt.show()
    
    # Plot ADN signals
    plt.figure(figsize=(12, 6))
    plt.plot(subset["Time(s)"], subset["ADN control"], label="ADN control", alpha=0.7)
    plt.plot(subset["Time(s)"], subset["ADN 465"], label="ADN 465", alpha=0.7)
    plt.xlabel("Time (s)")
    plt.ylabel("Signal Intensity")
    plt.title("ADN Signals Over First 10 Seconds")
    plt.legend()
    plt.show()

# Example usage
if __name__ == "__main__":
    file_path = "/Users/brynnharrisshanks/Documents/GitHub/MouseMemoryGraph/data/cfc_2046.csv"
    df_clean = load_photometry_data(file_path)
    plot_photometry_signals(df_clean)