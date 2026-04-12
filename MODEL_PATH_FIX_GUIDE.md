# DETECTIFY Model Path Configuration Guide

## Problem Summary
Your Flask app is throwing a `FileNotFoundError` when trying to load `model_casia_run1.h5` because the model file is not in the location where the app is looking for it.

---

## 📊 Verification Results

Your verification check shows:
- **Current Working Directory:** `D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main`
- **Project Root:** Same as above
- **Model File Status:** ❌ **NOT FOUND**

---

## ✅ Solution: 3-Step Fix

### Step 1: Run the Verification Script (ALWAYS DO THIS FIRST)
```bash
cd "D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main"
python check_model_path.py
```
This script will:
- Show your current working directory
- Search for the model file in multiple locations
- Suggest the correct absolute path to use

---

### Step 2: Obtain the Model File

You need to get the `model_casia_run1.h5` file. Choose ONE of these options:

#### Option A: If you have the file somewhere else
1. Run `python check_model_path.py` - it will search your system
2. Note the absolute path where it finds the file
3. Proceed to Step 3

#### Option B: If the model is in your Downloads folder
```bash
python check_model_path.py
# It will show you the path, e.g., C:\Users\YourUsername\Downloads\model_casia_run1.h5
```

#### Option C: If you need to train/download the model
See your project's `forgery.ipynb` or `image.ipynb` notebooks for model training instructions.

---

### Step 3: Configure the Path in app.py

Your `app.py` now has improved path handling. There are 2 ways to load the model:

#### Method 1: Relative Path (Place file in project root)
```
Your Project Structure:
D:\dedlinux UVCE\6th Sem\Mini Project\
    └── Deepfakes-Detection-using-ELA-and-CNN-main/
        ├── app.py
        ├── model_casia_run1.h5  ← Place file HERE
        ├── static/
        └── templates/
```

Then in `app.py`, the code already works as-is:
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model_casia_run1.h5')
```

#### Method 2: Absolute Path (File is elsewhere)
If your model is at `C:\Users\Harshavardhan N\Downloads\model_casia_run1.h5`, edit `app.py`:

**BEFORE:**
```python
MODEL_FILENAME = 'model_casia_run1.h5'
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)
```

**AFTER:**
```python
# Using absolute path directly
MODEL_PATH = r'C:\Users\Harshavardhan N\Downloads\model_casia_run1.h5'
# OR if model is in a different location:
# MODEL_PATH = r'D:\path\to\your\model_casia_run1.h5'
```

> **Note:** Use `r''` (raw string) or double backslashes `\\` in Windows paths to avoid escape sequence errors.

---

## 🔍 How to Find Your Model's Absolute Path

### Option 1: Using the Verification Script (Recommended)
```bash
python check_model_path.py
```
Output will show the full absolute path where the model is located.

### Option 2: Manual Search in Windows
1. Open **File Explorer**
2. Press `Ctrl + F` to search
3. Type: `model_casia_run1.h5`
4. When found, right-click → Properties → copy the full path

### Option 3: Using Python
```python
import os

# Replace with actual path to check
model_path = r'C:\Users\Harshavardhan N\Downloads\model_casia_run1.h5'
print(f"File exists: {os.path.exists(model_path)}")
print(f"Absolute path: {os.path.abspath(model_path)}")
```

---

## 🚀 Running Your Flask App

### Before Running:
```bash
# Navigate to project directory
cd "D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main"

# Check model location
python check_model_path.py

# Activate virtual environment (if using .venv)
.venv\Scripts\Activate.ps1
```

### Start the App:
```bash
python app.py
```

### Expected Output (Success):
```
==============================================================
DETECTIFY - Model Path Debugging
==============================================================
Current Working Directory: D:\dedlinux UVCE\6th Sem\Mini Project\...
Script Location (BASE_DIR): D:\dedlinux UVCE\6th Sem\Mini Project\...
Expected Model Path: D:\dedlinux UVCE\6th Sem\Mini Project\...\model_casia_run1.h5
Model File Exists: True
==============================================================
✓ Model loaded successfully!
```

---

## ❌ Troubleshooting

### Error: Still getting FileNotFoundError
1. Run `python check_model_path.py` to find where the file actually is
2. Copy the absolute path from the output
3. Update `MODEL_PATH` in `app.py` with the correct path

### Error: Bad escape sequence
Make sure to use raw strings (prefix with `r`):
```python
# ❌ WRONG
MODEL_PATH = 'C:\Users\Name\model.h5'

# ✅ CORRECT
MODEL_PATH = r'C:\Users\Name\model.h5'
```

### Error: Model loads but predictions fail
The model file may be corrupted. Ensure you're using the correct trained model from your notebooks.

---

## 📝 Summary Table

| Scenario | Solution |
|----------|----------|
| Model is in project root | Keep current code, place file in project root |
| Model is in Downloads | Use absolute path: `r'C:\Users\...\Downloads\model_casia_run1.h5'` |
| Model location unknown | Run `python check_model_path.py` to find it |
| Still not working | Check path with: `python -c "import os; print(os.path.exists('PATH_HERE'))"` |

---

## 📞 Quick Command Reference

```bash
# Verify model location
python check_model_path.py

# Check if a specific path exists
python -c "import os; print(os.path.exists(r'YOUR_PATH_HERE'))"

# Get absolute path of current directory
python -c "import os; print(os.getcwd())"

# List all .h5 files in project
dir *.h5 /s
```

---

**Status:** ✅ All changes made to `app.py`. Now you just need to locate and configure your model file!

