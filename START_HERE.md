# ▶️ START HERE - DO THIS NOW

## Your Current Issue
```
FileNotFoundError: model_casia_run1.h5 not found
```

## The Fix (3 Minutes)

### Copy & Paste This into PowerShell

```powershell
cd "D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main"
python check_model_path.py
```

### Wait for the Output

The script will show you ONE of these:

#### **Case A: ✓ FOUND**
```
[✓ FOUND] In Downloads folder
         C:\Users\Harshavardhan N\Downloads\model_casia_run1.h5
```
→ **COPY THIS PATH**

#### **Case B: ✗ NOT FOUND**
```
✗ Model file NOT FOUND
```
→ **You need to train or find the model first** (see NEXT STEPS)

---

## What to Do Next (Based on Your Output)

### If Model Was FOUND (Case A)

1. **Copy the path** from the output above
2. **Open `app.py`** in your editor
3. **Find line ~17** that looks like:
   ```python
   MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)
   ```
4. **Replace it with:**
   ```python
   MODEL_PATH = r'C:\Users\Harshavardhan N\Downloads\model_casia_run1.h5'
   ```
   (Use the path from your output, not this example)
5. **Save the file** (Ctrl+S)
6. **Test it:**
   ```powershell
   python app.py
   ```
7. **You should see:**
   ```
   ✓ Model loaded successfully!
   ```

### If Model Was NOT FOUND (Case B)

**The model file doesn't exist on your system.**

**Options:**
1. **Train it** from your Jupyter notebooks:
   - Open `forgery.ipynb` or `image.ipynb`
   - Run the cells that train the model
   - The model will be saved as `model_casia_run1.h5`
   - Run `check_model_path.py` again

2. **Find it** if you trained it before:
   - Check your Downloads folder
   - Check your Documents folder
   - Check project subdirectories
   - The `check_model_path.py` script already searched common places

3. **Download it** if your team has it:
   - Ask for the model file from your group members
   - Place it in Downloads or your project folder
   - Run `check_model_path.py` again

---

## Quick Reference: Windows Paths

When you update `app.py`, use this format:

```python
# ✅ CORRECT (raw string)
MODEL_PATH = r'C:\Users\YourUsername\Downloads\model_casia_run1.h5'

# ❌ WRONG (will cause errors)
MODEL_PATH = 'C:\Users\YourUsername\Downloads\model_casia_run1.h5'
```

**Golden Rule:** Use `r'...'` for Windows paths!

---

## Verification Checklist

- [ ] Ran `python check_model_path.py`
- [ ] Model file found (or planning to train)
- [ ] Copied path from output
- [ ] Updated `app.py` line ~17
- [ ] Saved `app.py`
- [ ] Ran `python app.py`
- [ ] Saw "✓ Model loaded successfully!"
- [ ] Ready for demo! 🎉

---

## If Still Stuck

1. **Re-run:** `python check_model_path.py`
2. **Check output:** Does it say FOUND or NOT FOUND?
3. **If FOUND:** Did you use exact path from output?
4. **If NOT FOUND:** Did you train the model from notebooks?
5. **Still confused?** Read `ACTION_PLAN.md` for detailed steps

---

## Most Important Lines to Remember

**In PowerShell:**
```bash
python check_model_path.py
```

**In app.py (around line 17):**
```python
MODEL_PATH = r'EXACT_PATH_FROM_OUTPUT_ABOVE'
```

**To test:**
```bash
python app.py
```

---

**That's it! You've got this! 🚀**

