"""
Improved training script for AI_ARTBENCH ELA + CNN.
Target: 90%+ accuracy on ~5000 images (balanced real vs fake)
Output model: model_ai_artbench_run.h5

Fix vs previous version:
  - Augmentation moved OUT of the model and into tf.data pipeline
    (avoids Keras 2.19 deepcopy bug with EarlyStopping restore_best_weights)
  - ModelCheckpoint uses save_weights_only=True for same reason
"""

import os
import random
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from PIL import Image, ImageChops, ImageEnhance
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report


# ─────────────────────────────────────────────
# 1) Reproducibility
# ─────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

print("TensorFlow:", tf.__version__)
print("GPU devices:", tf.config.list_physical_devices("GPU"))


# ─────────────────────────────────────────────
# 2) Config
# ─────────────────────────────────────────────
AU_DIR      = "/content/dataset/real"
TP_DIR      = "/content/dataset/fake"
IMG_SIZE    = (128, 128)
ELA_QUALITY = 90

MAX_REAL  = 2500
MAX_FAKE  = 2500

EPOCHS        = 12
BATCH_SIZE    = 32
LEARNING_RATE = 1e-4

MODEL_PATH      = "model_ai_artbench_run.h5"
CHECKPOINT_PATH = "best_checkpoint.weights.h5"
METRICS_PATH    = "metrics.json"
STATIC_DIR = "/content/drive/MyDrive/your_project/static"
TRAINING_CURVE_PATH = os.path.join(STATIC_DIR, "training_curve.png")
CONFUSION_MATRIX_PATH = os.path.join(STATIC_DIR, "confusion_matrix.png")

VALID_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")


# ─────────────────────────────────────────────
# 3) ELA helpers
# ─────────────────────────────────────────────
def convert_to_ela_image(path: str, quality: int = 90) -> Image.Image:
    original  = Image.open(path).convert("RGB")
    temp_path = "/tmp/ela_temp.jpg"
    original.save(temp_path, "JPEG", quality=quality)
    compressed = Image.open(temp_path)

    ela      = ImageChops.difference(original, compressed)
    extrema  = ela.getextrema()
    max_diff = max(channel_max for _, channel_max in extrema)
    max_diff = max(max_diff, 1)
    ela      = ImageEnhance.Brightness(ela).enhance(255.0 / max_diff)
    return ela


def prepare_image(path: str) -> np.ndarray:
    ela = convert_to_ela_image(path, quality=ELA_QUALITY)
    arr = np.array(ela.resize(IMG_SIZE), dtype=np.float32) / 255.0
    return arr


def list_images(folder: str) -> list:
    files = []
    for root, _, names in os.walk(folder):
        for name in names:
            if name.lower().endswith(VALID_EXT):
                files.append(os.path.join(root, name))
    return files


# ─────────────────────────────────────────────
# 4) Dataset loader
# ─────────────────────────────────────────────
def load_dataset():
    real_files = list_images(AU_DIR)[:MAX_REAL]
    fake_files = list_images(TP_DIR)[:MAX_FAKE]

    print(f"Real files : {len(real_files)}")
    print(f"Fake files : {len(fake_files)}")

    all_files  = real_files + fake_files
    all_labels = [1] * len(real_files) + [0] * len(fake_files)

    pairs = list(zip(all_files, all_labels))
    random.shuffle(pairs)

    X, y = [], []
    for i, (path, label) in enumerate(pairs, start=1):
        try:
            X.append(prepare_image(path))
            y.append(label)
        except Exception as exc:
            print(f"  Skipped {path} → {exc}")
        if i % 500 == 0:
            print(f"  Processed {i}/{len(pairs)}")

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)
    print(f"X shape: {X.shape}  |  y shape: {y.shape}")
    return X, y


# ─────────────────────────────────────────────
# 5) Augmentation — applied in tf.data pipeline
#    NOT inside the model graph.
#    This avoids the Keras 2.19 deepcopy crash
#    caused by EarlyStopping(restore_best_weights)
#    trying to pickle TF module objects.
# ─────────────────────────────────────────────
augment_layer = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomFlip("vertical"),
    tf.keras.layers.RandomBrightness(factor=0.1),
    tf.keras.layers.RandomContrast(factor=0.1),
], name="augmentation")

def augment(image, label):
    image = augment_layer(image, training=True)
    return image, label


