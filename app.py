from flask import Flask, render_template, request, url_for
from flask_ngrok import run_with_ngrok
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageChops, ImageEnhance
from tensorflow import keras
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
# run_with_ngrok(app)

# =========================
# CREATE REQUIRED FOLDERS
# =========================
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/ela_images', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static', exist_ok=True)

# =========================
# MODEL PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = 'model_ai_artbench_run.h5'   # ✅ YOUR MODEL
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)
METRICS_PATH = os.path.join(BASE_DIR, "metrics.json")
COMPARISON_PATH = os.path.join(BASE_DIR, "static", "comparison.png")

print("=" * 60)
print("MODEL PATH:", MODEL_PATH)
print("EXISTS:", os.path.exists(MODEL_PATH))
print("=" * 60)

# =========================
# LOAD MODEL
# =========================
model = keras.models.load_model(MODEL_PATH)
print("✅ Model loaded successfully!")


def load_metrics():
    if not os.path.exists(METRICS_PATH):
        return None

    with open(METRICS_PATH, "r", encoding="utf-8") as fp:
        return json.load(fp)


def ensure_comparison_chart(my_model_accuracy: float):
    labels = ["Baseline CNN", "My Model", "IEEE Paper"]
    values = [0.92, my_model_accuracy, 0.99]
    colors = ["#f39c12", "#3498db", "#2ecc71"]

    plt.figure(figsize=(8, 4.5))
    bars = plt.bar(labels, values, color=colors)
    plt.ylim(0.0, 1.05)
    plt.ylabel("Accuracy")
    plt.title("Accuracy Comparison")

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            f"{value:.2f}",
            ha="center"
        )

    plt.tight_layout()
    plt.savefig(COMPARISON_PATH, dpi=150)
    plt.close()

# =========================
# ROUTE
# =========================
@app.route('/', methods=['GET', 'POST'])
def index():
    ela_image_path = None
    uploaded_image_path = None
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
                original_name = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{original_name}"
                filepath = os.path.join('static', 'uploads', unique_name)
                file.save(filepath)
                uploaded_image_path = url_for('static', filename=f'uploads/{unique_name}')

                ela_image_path = convert_and_save_ela_image(filepath)
                confidence, result = predict_fake_real(ela_image_path)

    return render_template(
        'index.html',
        ela_image_path=ela_image_path,
        uploaded_image_path=uploaded_image_path,
        confidence=confidence,
        result=result,
        error=error,
    )


@app.route('/dashboard')
def dashboard():
    metrics = load_metrics()
    if metrics and "accuracy" in metrics:
        ensure_comparison_chart(float(metrics["accuracy"]))

    return render_template(
        'dashboard.html',
        metrics=metrics,
        confusion_matrix_image='confusion_matrix.png',
        training_curve_image='training_curve.png',
        comparison_image='comparison.png'
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

    result = 'AI Generated Art' if np.argmax(prediction) == 0 else 'Real Human Art'

    return confidence, result

# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run()
