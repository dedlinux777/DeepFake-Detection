
import os
import random
import numpy as np
import tensorflow as tf
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
AU_DIR    = "/content/dataset/real"
TP_DIR    = "/content/dataset/fake"
IMG_SIZE  = (128, 128)
ELA_QUALITY = 90

MAX_REAL  = 2500        # full subset
MAX_FAKE  = 2500

EPOCHS      = 15        # early stopping will kick in well before this
BATCH_SIZE  = 32
LEARNING_RATE = 5e-4    # slightly higher than before; ReduceLROnPlateau will anneal it

MODEL_PATH = "model_ai_artbench_run.h5"

VALID_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")


# ─────────────────────────────────────────────
# 3) ELA helpers  (unchanged from original)
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
    all_labels = [1] * len(real_files) + [0] * len(fake_files)  # 1=real, 0=fake

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
# 5) Augmentation pipeline (lightweight)
#    Only flips + mild brightness — safe for ELA
#    Heavy spatial transforms (rotation > 15°,
#    heavy crop) would distort ELA patterns and
#    hurt rather than help.
# ─────────────────────────────────────────────
def build_augmentation():
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomFlip("vertical"),
        tf.keras.layers.RandomBrightness(factor=0.1),   # ±10 % brightness
        tf.keras.layers.RandomContrast(factor=0.1),     # ±10 % contrast
    ], name="augmentation")


# ─────────────────────────────────────────────
# 6) Improved CNN architecture
#
#   Key changes vs original:
#   • BatchNormalization after every Conv2D
#     → stabilises training, allows higher LR
#   • 4 conv-blocks (32 → 64 → 128 → 256)
#     → your suggested 256 block, done properly
#   • Flatten + Dense(256) instead of GAP
#     → preserves spatial layout of ELA artifacts
#   • Dropout 0.4 before final Dense
#     → stronger regularisation for 5 k images
# ─────────────────────────────────────────────
def build_model(input_shape=(128, 128, 3)):
    inputs = tf.keras.Input(shape=input_shape)

    # ── augmentation (only active during training) ──
    x = build_augmentation()(inputs)

    # ── Block 1 ──
    x = tf.keras.layers.Conv2D(32, (3, 3), padding="same", use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)      # 128 → 64

    # ── Block 2 ──
    x = tf.keras.layers.Conv2D(64, (3, 3), padding="same", use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)      # 64 → 32

    # ── Block 3 ──
    x = tf.keras.layers.Conv2D(128, (3, 3), padding="same", use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)      # 32 → 16

    # ── Block 4  (your suggested 256-filter block) ──
    x = tf.keras.layers.Conv2D(256, (3, 3), padding="same", use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)      # 16 → 8

    # ── Classifier head ──
    x = tf.keras.layers.Flatten()(x)                 # 8×8×256 = 16 384 features
    x = tf.keras.layers.Dense(256, use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.Dropout(0.4)(x)

    outputs = tf.keras.layers.Dense(2, activation="softmax")(x)

    return tf.keras.Model(inputs, outputs, name="detectify_v2")


# ─────────────────────────────────────────────
# 7) Training entry point
# ─────────────────────────────────────────────
def main():
    X, y = load_dataset()

    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=0.2,
        random_state=SEED,
        stratify=y,
    )
    print(f"Train: {len(X_train)}  |  Val: {len(X_val)}")

    # ── tf.data pipelines ──
    # Augmentation is INSIDE the model, so no special flag needed here.
    train_ds = (
        tf.data.Dataset.from_tensor_slices((X_train, y_train))
        .shuffle(4000, seed=SEED)
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )
    val_ds = (
        tf.data.Dataset.from_tensor_slices((X_val, y_val))
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    # ── Build & summarise ──
    model = build_model(input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    model.summary()

    # ── Compile ──
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    # ── Callbacks ──
    callbacks = [
        # Stop early if val_accuracy doesn't improve for 4 epochs
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=4,
            restore_best_weights=True,
            verbose=1,
        ),
        # Halve LR when val_loss plateaus for 2 epochs
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
        # Save best checkpoint (optional, comment out if Drive not available)
        tf.keras.callbacks.ModelCheckpoint(
            filepath="best_checkpoint.h5",
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
    ]

    # ── Train ──
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )

    # ── Save final model ──
    model.save(MODEL_PATH)
    print(f"\n✅ Saved model → {MODEL_PATH}")
    print("   Exists?", os.path.exists(MODEL_PATH))

    # ── Evaluation ──
    y_prob = model.predict(val_ds, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)

    cm = confusion_matrix(y_val, y_pred)
    print("\nConfusion matrix:\n", cm)
    print("\nClassification report:")
    print(classification_report(y_val, y_pred, target_names=["Fake", "Real"]))

    print("\nFinal epoch metrics:")
    print("  train_acc :", round(float(history.history["accuracy"][-1]),  4))
    print("  val_acc   :", round(float(history.history["val_accuracy"][-1]), 4))


if __name__ == "__main__":
    main()