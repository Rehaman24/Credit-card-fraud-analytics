

```markdown
# Credit Card Transactional Analysis for Fraud Risk

A scalable, end-to-end data pipeline built on the Google Cloud Platform to ingest, process, and analyze daily credit card transactions for fraud risk. This industrial-grade project demonstrates a modern data stack using PySpark, Airflow, and serverless technologies.

## Project Overview

This pipeline provides a complete solution for processing financial transactions. It ingests raw, daily JSON transaction files, enriches them with static cardholder data, performs crucial data validations, and applies business rules to calculate a fraud risk level. The entire process is orchestrated by Airflow (GCP Composer) and leverages the scalability of Dataproc Serverless for PySpark processing.

**Business Goal:** To provide analysts and risk teams with a clean, enriched, and pre-calculated dataset in BigQuery, enabling them to quickly identify and act on high-risk transactions.

## Solution Architecture

This pipeline uses a reactive, polling-based model orchestrated by Airflow. The workflow is triggered by a file sensor (`GCSObjectsWithPrefixExistenceSensor`) that periodically checks a GCS bucket for new transaction files, making it reactive to data arrival.

*(**Note:** You should create and insert your own architecture diagram image here. You can upload it to your repo and link to it.)*
```

[Architecture\_Diagram.png]

```

**Data Flow:**
1.  **File Arrival:** Raw JSON transaction files (e.g., `transactions_2025-02-01.json`) are uploaded daily to a 'transactions' bucket in Google Cloud Storage (GCS).
2.  **Orchestration (Airflow):**
    * The `GCSObjectsWithPrefixExistenceSensor` in Airflow is on a schedule, polling the GCS bucket. When it detects a new file, it marks its task as successful.
    * Once the sensor succeeds, Airflow triggers the next task, `DataprocCreateBatchOperator`.
3.  **Processing (PySpark on Dataproc):**
    * The Dataproc Serverless job spins up and executes the `spark_job.py` application.
    * The Spark job reads the newly arrived JSON data from GCS.
    * It also reads the static `cardholders` table from BigQuery.
    * **Transformations:** The job validates the data (e.g., checks for nulls, valid amounts), enriches transaction data by joining it with cardholder info, and calculates new fields.
    * **Core Logic:** It calculates `transaction_category`, `high_risk` flags, `updated_reward_points`, and a final `fraud_risk_level` (e.g., 'Low', 'High', 'Critical') based on transaction amount, fraud flags, and cardholder risk scores.
4.  **Loading (BigQuery):** The final, enriched DataFrame is written (or appended) to the primary `transactions` table in BigQuery.
5.  **Archiving (Airflow):** After the Spark job succeeds, an Airflow `GCSToGCSOperator` moves the processed JSON file from the 'transactions' landing zone to an 'archive' folder to prevent re-processing.

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| **Cloud Provider** | [![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/) |
| **Data Storage** | [![Google Cloud Storage](https://img.shields.io/badge/Google_Cloud_Storage-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/storage) |
| **Data Warehouse** | [![Google BigQuery](https://img.shields.io/badge/Google_BigQuery-4285F4?style=for-the-badge&logo=google-bigquery&logoColor=white)](https://cloud.google.com/bigquery) |
| **Data Processing** | [![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)](https://spark.apache.org/) (via PySpark) |
| **Processing Platform**| [![Dataproc](https://img.shields.io/badge/Dataproc_Serverless-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/dataproc) |
| **Orchestration** | [![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)](https://airflow.apache.org/) (via GCP Composer) |
| **Core Language** | [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) |
| **Testing** | [![PyTest](https://img.shields.io/badge/PyTest-0A9B5C?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/) |
| **CI/CD** | [![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions) |

## 🔬 Key Features & Business Logic

This pipeline goes beyond simple ETL by embedding critical business logic within the Spark application.

* **Data Validation:** The pipeline automatically filters out records with invalid data (e.g., negative transaction amounts, null `cardholder_id` or `merchant_id`) to ensure data integrity.
* **Data Enrichment:** Enriches raw transactions by joining with the `cardholders` table to add customer details (name, email, country, etc.) to each transaction.
* **Reward Point Calculation:** A stateful transformation that calculates `updated_reward_points` for each cardholder based on `transaction_amount` (e.g., 1 point per $10 spent).
* **Fraud Risk Calculation:** The core logic of this project. A `fraud_risk_level` is assigned based on a rules engine:
    * **`Critical`**: The transaction is flagged as `high_risk` (e.g., `fraud_flag` is true, or amount > $10,000).
    * **`High`**: The cardholder's static `risk_score` is > 0.3 OR the transaction was already flagged as `fraud_flag` = true.
    * **`Low`**: All other cases.
    * *(This logic is fully unit-tested in `test_credit_txn_processing.py`.)*

## 🧪 Unit Testing

For a financial application, reliability is paramount. This project uses `PyTest` to validate the Spark transformation logic.

The test suite (`test_credit_txn_processing.py`) creates an in-memory Spark session, defines mock input data (for transactions and cardholders), and runs the *exact* same transformation logic as the production job.

**Tests include:**
* **Schema Validation:** Ensures the output schema is correct.
* **Reward Point Logic:** Asserts that `updated_reward_points` are calculated correctly.
* **Risk Level Accuracy:**
    * Asserts a transaction becomes 'Critical' when `high_risk` is true.
    * Asserts a transaction becomes 'High' when `risk_score` is high.
* **Categorization:** Verifies that `transaction_category` (Low, Medium, High) is assigned correctly based on amount.

This testing strategy ensures that new changes to the business logic are vetted *before* deployment.

## 🤖 CI/CD with GitHub Actions

A full CI/CD pipeline is configured using GitHub Actions (`.github/workflows/main.yml`). This workflow automates testing and deployment.

**On `push` to the `main` branch:**
1.  **Checkout Code:** The repository is checked out.
2.  **Set up Python:** The correct Python environment is initialized.
3.  **Install Dependencies:** Installs `pyspark`, `pytest`, etc., from `requirements.txt`.
4.  **Run Unit Tests:** Executes `pytest`. If any test fails, the pipeline stops, and the deployment is CANCELED.
5.  **Deploy to GCS:** If all tests pass, the workflow authenticates with GCP and copies the updated files (`airflow_job.py` and `spark_job.py`) to their respective GCS buckets, making the new logic live.

This process ensures that no code that breaks our business logic or tests can ever make it to production.

## 📂 Repository Structure

```

