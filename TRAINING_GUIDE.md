# 🎓 HOW TO TRAIN YOUR MODEL - COMPLETE GUIDE

## Your Situation
❌ Model file `model_casia_run1.h5` NOT FOUND
✅ You have training notebooks: `forgery.ipynb` and `image.ipynb`
✅ Both contain code to train the model

---

## Option 1: Train from `forgery.ipynb` (RECOMMENDED) ⭐

### Step 1: Open the Notebook
1. Navigate to your project folder
2. Open `forgery.ipynb` in Jupyter Notebook or JupyterLab
3. Or open it directly: [VS Code can open notebooks] or use Google Colab

### Step 2: Run the Training Code

The notebook has this code that saves the model:
```python
model.save('model_casia_run1.h5')
```

This is typically near the end of the notebook.

### Step 3: Run All Cells
- **In Jupyter:** Click "Kernel" → "Restart & Run All"
- **Or manually:** Run cells from top to bottom (Shift+Enter)
- **Important:** This may take 30 minutes to several hours depending on dataset size

### Step 4: Model is Saved
Once complete, `model_casia_run1.h5` will be created in the same folder where you ran the notebook

### Step 5: Verify with Our Script
```bash
python check_model_path.py
```

You should now see:
```
[✓ FOUND] In Notebook folder
         D:\dedlinux UVCE\6th Sem\Mini Project\...\model_casia_run1.h5
```

---

## Option 2: Train from `image.ipynb`

Similar process to Option 1:

### Step 1: Open Notebook
Open `image.ipynb` in Jupyter

### Step 2: Look for Model Saving Code
Search for:
- `model.save()`
- `.h5` file saving
- Training cells

### Step 3: Run All Cells
- This notebook downloads CASIA dataset from Kaggle
- You need Kaggle credentials (see below)
- Same process: "Restart & Run All"

### Step 4: Model Saved
`model_casia_run1.h5` will be created

### Step 5: Verify
```bash
python check_model_path.py
```

---

## ⚠️ Prerequisites for Training

### 1. TensorFlow & Keras Installed
```bash
pip install tensorflow keras
```

### 2. GPU Support (Optional but Recommended)
Training is MUCH faster with GPU:
```bash
pip install tensorflow[and-cuda]
```

### 3. For `image.ipynb`: Kaggle Credentials
The notebook downloads the CASIA dataset. You need:
1. Kaggle API key from https://www.kaggle.com/settings/account
2. Place `kaggle.json` in your project folder
3. The notebook handles uploading it

---

## Expected Training Time

| Notebook | Dataset Size | Training Time | GPU | CPU |
|----------|------|------|-----|-----|
| `image.ipynb` | ~5GB | Download | 5 min | 15 min |
| `forgery.ipynb` | Varies | Training | 30-60 min | 2-4 hours |

---

## Step-by-Step: Using VS Code/Jupyter

### Method 1: Using Jupyter Notebook (Easiest)

```bash
# 1. Navigate to project
cd "D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main"

# 2. Start Jupyter
jupyter notebook

# 3. Browser opens with list of files
# 4. Click on forgery.ipynb
# 5. In notebook, go to Kernel menu → "Restart & Run All"
# 6. Wait for training to complete
# 7. Model is saved!
```

### Method 2: Using JupyterLab (Better UI)

```bash
# Install JupyterLab if needed
pip install jupyterlab

# Start JupyterLab
jupyter lab

# Then follow steps 3-7 above
```

### Method 3: Using VS Code (If you have Jupyter extension)

1. Open VS Code
2. Install Python extension
3. Install Jupyter extension
4. Open `forgery.ipynb`
5. Click "Run All" button
6. Wait for completion

### Method 4: Using Google Colab (Free GPU!)

**BEST OPTION** if your computer is slow:

1. Go to https://colab.research.google.com
2. Click "File" → "Open notebook" → "GitHub"
3. Paste the notebook URL or upload `forgery.ipynb`
4. Click "Runtime" → "Change runtime type" → GPU
5. Run all cells
6. Download the resulting `model_casia_run1.h5`

---

## What Happens During Training

### The notebook will:
1. **Load dataset** (CASIA or whatever is configured)
2. **Preprocess images** (resizing, normalization)
3. **Build CNN model** (Convolutional Neural Network)
4. **Train model** (pass data through network multiple times)
5. **Validate** (test accuracy on validation set)
6. **Save model** as `model_casia_run1.h5`

### You'll see output like:
```
Epoch 1/50
1000/1000 [==============================] - 45s 45ms/step - loss: 0.4521 - accuracy: 0.8234
Epoch 2/50
1000/1000 [==============================] - 42s 42ms/step - loss: 0.3421 - accuracy: 0.8712
...
Model saved successfully!
```

---

## Troubleshooting Training

### Problem: "Out of Memory" Error
**Solution:**
```bash
# Free up RAM
# Close other programs
# OR reduce batch size in notebook

# If using CPU instead of GPU:
pip install tensorflow[and-cuda]  # Install GPU support
```

### Problem: "Dataset not found"
**Solution:**
- For `image.ipynb`: Ensure Kaggle API is configured
- For `forgery.ipynb`: Check if dataset path is correct in code

### Problem: "GPU not detected"
**Solution:**
```bash
# Check if CUDA/GPU available
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# If not found, training will use CPU (slower but works)
```

### Problem: Notebook won't run
**Solution:**
```bash
# Restart kernel and clear outputs
# Then run cells one by one to see which fails
# Check error message carefully
```

---

## After Training: Next Steps

### Step 1: Find the Model
```bash
python check_model_path.py
```

### Step 2: It Should Show
```
[✓ FOUND] In Notebook folder
         D:\dedlinux UVCE\6th Sem\Mini Project\...\model_casia_run1.h5
```

### Step 3: Update app.py (if needed)
Copy the path from above and paste into `app.py` line 17

### Step 4: Test Flask App
```bash
python app.py
```

### Step 5: Success!
You should see: `✓ Model loaded successfully!`

---

## Quick Checklist

- [ ] Have Jupyter Notebook/Lab installed
- [ ] Have TensorFlow/Keras installed
- [ ] Have `forgery.ipynb` or `image.ipynb` ready
- [ ] Have dataset available (or Kaggle API)
- [ ] Computer has 8GB+ RAM (16GB+ recommended)
- [ ] Have 1-4 hours for training
- [ ] Ready to run the training

---

## Alternative: Use Pre-trained Model

If training takes too long:

1. **Ask your team** if they have a pre-trained model
2. **Download** from GitHub releases if available
3. **Use transfer learning** (train shorter)
4. **Use Google Colab** for free GPU (much faster)

---

## Estimated Time to Complete

1. **Install/Update libraries:** 5 minutes
2. **Run training:** 30 minutes - 4 hours (depending on GPU/CPU)
3. **Save model:** Automatic (included in training)
4. **Update app.py:** 2 minutes
5. **Total:** 40 minutes - 4 hours

---

## I'm Ready to Train!

When you're ready to start:

1. **Run this to start Jupyter:**
   ```bash
   cd "D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main"
   jupyter notebook
   ```

2. **Click on `forgery.ipynb`**

3. **Go to Kernel → Restart & Run All**

4. **Wait for training (30 min - 4 hours)**

5. **Then run:**
   ```bash
   python check_model_path.py
   ```

6. **Copy the path and update app.py**

7. **Done!** 🎉

---

**Need help?** Let me know when you start training and I can guide you through any issues!

