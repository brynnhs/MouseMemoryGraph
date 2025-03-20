# Using the Dash App

Follow these instructions to set up and run this Dash-based application with **Visual Studio Code** as your primary development environment, and **Anaconda** (or Miniconda) for managing your Python environment. The dependencies for this project are defined in `requirements.txt` and will be automatically installed during environment creation.

---

## 1. Download & Install Visual Studio Code

1. **Download Visual Studio Code**:  
   Visit [Visual Studio Code](https://code.visualstudio.com/) and download the installer for your operating system.

2. **Install Visual Studio Code**:  
   Follow the installation instructions provided on the website for your OS.

---

## 2. Download & Install Anaconda

1. **Download Anaconda**:  
   Visit [the official Anaconda website](https://www.anaconda.com/products/distribution) and download the latest Anaconda installer for your operating system (Windows, macOS, or Linux).

2. **Install Anaconda**:  
   Follow the on-screen instructions to install Anaconda.  
   - On Windows, you’ll typically use the GUI installer.
   - On macOS/Linux, you can use the `.pkg` file or a command-line installer.

---

## 3. Set Up Your Python Environment in VS Code

1. **Open Your Project in VS Code**:  
   - Launch Visual Studio Code.
   - Go to `File > Open Folder...` and select the root folder of your project (e.g., `MOUSEMEMORYGRAPH/`).


2. **Select Your Python Interpreter in VS Code**:  
   - Press `Command+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux) to open the Command Palette.
   - Type `Python: Select Interpreter` and hit Enter.
   - Choose the interpreter associated with your new environment (e.g., `myenv`).

---

## 4. Clone or Download the Repository

1. **Clone via Git**:
   ```bash
   git clone https://github.com/yourusername/MOUSEMEMORYGRAPH.git
   cd MOUSEMEMORYGRAPH
   ```
   or

2. **Download ZIP**:
   - Download the project as a `.zip` file from GitHub.
   - Unzip it, then open the folder in VS Code.

---

## 5. Create a Virtual Environment with Dependencies from requirements.txt

Instead of manually installing dependencies, use Visual Studio Code’s integrated feature to create a virtual environment that automatically installs the dependencies listed in `requirements.txt`.

1. **Open the Command Palette**:  
   Press `Command+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux).

2. **Run "Python: Create Environment"**:  
   Type `Python: Create Environment` and select it. 
   - Choose the Python version you want to use (for example, Python 3.9).
   - When prompted, select the option to install dependencies from `requirements.txt`.

3. **Wait for Environment Creation**:  
   VS Code will create a new virtual environment and automatically install all dependencies defined in `requirements.txt`. 
   Once completed, ensure that the new environment is active by checking the selected interpreter in the bottom left corner of VS Code.

---

## 6. Run the Application

1. **Run from the Integrated Terminal in VS Code**:
   ```bash
   python code/app.py
   ```
   Alternatively, you can use the provided scripts:
   - For macOS/Linux:
     ```bash
     ./run_app.sh
     ```
   - For Windows:
     ```bash
     run_app.bat
     ```

2. **Access the App**:
    The app should launch a browser itself, but if it doesn't, open your web browser and navigate to `http://127.0.0.1:8050` (or the URL displayed in your terminal) to view the Dash interface.

---

## 8. Additional Resources

- [Visual Studio Code Documentation](https://code.visualstudio.com/docs)
- [Anaconda Documentation](https://docs.anaconda.com/anaconda/)
- [Conda Environments Guide](https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html)
- [Dash Official Documentation](https://dash.plotly.com/)

Feel free to adjust these instructions as needed for your setup.