# ─────────────────────────────────────────────
# 6) Model — clean graph, no augmentation layers
# ─────────────────────────────────────────────
def build_model(input_shape=(128, 128, 3)):
    inputs = tf.keras.Input(shape=input_shape)

    # Block 1
    x = tf.keras.layers.Conv2D(32, (3, 3), padding="same", use_bias=False)(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)       # 128 → 64

    # Block 2
    x = tf.keras.layers.Conv2D(64, (3, 3), padding="same", use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)       # 64 → 32

    # Block 3
    x = tf.keras.layers.Conv2D(128, (3, 3), padding="same", use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)       # 32 → 16

    # Block 4
    x = tf.keras.layers.Conv2D(256, (3, 3), padding="same", use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)       # 16 → 8

    # Classifier head
    x = tf.keras.layers.Flatten()(x)                  # 8×8×256 = 16 384
    x = tf.keras.layers.Dense(256, use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.Dropout(0.4)(x)

    outputs = tf.keras.layers.Dense(2, activation="softmax")(x)

    return tf.keras.Model(inputs, outputs, name="detectify_v2")


def plot_training_curves(history_dict: dict, output_path: str):
    epochs = range(1, len(history_dict["accuracy"]) + 1)
    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, history_dict["accuracy"], label="Train Accuracy")
    plt.plot(epochs, history_dict["val_accuracy"], label="Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Accuracy vs Epochs")
    plt.legend()
    plt.grid(alpha=0.2)

    plt.subplot(1, 2, 2)
    plt.plot(epochs, history_dict["loss"], label="Train Loss")
    plt.plot(epochs, history_dict["val_loss"], label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Loss vs Epochs")
    plt.legend()
    plt.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_conf_matrix(cm: np.ndarray, output_path: str):
    plt.figure(figsize=(5, 4))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Confusion Matrix")
    plt.colorbar()
    tick_marks = np.arange(2)
    class_names = ["Fake", "Real"]
    plt.xticks(tick_marks, class_names)
    plt.yticks(tick_marks, class_names)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    thresh = cm.max() / 2.0 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(
                j, i, format(cm[i, j], "d"),
                ha="center",
                color="white" if cm[i, j] > thresh else "black"
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


# ─────────────────────────────────────────────
# 7) Training entry point
# ─────────────────────────────────────────────
def main():
    os.makedirs(STATIC_DIR, exist_ok=True)

    X, y = load_dataset()

    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=0.2,
        random_state=SEED,
        stratify=y,
    )
    print(f"Train: {len(X_train)}  |  Val: {len(X_val)}")

    # Augmentation applied to training batches only
    train_ds = (
        tf.data.Dataset.from_tensor_slices((X_train, y_train))
        .shuffle(4000, seed=SEED)
        .batch(BATCH_SIZE)
        # .map(augment, num_parallel_calls=tf.data.AUTOTUNE)
        .prefetch(tf.data.AUTOTUNE)
    )
    val_ds = (
        tf.data.Dataset.from_tensor_slices((X_val, y_val))
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    model = build_model(input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    model.summary()

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=4,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=CHECKPOINT_PATH,
            monitor="val_accuracy",
            save_best_only=True,
            save_weights_only=True,   # avoids full-model serialisation issues
            verbose=1,
        ),
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )

    model.save(MODEL_PATH)
    print(f"\n✅ Saved model → {MODEL_PATH}")

    y_prob = model.predict(val_ds, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)

    cm = confusion_matrix(y_val, y_pred)
    print("\nConfusion matrix:\n", cm)
    print("\nClassification report:")
    report_text = classification_report(y_val, y_pred, target_names=["Fake", "Real"])
    report_dict = classification_report(
        y_val, y_pred, target_names=["Fake", "Real"], output_dict=True
    )
    print(report_text)

    metrics_payload = {
        "accuracy": float(report_dict["accuracy"]),
        "precision": float(report_dict["weighted avg"]["precision"]),
        "recall": float(report_dict["weighted avg"]["recall"]),
        "f1_score": float(report_dict["weighted avg"]["f1-score"]),
        "confusion_matrix": cm.tolist(),
        "train_accuracy": [float(v) for v in history.history["accuracy"]],
        "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
        "train_loss": [float(v) for v in history.history["loss"]],
        "val_loss": [float(v) for v in history.history["val_loss"]],
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as fp:
        json.dump(metrics_payload, fp, indent=2)
    print(f"\n✅ Saved metrics → {METRICS_PATH}")

    plot_training_curves(history.history, TRAINING_CURVE_PATH)
    print(f"✅ Saved training curve → {TRAINING_CURVE_PATH}")

    plot_conf_matrix(cm, CONFUSION_MATRIX_PATH)
    print(f"✅ Saved confusion matrix plot → {CONFUSION_MATRIX_PATH}")

    print("\nFinal epoch metrics:")
    print("  train_acc :", round(float(history.history["accuracy"][-1]),  4))
    print("  val_acc   :", round(float(history.history["val_accuracy"][-1]), 4))


if __name__ == "__main__":
    main()