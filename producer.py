"""
producer.py
-----------------------------------
Generates mock e-commerce data and streams it to Kafka.
Each record contains:
    - num_clicks
    - rating
    - discount_percentage
    - purchases_last_30_days
    - category
    - price
    - purchase_percent (target variable)
"""

from kafka import KafkaProducer
import pandas as pd
import numpy as np
import json
import time

# ============ Kafka Configuration ============
KAFKA_BROKER = "kafka:9092"      # Change if your container name or host differs
TOPIC = "ecommerce_data"         # Kafka topic name

# ============ Data Generation ============
np.random.seed(42)
n = 50000  # Number of records to simulate

# Generate columns
num_clicks = np.random.randint(0, 500, n)
rating = np.random.choice(
    [np.round(np.random.uniform(1, 5), 1), np.nan], n, p=[0.8, 0.2]
)
discount_percentage = np.random.randint(0, 70, n)
purchases_last_30_days = np.random.randint(0, 200, n)
category = np.random.choice(
    ['Electronics', 'Clothing', 'Home', 'Beauty', 'Books'], n
)
price = np.round(np.random.uniform(100, 5000, n), 2)

# Complex function for purchase likelihood
purchase_score = (
    0.3 * np.log1p(num_clicks) +
    0.4 * np.nan_to_num(rating, nan=3.0) +
    0.25 * (discount_percentage / 10) +
    0.2 * np.log1p(purchases_last_30_days) -
    0.0005 * price +
    np.random.normal(0, 0.5, n)
)

# Scale to 0–100 range
purchase_percent = np.clip(
    (purchase_score - np.min(purchase_score)) /
    (np.max(purchase_score) - np.min(purchase_score)) * 100, 0, 100
)

# Build DataFrame
df = pd.DataFrame({
    'num_clicks': num_clicks,
    'rating': rating,
    'discount_percentage': discount_percentage,
    'purchases_last_30_days': purchases_last_30_days,
    'category': category,
    'price': price,
    'purchase_percent': purchase_percent
})

# ============ Kafka Producer Setup ============
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"[INFO] Starting to send {len(df)} records to Kafka topic '{TOPIC}'...")

# ============ Stream Data to Kafka ============
for _, row in df.iterrows():
    message = row.to_dict()
    producer.send(TOPIC, value=message)
    time.sleep(0.01)  # simulate real-time stream (~100 msgs/sec)

producer.flush()
print("[INFO] ✅ All messages sent successfully to Kafka.")

