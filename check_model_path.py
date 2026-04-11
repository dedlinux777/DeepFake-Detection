"""
DETECTIFY - Model Path Verification Script
This script helps diagnose and resolve model loading issues.
Run this before starting your Flask app!
"""

import os
import sys

def main():
    print("\n" + "=" * 70)
    print("DETECTIFY: Model Path Verification")
    print("=" * 70 + "\n")
    
    # 1. Get current working directory
    cwd = os.getcwd()
    print(f"1. Current Working Directory (CWD):")
    print(f"   {cwd}\n")
    
    # 2. Get script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"2. Script Location (where check_model_path.py is):")
    print(f"   {script_dir}\n")
    
    # 3. Check for model in different locations
    print("3. Searching for 'model_casia_run1.h5':\n")
    
    model_filename = 'model_casia_run1.h5'
    search_paths = [
        (os.path.join(cwd, model_filename), "In Current Working Directory (CWD)"),
        (os.path.join(script_dir, model_filename), "In Script Directory (Project Root)"),
        (os.path.join(script_dir, 'models', model_filename), "In 'models' subdirectory"),
        (os.path.join(os.path.expanduser('~'), 'Downloads', model_filename), "In Downloads folder"),
    ]
    
    found_locations = []
    for path, description in search_paths:
        exists = os.path.exists(path)
        status = "✓ FOUND" if exists else "✗ NOT FOUND"
        print(f"   [{status}] {description}")
        print(f"        {path}\n")
        if exists:
            found_locations.append((path, description))
    
    # 4. Recommendations
    print("=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70 + "\n")
    
    if found_locations:
        print(f"✓ Model file found in {len(found_locations)} location(s):\n")
        for path, desc in found_locations:
            print(f"  • {desc}")
            print(f"    Use absolute path: {path}\n")
        
        print("To use the model, add this to app.py:\n")
        print(f'MODEL_PATH = r"{found_locations[0][0]}"\n')
    else:
        print("✗ Model file NOT FOUND\n")
        print("STEPS TO RESOLVE:\n")
        print(f"1. Ensure 'model_casia_run1.h5' is downloaded or available\n")
        print(f"2. Place it in the PROJECT ROOT directory:\n")
        print(f"   {script_dir}\n")
        print(f"3. OR specify an absolute path in app.py:\n")
        print(f'   MODEL_PATH = r"C:\\\\path\\\\to\\\\model_casia_run1.h5"\n')
        print(f"4. Then run: python app.py\n")
    
    # 5. List all .h5 files in project
    print("=" * 70)
    print("Searching for ANY .h5 files in project directory...\n")
    h5_files = []
    for root, dirs, files in os.walk(script_dir):
        # Skip .venv directory
        dirs[:] = [d for d in dirs if d != '.venv']
        for file in files:
            if file.endswith('.h5'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, script_dir)
                h5_files.append(full_path)
                print(f"✓ Found: {rel_path}\n")
    
    if not h5_files:
        print("✗ No .h5 files found in project directory\n")
    
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