├── .github/workflows/          \# CI/CD pipeline definitions
│   └── main.yml
├── dags/                       \# Airflow DAGs
│   └── airflow\_job.py
├── data/                       \# Sample data
│   ├── cardholders.csv
│   └── transactions\_2025-02-01.json
├── spark\_job/                  \# PySpark application
│   └── spark\_job.py
├── tests/                      \# Unit and integration tests
│   └── test\_credit\_txn\_processing.py
├── .gitignore
├── requirements.txt            \# Python dependencies
└── README.md

```

## 🚀 How to Set Up & Deploy

### Prerequisites
* A Google Cloud Platform (GCP) project.
* `gcloud` CLI installed and authenticated.
* GCP APIs enabled: BigQuery, GCS, Dataproc, Cloud Composer.
* A configured Cloud Composer (Airflow) environment.
* GCS Buckets created for DAGs, Spark jobs, and data (landing/archive).

### Step-by-Step Guide
1.  **Set up BigQuery:**
    * Create a dataset (e.g., `credit_card`).
    * Load the `cardholders.csv` data into a new table named `cardholders`.

2.  **Configure GCS:**
    * Create a bucket structure (e.g., `gs://credit-card-data-analysis_24`).
    * Create folders: `dags`, `spark_job`, `transactions`, `archive`.

3.  **Configure Airflow / Composer:**
    * Set the `gcs_bucket` variable in `airflow_job.py` to match your GCS bucket.
    * Ensure your Composer environment's service account has permissions to:
        * Read/Write to the GCS buckets.
        * Read/Write to the BigQuery tables.
        * Submit jobs to Dataproc.

4.  **Deploy Files (via CI/CD or Manually):**
    * The CI/CD pipeline will automatically deploy files to GCS.
    * **Manually:**
        * Upload `airflow_job.py` to your `dags` GCS folder.
        * Upload `spark_job.py` to your `spark_job` GCS folder.

5.  **Run the Pipeline:**
    * Un-pause the `credit_card_transactions_dataproc_dag` in your Airflow UI.
    * Upload one of the sample `transactions_*.json` files to the `transactions` GCS folder.
    * The file sensor will detect it, and the DAG will trigger, processing the data into BigQuery.

## 🌟 Future Improvements
* **Move to Streaming:** Convert the pipeline to a real-time system using **Pub/Sub** and **Dataflow** for immediate fraud detection.
* **Advanced Fraud Model:** Replace the simple rule-based system with a **Vertex AI** auto-ML model trained on historical fraud data for more nuanced scoring.
* **Data Quality Checks:** Integrate **Great Expectations** into the PySpark job to automatically quarantine bad data that fails statistical checks.
```
