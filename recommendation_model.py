# model_stream_update.py
# --------------------------------------------------------------
# Load existing model (.pkl), predict for new data (file/stream),
# and continue training with new data.
# --------------------------------------------------------------

import joblib # Changed from pickle to joblib
import pandas as pd
import numpy as np
# from kafka import KafkaConsumer
import json
import sys
import io
from sklearn.model_selection import train_test_split

# ====== Load Saved Model ======
MODEL_PATH = "streaming/recommendation_model.pkl"  # update if needed
print(f"[INFO] Loading saved model from {MODEL_PATH} ...")
# Changed from pickle.load to joblib.load
model = joblib.load(MODEL_PATH)

# ====== Input Option ======
mode = input("Enter mode ('file' or 'stream'): ").strip().lower()

# --------------------------------------------------------------
# Case 1: Predict from new CSV file
# --------------------------------------------------------------
if mode == "file":
    file_path = input("Enter CSV file path: ").strip()
    df_new = pd.read_csv(file_path)
    print(f"[INFO] Loaded {len(df_new)} new records.")

    # Separate target if available
    if 'purchase_percent' in df_new.columns:
        X_new = df_new.drop(columns=['purchase_percent'])
        y_new = df_new['purchase_percent']
    else:
        X_new = df_new
        y_new = None

    # Predict
    preds = model.predict(X_new)
    df_new['predicted_purchase_percent'] = preds
    print("[INFO] Predictions generated.")
    print(df_new.head())


# --------------------------------------------------------------
# Case 2: Predict from Kafka Stream
# --------------------------------------------------------------
elif mode == "stream":
    topic = "ecommerce_data"
    broker = "localhost:9092"
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[broker],
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id="model_predictor_group"
    )
    print(f"[INFO] Listening to Kafka topic '{topic}' ...")

    records = []
    for message in consumer:
        data = message.value
        records.append(data)
        df_stream = pd.DataFrame([data])

        # Handle missing or categorical
        df_stream = pd.get_dummies(df_stream, columns=['category'], drop_first=True)
        df_stream = df_stream.fillna(df_stream.mean())

        # Predict
        pred = model.predict(df_stream)[0]
        print(f"Predicted purchase_percent: {pred:.2f}")

        # Optional: accumulate batch and retrain
        if len(records) >= 500:
            df_batch = pd.DataFrame(records)
            if 'purchase_percent' in df_batch.columns:
                X = df_batch.drop(columns=['purchase_percent'])
                y = df_batch['purchase_percent']
                X = pd.get_dummies(X, columns=['category'], drop_first=True)
                X = X.fillna(X.mean())
                records = []

else:
    print("Invalid mode. Choose 'file' or 'stream'.")
    sys.exit(1)
