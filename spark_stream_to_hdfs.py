from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, lit, when, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# ----------------------------------------------------------
# 1. Spark Session
# ----------------------------------------------------------
spark = (
    SparkSession.builder
    .appName("EcommerceStreamToHDFS")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# ----------------------------------------------------------
# 2. Define schema (must match producer.py)
# ----------------------------------------------------------
schema = StructType([
    StructField("num_clicks", IntegerType(), True),
    StructField("rating", DoubleType(), True),
    StructField("discount_percentage", DoubleType(), True),
    StructField("purchases_last_30_days", IntegerType(), True),
    StructField("category", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("purchase_percent", DoubleType(), True)
])

# ----------------------------------------------------------
# 3. Read stream from Kafka
# ----------------------------------------------------------
kafka_bootstrap = "kafka:29092"      # for internal Docker communication
topic_name = "ecommerce_data"

raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap)
    .option("subscribe", topic_name)
    .option("startingOffsets", "latest")
    .load()
)

# ----------------------------------------------------------
# 4. Parse JSON
# ----------------------------------------------------------
parsed_stream = (
    raw_stream
    .selectExpr("CAST(value AS STRING)")
    .select(from_json(col("value"), schema).alias("data"))
    .select("data.*")
)

# ----------------------------------------------------------
# 5. Define batch function
# ----------------------------------------------------------
output_path = "hdfs://ecommerce-recommendation-namenode-1:9000/stream_output/combined/"
checkpoint_path = "hdfs://ecommerce-recommendation-namenode-1:9000/stream_output/checkpoints/"

def process_batch(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    # --- Step 1: Compute average rating (current batch) ---
    avg_rating = batch_df.select(avg("rating")).collect()[0][0]
    avg_rating = avg_rating if avg_rating is not None else 3.0

    # --- Step 2: Fill NA/blank ratings with running avg ---
    filled_df = batch_df.withColumn(
        "rating",
        when(col("rating").isNull(), lit(avg_rating)).otherwise(col("rating"))
    )

    # --- Step 3: Compute aggregation per category ---
    agg_df = filled_df.groupBy("category").agg(
        avg("rating").alias("avg_rating"),
        count("*").alias("records")
    ).withColumn("_batch_id", lit(batch_id))

    # --- Step 4: Join aggregation with filled original data ---
    combined_df = filled_df.join(
        agg_df.select("category", "avg_rating", "records", "_batch_id"),
        on="category",
        how="left"
    )

    # --- Step 5: Write to HDFS ---
    combined_df.write.mode("append").parquet(output_path)

# ----------------------------------------------------------
# 6. Streaming write
# ----------------------------------------------------------
query = (
    parsed_stream.writeStream
    .outputMode("append")
    .trigger(processingTime="30 seconds")
    .foreachBatch(process_batch)
    .option("checkpointLocation", checkpoint_path)
    .start()
)

query.awaitTermination()

