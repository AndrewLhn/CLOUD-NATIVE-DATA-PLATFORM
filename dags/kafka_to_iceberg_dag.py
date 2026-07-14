from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    'simple_kafka_to_iceberg',
    start_date=datetime(2026, 1, 1),
    schedule_interval='@hourly',
    catchup=False
) as dag:
    
    run_process = BashOperator(
        task_id='run_kafka_sync',
        bash_command=(
            "env -u PYTHONPATH -u LD_PRELOAD PYTHONNOUSERSITE=1 "
            "/home/airflow/iceberg_env/bin/python /opt/airflow/dags/kafka_to_iceberg_run.py"
        )
    )