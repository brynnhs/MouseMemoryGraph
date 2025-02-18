from scipy.io import loadmat

# Load the .mat file
mat_data = loadmat("/Users/brynnharrisshanks/Documents/GitHub/MouseMemoryGraph/data/behaviour1/Behavior.mat")

# Print all variable names stored in the .mat file
print(mat_data.keys())