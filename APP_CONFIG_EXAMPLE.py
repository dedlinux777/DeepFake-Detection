"""
EXAMPLE: app.py with ABSOLUTE PATH configuration
This shows how to modify your app.py if your model is elsewhere on disk
"""

from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import os
import numpy as np
from PIL import Image
from tensorflow import keras
from PIL import Image, ImageChops, ImageEnhance

app = Flask(__name__)
run_with_ngrok(app)

# ===== MODEL PATH CONFIGURATION =====
# Choose ONE of these methods:

# METHOD 1: RELATIVE PATH (Model in project root - RECOMMENDED)
# =========================================================
# Place your model_casia_run1.h5 in the same folder as app.py
# Then use this:
"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = 'model_casia_run1.h5'
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)
"""

# METHOD 2: ABSOLUTE PATH (Model is elsewhere)
# ===============================================
# If model_casia_run1.h5 is in your Downloads or another location, use:
# Example Windows path - COPY YOUR ACTUAL PATH HERE:
"""
MODEL_PATH = r'C:\Users\Harshavardhan N\Downloads\model_casia_run1.h5'
# OR if it's on another drive:
# MODEL_PATH = r'D:\path\to\your\model_casia_run1.h5'
"""

# METHOD 3: ENVIRONMENT VARIABLE (Most flexible)
# ================================================
# Set an environment variable and use it:
"""
MODEL_PATH = os.environ.get(
    'DETECTIFY_MODEL_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_casia_run1.h5')
)
# Then run: set DETECTIFY_MODEL_PATH=C:\path\to\model.h5 && python app.py
"""

# ===== ACTUAL IMPLEMENTATION IN YOUR CODE =====
# Use Method 1 by default, change to Method 2 if needed:

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = 'model_casia_run1.h5'
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

# Uncomment below and comment above to use absolute path instead:
# MODEL_PATH = r'PASTE_YOUR_ABSOLUTE_PATH_HERE'

# Example absolute paths:
# MODEL_PATH = r'C:\Users\Harshavardhan N\Downloads\model_casia_run1.h5'
# MODEL_PATH = r'D:\Models\deepfakes\model_casia_run1.h5'

print("=" * 60)
print("DETECTIFY - Model Path Configuration")
print("=" * 60)
print(f"Current Working Directory: {os.getcwd()}")
print(f"Script Location (BASE_DIR): {BASE_DIR}")
print(f"Configured Model Path: {MODEL_PATH}")
print(f"Model File Exists: {os.path.exists(MODEL_PATH)}")
print("=" * 60)

# Load the model with error handling
try:
    model = keras.models.load_model(MODEL_PATH)
    print("✓ Model loaded successfully!")
except FileNotFoundError as e:
    print(f"✗ ERROR: Model file not found at:")
    print(f"   {MODEL_PATH}")
    print(f"\nFix this by:")
    print(f"1. Running: python check_model_path.py")
    print(f"2. Finding where your model is located")
    print(f"3. Using absolute path in this file:")
    print(f"   MODEL_PATH = r'C:\\\\path\\\\to\\\\model_casia_run1.h5'")
    raise
except Exception as e:
    print(f"✗ ERROR loading model: {type(e).__name__}: {e}")
    raise

# ... rest of your app code follows ...

