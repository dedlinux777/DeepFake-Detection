"""
Colab-ready training script for AI_ARTBENCH ELA + CNN.
Output model: model_ai_artbench_run.h5
"""

import os
import random
import numpy as np
import tensorflow as tf
from PIL import Image, ImageChops, ImageEnhance
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


# -------------------------
# 1) Reproducibility + setup
# -------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

print("TensorFlow:", tf.__version__)
print("GPU devices:", tf.config.list_physical_devices("GPU"))


# -------------------------
# 2) Config (edit here)
# -------------------------
AU_DIR = "/content/dataset/real"
TP_DIR = "/content/dataset/fake"
IMG_SIZE = (128, 128)
ELA_QUALITY = 90
MAX_REAL = 900
MAX_FAKE = 900
EPOCHS = 5
BATCH_SIZE = 16
LEARNING_RATE = 1e-4
MODEL_PATH = "model_ai_artbench_run.h5"

VALID_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")


# -------------------------
# 3) ELA helpers
# -------------------------
def convert_to_ela_image(path: str, quality: int = 90) -> Image.Image:
    original = Image.open(path).convert("RGB")
    temp_path = "/tmp/ela_temp.jpg"
    original.save(temp_path, "JPEG", quality=quality)
    compressed = Image.open(temp_path)

    ela = ImageChops.difference(original, compressed)
    extrema = ela.getextrema()
    max_diff = max(channel_max for _, channel_max in extrema)
    max_diff = max(max_diff, 1)
    scale = 255.0 / max_diff
    ela = ImageEnhance.Brightness(ela).enhance(scale)
    return ela


def prepare_image(path: str) -> np.ndarray:
    ela = convert_to_ela_image(path, quality=ELA_QUALITY)
    arr = np.array(ela.resize(IMG_SIZE), dtype=np.float32) / 255.0
    return arr


def list_images(folder: str) -> list[str]:
    files = []
    for root, _, names in os.walk(folder):
        for name in names:
            if name.lower().endswith(VALID_EXT):
                files.append(os.path.join(root, name))
    return files


# -------------------------
# 4) Build dataset
# -------------------------
def load_dataset():
    real_files = list_images(AU_DIR)[:MAX_REAL]
    fake_files = list_images(TP_DIR)[:MAX_FAKE]

    print("Real files:", len(real_files))
    print("Fake files:", len(fake_files))

    all_files = real_files + fake_files
    all_labels = [1] * len(real_files) + [0] * len(fake_files)  # 1=real, 0=fake

    pairs = list(zip(all_files, all_labels))
    random.shuffle(pairs)  # keep file-label mapping correct

    X, y = [], []
    for i, (path, label) in enumerate(pairs, start=1):
        try:
            X.append(prepare_image(path))
            y.append(label)
        except Exception as exc:
            print(f"Skipped {path} -> {exc}")

        if i % 500 == 0:
            print(f"Processed {i}/{len(pairs)}")

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    print("X shape:", X.shape)
    print("y shape:", y.shape)
    return X, y


# -------------------------
# 5) Build model
# -------------------------
def build_model(input_shape=(128, 128, 3)):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=input_shape),
        tf.keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(2, activation="softmax"),
    ])
    return model


# -------------------------
# 6) Training entry point
# -------------------------
def main():
    X, y = load_dataset()

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=SEED,
        stratify=y,
    )

    train_ds = (
        tf.data.Dataset.from_tensor_slices((X_train, y_train))
        .shuffle(2000, seed=SEED)
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )
    val_ds = (
        tf.data.Dataset.from_tensor_slices((X_val, y_val))
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    model = build_model(input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    model.summary()

    optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=3,
            restore_best_weights=True,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
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
    print(f"Saved model -> {MODEL_PATH}")
    print("Exists?", os.path.exists(MODEL_PATH))

    y_prob = model.predict(val_ds, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)
    cm = confusion_matrix(y_val, y_pred)
    print("Confusion matrix:\n", cm)

    print("Last epoch metrics:")
    print("train_acc:", float(history.history["accuracy"][-1]))
    print("val_acc:", float(history.history["val_accuracy"][-1]))


if __name__ == "__main__":
    main()
