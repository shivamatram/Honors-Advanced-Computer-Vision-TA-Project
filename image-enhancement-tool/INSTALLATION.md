# Installation Guide

## Complete Step-by-Step Setup Instructions

This guide provides detailed instructions for installing and running the **Real-Time Intelligent Image Enhancement & Editing Toolkit** on different operating systems.

---

## Quick Start (Recommended)

### For macOS/Linux:
```bash
# Navigate to project directory
cd image-enhancement-tool

# Run the automatic setup script
chmod +x run.sh
./run.sh
```

### For Windows:
```powershell
# Navigate to project directory
cd image-enhancement-tool

# Run the automatic setup script
run.bat
```

---

## Manual Installation (Step-by-Step)

### Prerequisites Check

Before starting, verify you have:
- Python 3.8 or higher installed
- pip (Python package manager)
- 500MB free disk space
- 4GB RAM minimum

### Step 1: Verify Python Installation

#### On macOS/Linux:
```bash
python3 --version
# Output: Python 3.x.x
```

#### On Windows:
```powershell
python --version
# Output: Python 3.x.x
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

### Step 2: Clone or Download the Project

#### Option A: Using Git
```bash
git clone https://github.com/yourusername/image-enhancement-tool.git
cd image-enhancement-tool
```

#### Option B: Download ZIP
1. Download the ZIP file from the repository
2. Extract it to your desired location
3. Open terminal/command prompt in the extracted folder

### Step 3: Create Virtual Environment

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) prefix in your terminal
```

#### On Windows (Command Prompt):
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) prefix in your terminal
```

#### On Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Upgrade pip

Ensure you have the latest version of pip:

#### On macOS/Linux/Windows:
```bash
pip install --upgrade pip
```

### Step 5: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed streamlit-1.28.1 opencv-python-4.8.1.78 opencv-contrib-python-4.8.1.78 numpy-1.24.3 Pillow-10.0.1
```

### Step 6: Generate Sample Image

```bash
# Generate sample image for testing
python create_sample.py
```

**Expected Output:**
```
Sample image created: sample_images/sample.jpg
```

### Step 7: Run the Application

```bash
# Start the Streamlit application
streamlit run app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://xxx.xxx.x.xxx:8501
```

---

## Accessing the Application

Once the application is running:

1. **Open your web browser**
2. **Navigate to**: `http://localhost:8501`
3. **Upload an image** to get started

The application will load in your browser with:
- Sidebar controls on the left
- Main content area with image display
- Real-time preview of enhancements

---

## Virtual Environment Management

### Activate Virtual Environment Anytime

#### On macOS/Linux:
```bash
source venv/bin/activate
```

#### On Windows (Command Prompt):
```cmd
venv\Scripts\activate
```

#### On Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Delete Virtual Environment

```bash
# On macOS/Linux
rm -rf venv

# On Windows (Command Prompt)
rmdir /s venv

# On Windows (PowerShell)
Remove-Item -Recurse -Force venv
```

---

## Troubleshooting Installation

### Error: "Python not found"

**Solution:**
- Install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal/command prompt

### Error: "pip command not found"

**Solution:**
```bash
# Try using pip3 instead
python3 -m pip install -r requirements.txt

# Or upgrade pip
python -m ensurepip --upgrade
```

### Error: "Permission denied" (macOS/Linux)

**Solution:**
```bash
# Make scripts executable
chmod +x run.sh
chmod +x create_sample.py

# Then run
./run.sh
```

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'cv2'"

**Solution:**
```bash
# Install OpenCV explicitly
pip install opencv-python opencv-contrib-python
```

### Error: Virtual environment won't activate

**Solution:**
```bash
# Delete and recreate virtual environment
rm -rf venv  # or: rmdir /s venv (Windows)
python3 -m venv venv

# Then activate it again
source venv/bin/activate  # or: venv\Scripts\activate (Windows)

# Reinstall dependencies
pip install -r requirements.txt
```

---

## System-Specific Instructions

### macOS Specific

#### Using Homebrew (Recommended):
```bash
# Install Python
brew install python@3.10

# Install Xcode Command Line Tools (if needed)
xcode-select --install
```

#### Intel Mac vs Apple Silicon (M1/M2):
- **Apple Silicon (M1/M2)**: Some packages may need native builds
- **Solution**: Use conda instead of pip
  ```bash
  # Install Anaconda
  # Then create environment with conda
  conda create -p myenv python=3.10
  conda activate myenv
  pip install -r requirements.txt
  ```

### Windows Specific

#### Using Anaconda (Alternative):
```bash
# Install Anaconda from anaconda.com
# Then create environment
conda create -n imagetools python=3.10
conda activate imagetools
pip install -r requirements.txt
streamlit run app.py
```

#### PowerShell Execution Policy:
If you get "cannot be loaded because running scripts is disabled":
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux Specific

#### Ubuntu/Debian:
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

#### Fedora/RHEL:
```bash
# Install Python and dependencies
sudo dnf install python3 python3-pip

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## Security Considerations

### Virtual Environment Benefits
- Isolates project dependencies
- Prevents conflicts with system packages
- Easier to delete and recreate
- **Always use virtual environments for Python projects**

### Safe Installation Practices
```bash
# 1. Use specific versions (already in requirements.txt)
# 2. Always use virtual environment
# 3. Keep dependencies updated
pip list --outdated

# 4. Verify package integrity
pip install --require-hashes requirements.txt
```

---

## Verification

After installation, verify everything is working:

```bash
# 1. Check Python
python --version

# 2. Check pip packages
pip list

# Expected packages:
# - streamlit
# - opencv-python
# - opencv-contrib-python
# - numpy
# - Pillow

# 3. Test imports
python -c "import cv2; import streamlit; print('All imports successful')"

# 4. Check sample image
ls sample_images/sample.jpg  # or: dir sample_images (Windows)

# 5. Run application
streamlit run app.py
```

---

## Running on Server/Cloud

### Streamlit Cloud (Recommended)
```bash
# Push to GitHub, then deploy via streamlit.io
# Free hosting for public projects
```

### Local Network Access
```bash
# Run with network access
streamlit run app.py --server.address=0.0.0.0
```

### Docker Deployment (Advanced)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

---

## Support

If you encounter issues:

1. **Check this guide** - Most common issues covered
2. **Review requirements** - Ensure all packages installed
3. **Update packages** - `pip install --upgrade -r requirements.txt`
4. **Recreate environment** - Delete venv and start fresh
5. **Check documentation** - See README.md for detailed info

---

## Next Steps

After successful installation:

1. **Generate Sample Image**: `python create_sample.py`
2. **Run Application**: `streamlit run app.py`
3. **Upload an Image**: Use the sidebar file uploader
4. **Explore Features**: Test different filters and enhancements
5. **Download Results**: Export enhanced images

---

**Happy Image Processing!**

For more information, see [README.md](README.md)
