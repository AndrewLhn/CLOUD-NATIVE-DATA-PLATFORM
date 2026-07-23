from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="kafka_to_iceberg",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["kafka", "iceberg"],
) as dag:
    BashOperator(
        task_id="consume_kafka_batch",
        bash_command=(
            "env -u PYTHONPATH -u LD_PRELOAD PYTHONNOUSERSITE=1 "
            "/home/airflow/iceberg_env/bin/python "
            "/opt/airflow/dags/kafka_to_iceberg_run.py"
        ),
    )
