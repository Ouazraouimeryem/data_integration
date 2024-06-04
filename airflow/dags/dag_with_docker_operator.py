from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator

import requests
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 6, 1),
    'retry_delay': timedelta(minutes=10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

def check_send_status(**kwargs):
    try:
        response = requests.get('http://flask:5000/check_send_status')  # Replace container_ip with your container's IP
        response.raise_for_status()  
        if response.text:
            response_json = response.json()
            if response_json.get("status") != "success":
                raise ValueError(f"Request returned non-success status: {response_json.get('status')}")
            return response_json
        else:
            return {"status": "No content"}
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions (e.g., connection errors)
        return {"status": "Request failed", "error": str(e)}


with DAG(
    dag_id='dag_with_docker_operator',
    default_args=default_args,
    description='Run command inside Docker container in Airflow',
    schedule_interval=timedelta(minutes=1)
) as dag:
    
    execute_get_command_task = DockerOperator(
        task_id='execute_get_command_inside_docker',
        docker_url="unix://var/run/docker.sock",
        api_version='auto',
        auto_remove=True,
        image='composer-flask:latest',  # Replace with your Docker image and tag
        command='curl -X GET http://host.docker.internal/check_send_status',  # Replace container_ip with your container's IP
        
    )

    check_status_task = PythonOperator(
        task_id='check_status',
        python_callable=check_send_status,
    )

    execute_get_command_task >> check_status_task
