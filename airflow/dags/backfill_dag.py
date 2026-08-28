from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator #type: ignore
from airflow.decorators import task #type: ignore
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
    'backfill_dag',
    start_date=datetime(2026, 6, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1
) as dag:

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

    seed_dbt = DockerOperator(
        task_id='seed_dbt',
        image='fpl-data-platform-dbt:latest',
        command='dbt seed',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        environment=env_variables
    )

    list_seasons = DockerOperator(
        task_id='list_seasons',
        image='fpl-data-platform-ingestion:latest',
        command='fpl-list-seasons',
        retrieve_output=True,
        retrieve_output_path='/tmp/airflow_xcom_seasons.json',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
        environment=env_variables
    )

    @task
    def backfill_load_and_transform(**context):
        ti = context['ti']
        seasons = ti.xcom_pull(task_ids='list_seasons')

        for season in seasons:
            load_task = DockerOperator(
                task_id=f'load_fpl_{season}',
                image='fpl-data-platform-ingestion:latest',
                command=f'fpl-load {season}',
                auto_remove=True,
                docker_url='unix://var/run/docker.sock',
                network_mode='fpl-data-platform_default',
                mounts=[Mount(target='/app/data', source=BASE_DIR, type='bind')],
                environment=env_variables
            )

            load_task.execute(context=context)

            transform_task = DockerOperator(
                    task_id=f'transform_dbt_{season}',
                    image='fpl-data-platform-dbt:latest',
                    command='dbt run',
                    auto_remove=True,
                    docker_url='unix://var/run/docker.sock',
                    network_mode='fpl-data-platform_default',
                    environment=env_variables
            )

            transform_task.execute(context=context)

    test_dbt = DockerOperator(
        task_id='test_dbt',
        image='fpl-data-platform-dbt:latest',
        command='dbt test',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='fpl-data-platform_default',
        environment=env_variables
    )

    load_vaastav >> load_understat >> seed_dbt >> list_seasons >> backfill_load_and_transform() >> test_dbt