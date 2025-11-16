# Credit Card Transactional Analysis for Fraud Risk (Industrial Project)

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)  
[![PySpark](https://img.shields.io/badge/PySpark-3.5-orange?logo=apache-spark&logoColor=white)](https://spark.apache.org/)  
[![GCP](https://img.shields.io/badge/GCP-Data%20Pipeline-red?logo=googlecloud&logoColor=white)](https://cloud.google.com/)  
[![Airflow](https://img.shields.io/badge/Airflow-2.7-blue?logo=apache-airflow&logoColor=white)](https://airflow.apache.org/)  
[![Build](https://img.shields.io/github/actions/workflow/status/Rehaman24/Credit-card-fraud-analytics/ci-cd.yml?branch=main)](https://github.com/Rehaman24/Credit-card-fraud-analytics/actions)

---

## 🚀 Project Overview
This project implements an end-to-end **ETL pipeline** for **credit card fraud risk analysis**. Using **PySpark**, **GCP services**, and **Airflow orchestration**, the pipeline ingests daily transactional data, performs validation and transformations, calculates fraud risk scores, and stores results in **BigQuery**.  

The project is **production-ready** with **unit tests** and **CI/CD automation** using **GitHub Actions**.  

---

## 🛠 Tech Stack
- **Python 3.11**  
- **PySpark 3.5**  
- **Google Cloud Storage (GCS)**  
- **GCP Dataproc Serverless**  
- **BigQuery**  
- **GCP Composer (Airflow)**  
- **PyTest**  
- **GitHub / GitHub Actions**  

---

## ⚙️ Features & Workflow

1. **BigQuery Static Table**: Stores Card Holders information.  
2. **PySpark Processing**:
   - Reads Card Holders info from BigQuery.  
   - Reads daily transactional JSON files from GCS.  
   - Performs data validations and transformations.  
   - Calculates fraud risk scores.  
3. **Airflow DAG Orchestration**:
   - Detects new transaction JSON files in GCS.  
   - Triggers PySpark job on **Dataproc Serverless**.  
   - Moves processed files to an **archive folder**.  
4. **Testing**: Unit tests for PySpark logic using **PyTest**.  
5. **CI/CD Automation**: GitHub Actions deploys DAGs and PySpark scripts, and runs unit tests automatically.  

---

## 📊 ETL Workflow Diagram

```mermaid
flowchart TD
    A[New Transaction JSON Files in GCS] --> B[Airflow DAG Sensor]
    B --> C[Trigger PySpark ETL Job on Dataproc Serverless]
    C --> D[Read Cardholder Info from BigQuery]
    C --> E[Validate & Transform Transaction Data]
    E --> F[Calculate Fraud Risk Scores]
    F --> G[Write Results to BigQuery]
    C --> H[Move Processed Files to Archive Folder]
    B --> I[Trigger Alerts/Logs if Job Fails]
