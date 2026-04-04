import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

# -----------------------------
# Load dataset
# -----------------------------
data = pd.read_csv("hazard_data_demo.csv")

print("\nDataset preview:\n")
print(data.head())

# -----------------------------
# Feature selection
# -----------------------------
features = data[["water_level","crowd_density"]].values

# -----------------------------
# Normalize
# -----------------------------
scaler = MinMaxScaler()
X = scaler.fit_transform(features)

# -----------------------------
# Train/validation split
# -----------------------------
X_train, X_val = train_test_split(X,test_size=0.2,random_state=42)

# -----------------------------
# Add noise (denoising AE)
# -----------------------------
noise_factor = 0.05

X_train_noisy = X_train + noise_factor*np.random.normal(size=X_train.shape)
X_val_noisy = X_val + noise_factor*np.random.normal(size=X_val.shape)

X_train_noisy = np.clip(X_train_noisy,0.,1.)
X_val_noisy = np.clip(X_val_noisy,0.,1.)

# -----------------------------
# Build Autoencoder
# -----------------------------
input_dim = X.shape[1]

model = models.Sequential([
    layers.Input(shape=(input_dim,)),
    layers.Dense(4,activation="relu"),
    layers.Dense(2,activation="relu"),
    layers.Dense(4,activation="relu"),
    layers.Dense(input_dim,activation="sigmoid")
])

model.summary()

model.compile(
    optimizer=tf.keras.optimizers.Adam(0.001),
    loss="mse"
)

# -----------------------------
# Early stopping
# -----------------------------
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)

# -----------------------------
# Train
# -----------------------------
history = model.fit(
    X_train_noisy,
    X_train,
    validation_data=(X_val_noisy,X_val),
    epochs=100,
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

# -----------------------------
# Plot training curve
# -----------------------------
plt.figure()

plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")

plt.title("Autoencoder Training Curve")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()

plt.tight_layout()

plt.savefig("training_curve.png")

# -----------------------------
# Reconstruction error
# -----------------------------
recon = model.predict(X)

mse = np.mean(np.square(X-recon),axis=1)

data["dl_risk_score"] = mse

# -----------------------------
# Threshold
# -----------------------------
threshold = np.percentile(mse,95)

data["dl_anomaly"] = data["dl_risk_score"] > threshold

print("\nAnomaly threshold:",threshold)
print("Detected anomalies:",data["dl_anomaly"].sum())

# -----------------------------
# Histogram
# -----------------------------
plt.figure()

plt.hist(mse, bins=50)

plt.title("Reconstruction Error Distribution")
plt.xlabel("Reconstruction Error")
plt.ylabel("Frequency")

plt.tight_layout()
plt.savefig("reconstruction_error_hist.png")

# -----------------------------
# Isolation Forest
# -----------------------------
iso_model = IsolationForest(contamination=0.05,random_state=42)

iso_pred = iso_model.fit_predict(X)
iso_pred = (iso_pred == -1)

data["iso_anomaly"] = iso_pred

# -----------------------------
# Ground truth label
# -----------------------------
data["true_hazard"] = (
    (data["water_level"]>0.6) |
    (data["crowd_density"]>0.6)
)

y_true = data["true_hazard"]

# Predictions
y_fuzzy = data["risk_score"] > 0.5
y_dl = data["dl_anomaly"]
y_iso = data["iso_anomaly"]

# -----------------------------
# Load GNN predictions
# -----------------------------
try:
    import geopandas as gpd

    gnn_edges = gpd.read_file("gnn_risk_edges.geojson")

    print("\nGNN file loaded successfully")

    if "gnn_risk" in gnn_edges.columns:

        # convert to boolean prediction
        y_gnn = gnn_edges["gnn_risk"].astype(bool)

        # trim length to match dataset if needed
        y_gnn = y_gnn[:len(y_true)]

    else:
        print("Column 'gnn_risk' not found in GNN file")
        y_gnn = None

except Exception as e:
    print("GNN results could not be loaded:", e)
    y_gnn = None

# -----------------------------
# Evaluation
# -----------------------------
def evaluate(name,y_pred):
    return {
        "Model":name,
        "Accuracy":accuracy_score(y_true,y_pred),
        "Precision":precision_score(y_true,y_pred),
        "Recall":recall_score(y_true,y_pred),
        "F1 Score":f1_score(y_true,y_pred)
    }

results = []

results.append(evaluate("Fuzzy Logic",y_fuzzy))
results.append(evaluate("Isolation Forest",y_iso))
results.append(evaluate("Autoencoder (DL)",y_dl))

if y_gnn is not None:
    results.append(evaluate("Graph Neural Network",y_gnn))

results_df = pd.DataFrame(results)

print("\n==============================")
print("MODEL COMPARISON")
print("==============================\n")

print(results_df)

# -----------------------------
# Comparison chart
# -----------------------------
results_df.set_index("Model")[["Accuracy","Precision","Recall","F1 Score"]].plot(
    kind="bar",
    figsize=(9,6)
)

plt.title("Model Performance Comparison")
plt.ylabel("Score")
plt.ylim(0,1)

plt.tight_layout()

plt.savefig("model_comparison.png")

plt.show()

# -----------------------------
# Save output
# -----------------------------
data.to_csv("edges_with_dl_risk.csv",index=False)

print("\nSaved results → edges_with_dl_risk.csv")