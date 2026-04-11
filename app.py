from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import os
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from tensorflow import keras

app = Flask(__name__)
# run_with_ngrok(app)

# =========================
# CREATE REQUIRED FOLDERS
# =========================
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/ela_images', exist_ok=True)

# =========================
# MODEL PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = 'model_ai_artbench_run.h5'   # ✅ YOUR MODEL
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

print("=" * 60)
print("MODEL PATH:", MODEL_PATH)
print("EXISTS:", os.path.exists(MODEL_PATH))
print("=" * 60)

# =========================
# LOAD MODEL
# =========================
model = keras.models.load_model(MODEL_PATH)
print("✅ Model loaded successfully!")

# =========================
# ROUTE
# =========================
@app.route('/', methods=['GET', 'POST'])
def index():
    ela_image_path = None
    result = None
    confidence = None
    error = None

    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file uploaded'
        else:
            file = request.files['file']

            if file.filename == '':
                error = 'No file selected'
            else:
                filepath = os.path.join('uploads', file.filename)
                file.save(filepath)

                ela_image_path = convert_and_save_ela_image(filepath)
                confidence, result = predict_fake_real(ela_image_path)

    return render_template(
        'index.html',
        ela_image_path=ela_image_path,
        confidence=confidence,
        result=result,
        error=error
    )

# =========================
# ELA FUNCTION
# =========================
def convert_to_ela_image(image_path, quality=90):
    temp_filename = 'temp.jpg'

    image = Image.open(image_path).convert('RGB')
    image.save(temp_filename, 'JPEG', quality=quality)
    temp_image = Image.open(temp_filename)

    ela_image = ImageChops.difference(image, temp_image)

    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])

    scale = 255.0 / max_diff if max_diff != 0 else 1
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    return ela_image

# =========================
# PREPROCESS IMAGE (FIXED)
# =========================
def prepare_image(image_path):
    image_size = (128, 128)

    ela_image = Image.open(image_path).convert('RGB').resize(image_size)

    ela_array = np.array(ela_image, dtype=np.float32) / 255.0

    return ela_array

# =========================
# SAVE ELA IMAGE
# =========================
def convert_and_save_ela_image(image_path):
    ela_image = convert_to_ela_image(image_path)
    ela_path = 'static/ela_images/ela_image.png'
    ela_image.save(ela_path)
    return ela_path

# =========================
# PREDICTION
# =========================
def predict_fake_real(ela_image_path):
    image_array = prepare_image(ela_image_path)

    image_array = image_array.reshape(1, 128, 128, 3)

    prediction = model.predict(image_array)

    confidence = round(float(np.max(prediction)) * 100, 2)

    result = 'Fake' if np.argmax(prediction) == 0 else 'Real'

    return confidence, result

# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run()