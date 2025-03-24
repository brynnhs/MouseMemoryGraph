import os
import pandas as pd

# Define the path to the data folder
data_folder = './data'

# Walk through the data folder and its subfolders
for root, dirs, files in os.walk(data_folder):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        
        # Check if the file is a CSV
        if file_name.endswith('.csv'):
            print(f"Processing file: {file_path}")
            
            # Load the CSV
            df = pd.read_csv(file_path)
            
            # Downsample rows (e.g., keep every 10th row)
            df_small = df.iloc[::10, :]
            
            # Overwrite the original file with the downsampled data
            df_small.to_csv(file_path, index=False)
            print(f"Overwritten file with downsampled data: {file_path}")