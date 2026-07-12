import sys
import os
sys.path.append('/opt/airflow/infra')
from airflow import DAG
from consumer_batch import process_batch
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from consumer_batch import process_batch 

default_args = {'owner': 'andrej', 'retries': 1, 'retry_delay': timedelta(minutes=5)}

with DAG(
    'kafka_to_iceberg_sync',
    default_args=default_args,
    schedule_interval='@hourly', 
    start_date=datetime(2026, 1, 1),
    catchup=False
) as dag:
    
    sync_task = PythonOperator(
        task_id='process_kafka_batch',
        python_callable=process_batch
    )