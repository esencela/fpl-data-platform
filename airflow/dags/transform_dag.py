from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
import os

env_variables = {
    'POSTGRES_DB': os.getenv('POSTGRES_DB'),
    'POSTGRES_USER': os.getenv('POSTGRES_USER'),
    'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'POSTGRES_HOST': os.getenv('POSTGRES_HOST'),
    'POSTGRES_PORT': os.getenv('POSTGRES_PORT')
}

with DAG(
    'transform_dag',
    start_date=datetime(2026, 6, 1),
    schedule='@daily',
    catchup=False
) as dag:
    
    transform_dbt = DockerOperator(
        task_id='transform_dbt',
        image='fpl-data-platform-dbt:latest',
        command='dbt run',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        environment=env_variables
    )

    test_dbt = DockerOperator(
        task_id='test_dbt',
        image='fpl-data-platform-dbt:latest',
        command='dbt test',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        environment=env_variables
    )

    transform_dbt >> test_dbt