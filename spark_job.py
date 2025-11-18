from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, round, concat, to_timestamp

# Create spark session
spark = SparkSession.builder \
    .appName("Advanced Credit Card data analysis") \
    .getOrCreate()

# JSON file location
JSON_FILE_PATH = 'gs://credit-card-data-analysis_24/transactions/transactions_*.json'

# BigQuery tables
BQ_PROJECT_ID = 'bigqueryprojects24'
BQ_DATASET = 'credit_card'
BQ_TRANSACTIONS_TABLE = f'{BQ_PROJECT_ID}:{BQ_DATASET}.transactions'
BQ_CARDHOLDERS_TABLE = f"{BQ_PROJECT_ID}:{BQ_DATASET}.BQ_CARDHOLDERS_TABLE"

# Load static card holder data from BigQuery
cardholder_df = spark.read.format("bigquery").option("table", BQ_CARDHOLDERS_TABLE).load()

# Load daily transaction data
transactions_df = spark.read.option("multiline", "true").json(JSON_FILE_PATH)

# Data validations
transactions_df = transactions_df.filter(
    (col("transaction_amount") >= 0) &
    (col("transaction_status").isin('SUCCESS', 'FAILED', 'PENDING')) &
    (col("cardholder_id").isNotNull()) &
    (col("merchant_id").isNotNull())
)

# Data transformations
transactions_df = transactions_df.withColumn(
    "transaction_category",
    when(col("transaction_amount") <= 100, lit('Low'))
     .when((col("transaction_amount") > 100) & (col("transaction_amount") <= 500), lit('Medium'))
     .otherwise(lit('High'))
).withColumn(
    "transaction_timestamp", to_timestamp(col("transaction_timestamp"))
).withColumn(
    "high_risk", (col("fraud_flag") == True) | (col("transaction_amount") > 10000) | (col("transaction_category") == 'High')
).withColumn(
    "merchant_info", concat(col("merchant_name"), lit('-'), col("merchant_location"))
)

enriched_df = transactions_df.join(cardholder_df, on='cardholder_id', how='left')

# Update reward points (Earn 1 point per $10 spent)
enriched_df = enriched_df.withColumn(
    "updated_reward_points", col('reward_points') + round(col("transaction_amount") / 10)
)

# Calculate fraud risk level
enriched_df = enriched_df.withColumn(
    'fraud_risk_level',
    when(col('high_risk') == True, lit('Critical'))
     .when((col("risk_score") > 0.3) | (col("fraud_flag") == True), lit('High'))
     .otherwise(lit('Low'))
)

# Write final processed data to BigQuery
enriched_df.write.format('bigquery') \
    .option("table", BQ_TRANSACTIONS_TABLE) \
    .option("writeMethod", 'direct') \
    .mode("append").save()

print(f'Successfully processed file: {JSON_FILE_PATH}')
print("Advanced Transactions Processing Completed")




#trigger workflow for demo push local to dev 