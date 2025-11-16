Credit Card Transactional Analysis For Fraud Risk

This project is an end-to-end data engineering pipeline built on the Google Cloud Platform to analyze credit card transactions for fraud risk. It automates the ingestion, processing, and analysis of daily transaction files using PySpark, Airflow, and BigQuery.

The repository features a full CI/CD workflow that automatically runs PyTest unit tests for the PySpark logic before deploying the production-ready Airflow DAG and PySpark application scripts to GCS.

Tech Stack

Service

Purpose

Python

Core programming language for all scripts.

PySpark

Used for scalable data validation, transformation, and fraud risk calculation.

Google Cloud Storage (GCS)

Stores raw JSON transaction files, PySpark/Airflow scripts, and archived files.

Dataproc Serverless

Provides a managed, serverless environment for executing the PySpark job.

Google BigQuery

Stores the static cardholders dimension table for data enrichment.

Cloud Composer (Airflow)

Orchestrates the entire pipeline, from file sensing to processing and archival.

PyTest

Used to create and run unit tests for the PySpark transformation logic.

GitHub

Version control and repository hosting.

GitHub Actions

Manages the complete CI/CD workflow (testing and deployment).

Pipeline Architecture & Data Flow

The pipeline is fully orchestrated by Airflow and uses a combination of GCP services to process the data.

                  [GCS (Raw JSONs)]
                         |
(1. File Sensor)         |
                         v
                  [Cloud Composer (Airflow DAG)]
                         |
(2. Trigger Job)         |
                         v
                  [Dataproc Serverless (PySpark Job)]
                  /                     \
(3. Read Cardholders) /                       \ (4. Read Transactions)
                 v                         v
        [BigQuery (Static Table)]       [GCS (Raw JSONs)]
                 \                       /
                  \                     /
                   v                   v
            [PySpark Transformations & Fraud Risk Calculation]
                         |
(5. Archive File)        |
                         v
                  [GCS (Archive Folder)]


Workflow Steps

GCS File Sensor: An Airflow DAG runs on a schedule, using a sensor to wait for a new daily transactions_YYYY-MM-DD.json file to arrive in the GCS raw data bucket.

Trigger Dataproc Job: Once a file is detected, Airflow triggers a PySpark job on Dataproc Serverless.

Data Processing (PySpark): The PySpark script (spark_job.py) executes:

It reads the static cardholders info from the BigQuery table.

It reads the new JSON transaction data from GCS.

It performs data validations (checking for nulls, correct types, etc.).

It joins the two datasets.

It applies transformations to calculate a fraud_risk_level.

Archive File: After the PySpark job successfully completes, the Airflow DAG moves the processed JSON file from the raw data bucket to an archive/ folder.

Automated CI/CD Workflow

This repository uses GitHub Actions for a robust CI/CD pipeline, defined in .github/workflows/ci-cd.yaml.

1. Continuous Integration (CI)

Trigger: On push or pull_request to the dev branch.

Job: run-tests

Action: This job builds a complete Python environment, installs all dependencies from requirements.txt, and runs the PySpark unit tests using pytest. This ensures that all data logic is validated before it can be merged into main.

2. Continuous Deployment (CD)

Trigger: On push (or merge) to the main branch.

Job: deploy-to-prod

Action: This job authenticates to Google Cloud and deploys the production-ready application scripts to GCS, ensuring the pipeline is always running the latest stable code.

airflow_job.py -> gs://[COMPOSER_BUCKET]/dags/

spark_job.py -> gs://[APP_BUCKET]/spark_job/

Local Development & Testing

You can run the PySpark unit tests locally without needing to connect to GCP.

Clone the repository:

git clone [https://github.com/Rehaman24/Credit-card-fraud-analytics.git](https://github.com/Rehaman24/Credit-card-fraud-analytics.git)
cd Credit-card-fraud-analytics


Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate


Install dependencies:
This will install pyspark, pytest, and all other required libraries.

pip install -r requirements.txt


Run the PySpark Unit Tests:
This command will discover and run all tests inside the tests/ directory.

pytest
