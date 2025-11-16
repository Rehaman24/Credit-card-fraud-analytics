# Credit Card Transactional Analysis for Fraud Risk

## Table of Contents
* [Introduction](#introduction)
* [Key Features](#key-features)
* [Solution Architecture](#solution-architecture)
* [Technology Stack](#technology-stack)
* [CI/CD Pipeline](#cicd-pipeline)
* [Unit Testing](#unit-testing)
* [Setup and Deployment](#setup-and-deployment)
* [Future Improvements](#future-improvements)

## Introduction
This project implements a scalable, end-to-end data pipeline on the Google Cloud Platform (GCP) to process credit card transactions and assess fraud risk. It ingests daily JSON transaction data, validates it, enriches it with cardholder information from BigQuery, and applies business logic to calculate risk levels. The entire workflow is orchestrated using Apache Airflow (GCP Composer) and processed using PySpark on Dataproc Serverless, with final analysis-ready data loaded into BigQuery. This project demonstrates a robust, automated, and tested data engineering solution.

## Key Features
* **Serverless Processing:** Uses **Dataproc Serverless** for scalable, cost-effective PySpark jobs without managing clusters.
* **Workflow Orchestration:** Employs an **Airflow DAG** in GCP Composer to manage the entire workflow, from file sensing to processing and archiving.
* **Complex Transformations:** Performs stateful calculations (e.g., fraud risk scoring based on multiple rules) and enriches transaction data with static cardholder info from BigQuery.
* **Automated CI/CD:** Integrates **GitHub Actions** to automatically run unit tests (PyTest) and deploy the Airflow DAG and PySpark script to GCS buckets.
* **Data Validation:** Includes a validation layer in the PySpark script to ensure data quality before loading into BigQuery.

## Solution Architecture
*(Note: You will need to create and upload your own architecture diagram and name it `Architecture_Diagram.png` in your repo for this image to load.)*

`[Architecture_Diagram.png]`

**Data Flow:**
1.  **File Arrival:** Daily JSON transaction files (e.g., `transactions_2025-02-01.json`) are uploaded to a Google Cloud Storage (GCS) `transactions/` folder.
2.  **Orchestration (Airflow):** An Airflow DAG, managed by GCP Composer, uses a `GCSObjectsWithPrefixExistenceSensor` to poll for the new file.
3.  **Processing (Dataproc):** Once the file is detected, the DAG triggers a `DataprocCreateBatchOperator` to run the PySpark (`spark_job.py`) job on Dataproc Serverless.
4.  **Transformation (PySpark):** The Spark job reads the new JSON file from GCS and the static `cardholders` table from BigQuery. It then performs data validation, enriches the data, calculates reward points, and applies rules to determine a `fraud_risk_level`.
5.  **Loading (BigQuery):** The final, processed DataFrame is appended to the main `transactions` table in BigQuery.
6.  **Archiving (Airflow):** Upon successful completion of the Spark job, an `GCSToGCSOperator` moves the processed JSON file from the `transactions/` folder to an `archive/` folder to prevent re-processing.

## Technology Stack
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

## CI/CD Pipeline
*(Note: You will need to create and upload your own CI/CD diagram and name it `CI_CD_Pipeline.png` in your repo for this image to load.)*

`[CI_CD_Pipeline.png]`

The CI/CD pipeline is automated using GitHub Actions. The workflow is defined in `.github/workflows/main.yml`.
1.  **Trigger:** The pipeline automatically starts on every `push` or `pull_request` to the `main` branch.
2.  **Setup:** It checks out the code, sets up a Python 3.x environment, and installs all dependencies from `requirements.txt`.
3.  **Unit Testing:** It runs the `pytest` command to execute all unit tests in the `tests/` directory (e.g., `test_credit_txn_processing.py`).
4.  **Block Deployment on Failure:** If any test fails, the pipeline stops, preventing buggy code from being deployed.
5.  **Deployment:** If all tests pass on a `push` to `main`, the workflow authenticates with Google Cloud and copies the updated Airflow DAG (`airflow_job.py`) and the PySpark script (`spark_job.py`) to their respective GCS buckets.

## Unit Testing
Unit tests are implemented using **PyTest** to ensure the core business logic in the PySpark application is correct. The tests (`test_credit_txn_processing.py`) create a local Spark session, build mock DataFrames for transactions and cardholders, and assert that the fraud risk calculation, reward point updates, and transformations produce the expected output for various scenarios (e.g., 'Critical' risk, 'High' risk, 'Low' risk).

## Setup and Deployment
1.  **GCP Setup:**
    * Enable necessary APIs: Compute Engine, BigQuery, GCS, Dataproc, Cloud Composer.
    * Create a BigQuery dataset (e.g., `credit_card`).
    * Create the static `cardholders` table in BigQuery and load the `cardholders.csv` data.
    * Create GCS buckets for DAGs, PySpark scripts, and data (e.g., `gs://<your-bucket>/dags`, `gs://<your-bucket>/spark_job`, `gs://<your-bucket>/transactions`, `gs://<your-bucket>/archive`).
2.  **Airflow Setup:**
    * Set up a Cloud Composer 2 environment.
    * Ensure the Composer service account has permissions for GCS (Read/Write), BigQuery (Job User, Data Editor), and Dataproc (Editor/Job User).
    * Update the variables in `airflow_job.py` (like `gcs_bucket`) to match your environment.
3.  **Deployment (CI/CD):**
    * Fork this repository.
    * Configure GitHub Actions secrets for GCP authentication (`GCP_PROJECT_ID`, `GCP_SA_KEY`).
    * Update the `main.yml` workflow file to point to your GCS buckets.
    * Push your code to the `main` branch. The GitHub Action will automatically test and deploy the DAG and PySpark files to GCS.
4.  **Run the Pipeline:**
    * Upload one of the sample `transactions_*.json` files to the `transactions/` GCS folder.
    * The Airflow DAG sensor will detect the file, trigger the Dataproc job, and process the data into BigQuery.

## Future Improvements
* **Move to Streaming:** Replace the batch, polling-based architecture with a real-time streaming pipeline using **Pub/Sub** and **Dataflow** for immediate fraud detection.
* **Advanced Fraud Model:** Integrate a **Vertex AI** machine learning model to replace the rule-based fraud logic for more accurate, dynamic risk scoring.
* **Data Quality Checks:** Add **Great Expectations** or similar data quality checks within the PySpark job to automatically quarantine or flag bad data that fails validation.
