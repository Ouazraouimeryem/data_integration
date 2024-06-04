from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import docker
import logging

def is_container_running(container_name):
    client = docker.from_env()
    containers = client.containers.list(filters={'name': container_name})
    return len(containers) > 0

def monitor_container(container_name):
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        if is_container_running(container_name):
            logging.info(f"Container {container_name} is running.")
        else:
            logging.info(f"Container {container_name} is not running.")
            container.restart()
    except Exception as e:
        logging.error(f"Error monitoring container {container_name}: {str(e)}")
        raise

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 30),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'container_monitoring',
    default_args=default_args,
    description='Monitor container status',
    schedule_interval=timedelta(minutes=30),  # Adjust as needed
)

container_names = [
    "composer-zookeeper-1",
    "composer-kafka-1",
    "composer-flask-1",
    "composer-mysql-1",
    
]

# Define tasks for monitoring each container
tasks = []
for container_name in container_names:
    task = PythonOperator(
        task_id=f'monitor_{container_name}',
        python_callable=monitor_container,
        op_args=[container_name],
        dag=dag,
    )
    tasks.append(task)

# Set task dependencies
for i in range(1, len(tasks)):
    tasks[i] 

