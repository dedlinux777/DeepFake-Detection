# ✅ QUICK TRAINING CHECKLIST

## Before You Start Training

### Prerequisites Check
```bash
# 1. Check Python version (3.7+)
python --version

# 2. Check TensorFlow installed
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__}')"

# 3. Check Keras installed
python -c "import keras; print(f'Keras {keras.__version__}')"

# 4. Check if GPU available (optional)
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### If Any Missing
```bash
# Install/Update all
pip install --upgrade tensorflow keras numpy pandas matplotlib
```

---

## The Training Process (3 Steps)

### STEP 1: Open Jupyter Notebook
```bash
cd "D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main"
jupyter notebook
```

### STEP 2: Click on Notebook & Run
- Browser opens with file list
- Click on `forgery.ipynb`
- Go to: **Kernel** → **Restart & Run All**
- Watch the training progress
- Wait 30 min - 4 hours

### STEP 3: Verify Model Created
```bash
python check_model_path.py
```

Expected output:
```
[✓ FOUND] In Notebook folder
         D:\dedlinux UVCE\6th Sem\Mini Project\...\model_casia_run1.h5
```

---

## During Training: What to Expect

### Training Output Example
```
Epoch 1/50
1000/1000 [==============================] - 45s 45ms/step - loss: 0.4521 - accuracy: 0.8234
Epoch 2/50
1000/1000 [==============================] - 42s 42ms/step - loss: 0.3421 - accuracy: 0.8712
...
Epoch 50/50
1000/1000 [==============================] - 40s 40ms/step - loss: 0.0234 - accuracy: 0.9876

Model saved to: model_casia_run1.h5 ✓
```

### Progress Signs
- ✅ Progress bar is moving: Training is working
- ✅ Loss decreasing: Model is improving
- ✅ Accuracy increasing: Model is learning
- ✅ Epoch 50/50 complete: Training finished!

### Warning Signs (Don't Panic)
- ⚠️ GPU not found: Will use CPU (slower, but works)
- ⚠️ Memory warning: Close other programs
- ⚠️ Slow progress: Normal for CPU (4 hours possible)
- ⚠️ Fluctuating loss: Normal during training

---

## If Training Fails

### Error: "Out of Memory"
```bash
# Reduce batch size in notebook
# From: batch_size=32
# To: batch_size=16
# Then restart and run again
```

### Error: "Dataset not found"
```bash
# Check dataset path in notebook
# Should be pointing to extracted CASIA folder
# For image.ipynb: Need Kaggle API key
```

### Error: "Keras/TensorFlow version mismatch"
```bash
pip install --upgrade tensorflow keras --force-reinstall
```

### Error: "GPU memory issue"
```bash
# Use CPU instead (slower but more reliable)
# Or use Google Colab with GPU (free and fast!)
```

---

## After Training: What to Do

### 1. Verify Model Exists
```bash
python check_model_path.py
```

### 2. Copy the Absolute Path
```
C:\Users\Harshavardhan N\...\model_casia_run1.h5
```

### 3. Update app.py
Edit `app.py` line ~17:
```python
MODEL_PATH = r'C:\Users\Harshavardhan N\...\model_casia_run1.h5'
```

### 4. Test Your App
```bash
python app.py
```

### 5. Success!
You should see: `✓ Model loaded successfully!`

---

## Timing Reference

| Task | CPU | GPU |
|------|-----|-----|
| Download Dataset | 10 min | 10 min |
| Preprocess | 5 min | 2 min |
| Train Model | 2-4 hours | 30-60 min |
| **Total** | **2.5-4.5 hours** | **45 min - 1.5 hours** |

---

## Best Option: Use Google Colab (FREE GPU!)

If your computer is slow or you want faster training:

1. Go to: https://colab.research.google.com
2. Click: **File** → **Upload notebook**
3. Upload: `forgery.ipynb`
4. Click: **Runtime** → **Change runtime type** → **GPU**
5. Press: **Ctrl+F9** (Run all cells)
6. Wait: 45 minutes
7. Download: `model_casia_run1.h5` from Colab
8. Place in your project folder
9. Run: `python check_model_path.py`
10. Done! ✅

---

## Checklist

Before training:
- [ ] Internet connection stable
- [ ] Computer won't sleep (disable sleep mode)
- [ ] 8GB+ RAM available
- [ ] Python, TensorFlow, Keras installed
- [ ] Notebook file ready
- [ ] 1-4 hours of patience 😄

After training:
- [ ] `model_casia_run1.h5` created
- [ ] Verified with `check_model_path.py`
- [ ] Path copied
- [ ] `app.py` updated
- [ ] `python app.py` runs successfully
- [ ] Ready for demo! 🎉

---

## Questions?

- **"How long will it take?"** → 30 min - 4 hours depending on hardware
- **"My computer is slow"** → Use Google Colab (free GPU)
- **"What if it fails?"** → Read TRAINING_GUIDE.md troubleshooting section
- **"Can I stop and restart?"** → Yes, notebooks save progress in checkpoints

---

## You're Ready! 

```bash
cd "D:\dedlinux UVCE\6th Sem\Mini Project\Deepfakes-Detection-using-ELA-and-CNN-main"
jupyter notebook
```

Then:
1. Click `forgery.ipynb`
2. Kernel → Restart & Run All
3. Wait...
4. Done! 🚀

**Let's train your model!**

