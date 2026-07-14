FROM apache/airflow:2.10.0

# 1. Установка компиляторов под root
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Возвращаемся к пользователю airflow
USER airflow

# 3. Создаем изолированное виртуальное окружение для задач Iceberg
RUN python -m venv /home/airflow/iceberg_env

# 4. Устанавливаем все библиотеки туда (здесь SQLAlchemy 2.x встанет без конфликтов с Airflow!)
RUN /home/airflow/iceberg_env/bin/pip install --no-cache-dir \
    confluent-kafka==2.4.0 \
    pyarrow==14.0.1 \
    "pyiceberg[sql-sqlite]==0.6.0"