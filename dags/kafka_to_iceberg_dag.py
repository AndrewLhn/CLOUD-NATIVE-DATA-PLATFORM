from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType

def init_iceberg_infrastructure():
    catalog = load_catalog(
        "default",
        **{
            "type": "sql",
            "uri": "postgresql+psycopg2://airflow:airflow@airflow-db:5432/airflow",
            "s3.endpoint": "http://minio:9000",
            "s3.access-key-id": "minioadmin",
            "s3.secret-access-key": "minioadmin",
        }
    )
    
    catalog.create_namespace_if_not_exists("my_db")
    
    schema = Schema(
        NestedField(field_id=1, name="id", field_type=IntegerType(), required=True),
        NestedField(field_id=2, name="message", field_type=StringType(), required=False),
    )
    
    catalog.create_table_if_not_exists(
        identifier="my_db.my_table",
        schema=schema
    )

with DAG(
    dag_id='simple_kafka_to_iceberg',
    start_date=datetime(2026, 7, 13),
    schedule_interval='@hourly',
    catchup=False
) as dag:

    init_db_task = PythonOperator(
        task_id='init_iceberg_table',
        python_callable=init_iceberg_infrastructure
    )

    run_kafka_sync = BashOperator(
        task_id='run_kafka_sync',
        bash_command='python /opt/airflow/dags/scripts/your_kafka_consumer.py' 
    )

    init_db_task >> run_kafka_sync