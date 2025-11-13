# Ecommerce Recommendation Using Big-Data Analytics

An end-to-end real-time data pipeline using **Kafka → Spark Streaming → HDFS → Spark ML→UI**.

---

## 1. Prerequisites
- Docker & Docker Compose  
- Python 3  
- Project structure:
```
.
│── docker-compose.yml
│── streaming/
│     ├── producer.py
│     └── spark_stream_to_hdfs.py
│── model/
      └── train_model.py
```

---

## 2. Start the Cluster
```
docker compose up -d
```

---

## 3. Create Kafka Topic
```
docker exec -it ecommerce-recommendation-kafka-1 kafka-topics.sh --create --topic ecommerce_data --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1
```

---

## 4. Run the Data Producer
```
python3 streaming/producer.py
```

---

## 5. Run Spark Streaming Job
```
docker cp streaming/spark_stream_to_hdfs.py ecommerce-recommendation-spark-master-1:/opt/bitnami/spark/
docker exec -it ecommerce-recommendation-spark-master-1 spark-submit /opt/bitnami/spark/spark_stream_to_hdfs.py
```

---

## 6. Check HDFS Output
```
docker exec -it ecommerce-recommendation-namenode-1 hdfs dfs -ls /stream_output/combined
```

---

## 7. Train ML Model
```
docker exec -it ecommerce-recommendation-spark-master-1 spark-submit /opt/bitnami/spark/model/train_model.py
```

---

## 8. Run UI
```
streamlit run streaming/ui_recommendation.py
```

---

## 9. Stop Services
```
docker compose down
```

---

## UI Access
- Spark UI at http://localhost:8080  
- HDFS NameNode at http://localhost:9870  
- User Interface at http://localhost:8501
- Kafka Drop at http://localhost:9999
