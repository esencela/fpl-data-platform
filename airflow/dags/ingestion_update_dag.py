from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator #type: ignore
from docker.types import Mount #type: ignore
from datetime import datetime
import os

env_variables = {
    'RAW_DATA_DIR': os.getenv('RAW_DATA_DIR'),
    'CURRENT_SEASON': os.getenv('CURRENT_SEASON'),
    'POSTGRES_DB': os.getenv('POSTGRES_DB'),
    'POSTGRES_USER': os.getenv('POSTGRES_USER'),
    'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'POSTGRES_HOST': os.getenv('POSTGRES_HOST'),
    'POSTGRES_PORT': os.getenv('POSTGRES_PORT')
}

BASE_DIR = os.getenv('HOST_DATA_DIR')

with DAG(
    'ingestion_update_dag',
    start_date=datetime(2026, 6, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1
) as dag:
    
    extract_fpl = DockerOperator(
        task_id='extract_fpl',
        image='fpl-data-platform-ingestion:latest',
        command='fpl-extract',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
        environment=env_variables
    )

    extract_vaastav = DockerOperator(
        task_id='extract_vaastav',
        image='fpl-data-platform-ingestion:latest',
        command='vaastav-extract',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
        environment=env_variables
    )

    extract_understat = DockerOperator(
        task_id='extract_understat',
        image='fpl-data-platform-ingestion:latest',
        command='understat-extract',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
        environment=env_variables
    )

    load_fpl = DockerOperator(
        task_id='load_fpl',
        image='fpl-data-platform-ingestion:latest',
        command='fpl-load',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
        environment=env_variables
    )

    load_vaastav = DockerOperator(
        task_id='load_vaastav',
        image='fpl-data-platform-ingestion:latest',
        command='vaastav-load',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
        environment=env_variables
    )

    load_understat = DockerOperator(
        task_id='load_understat',
        image='fpl-data-platform-ingestion:latest',
        command='understat-load',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
        environment=env_variables
    )

    extract_tasks = [extract_fpl, extract_vaastav, extract_understat]
    load_tasks = [load_fpl, load_vaastav, load_understat]

    for extract, load in zip(extract_tasks, load_tasks):
        extract >> load