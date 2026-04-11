"""
Quick Command: Copy-paste this into your terminal to verify Python paths
These are one-liner commands you can run directly in PowerShell
"""

# ===== COMMAND 1: Check Current Working Directory =====
# Run this in PowerShell:
# python -c "import os; print('CWD:', os.getcwd())"

# ===== COMMAND 2: List Files in Current Directory =====
# python -c "import os; print('Files:', os.listdir('.'))"

# ===== COMMAND 3: Check if Model Exists =====
# python -c "import os; print('Model exists:', os.path.exists('model_casia_run1.h5'))"

# ===== COMMAND 4: Get Absolute Path of Current Directory =====
# python -c "import os; print('Absolute path:', os.path.abspath('.'))"

# ===== COMMAND 5: Check Specific Model Path =====
# python -c "import os; path = r'C:\your\path\here\model_casia_run1.h5'; print(f'Path exists: {os.path.exists(path)}')"

# ===== COMMAND 6: Find model file in Downloads =====
# python -c "import os; path = os.path.join(os.path.expanduser('~'), 'Downloads', 'model_casia_run1.h5'); print(f'Downloads path: {path}'); print(f'Exists: {os.path.exists(path)}')"

# ===== COMMAND 7: Get Project Root and Expected Model Path =====
# Run from project directory:
# python -c "import os; bd = os.path.dirname(os.path.abspath('app.py')); print(f'Project root: {bd}'); print(f'Expected model path: {os.path.join(bd, \"model_casia_run1.h5\")}')"

