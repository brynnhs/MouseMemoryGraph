## 1. Incorrect channel names 

-   The dashboard expects specifc channel names to work correctly. Please go into your csv and edit your channel names to match the following:

    channel1_410 = ACC control data column 
    channel2_410 = ACC signal data column 
    channel1_470 = ADN control data column 
    channel2_470 = ADN signal data column 
    DI/O-1 = Digital input/output signal to mark the start of the behavioural data. Used to synchronise the photometry and behavioural data.

    *Note:* The original use case of the dash was to compare ADN and ACC, but you can look at any 2 parts of the brain

## 2. Incorrect file structure

    The dashboard expects that your data files are structured as follows:
    │-- data/                    
│   ├── mousename_group/              
│   │   ├── mousename_recording.csv      # Photometry data
│   │   ├── mousename_behavior.csv      # Behavioral classification
│   ├── mouse2/              # Additional datasets

- **Naming Conventions:**  
  The folder containing an individual mouse’s data should be named `mousename_group`, where `mousename` is their ID and `group` is the experimental condition.  
  For example:  
  - `h149_remote.csv` vs. `h149_recent.csv`
- **File Requirements:**  
  Each mouse folder must contain two files: one for photometry data (e.g., `h149_recording.csv`) and one for behavioral classification (e.g., `h149_behavior.csv`).

## 3. Mouse and average page not appearing on the menu drop-down. 

-   You must click **"Process"** after you enter the path to the data on your computer. 

## 4. New events not appearing on the analysis

-   You must click **"Save"** for each new event and interval added on the homepage.

## 5. Excluding a mouse from the group analysis

- To exclude mice from the group analysis either do not assign them a group on their individual mouse page or add a new group called "Exclude" and assign the mice you'd like to exclude to that group. 

## 6. Slow dashboard

-   The dashboard is a bit slow. This is because of how we are loading and processing the data. 
-   If the tab of the window says **"Updating.."**, then please be patient and wait for it to finish updating, it should only take 5-15 seconds.