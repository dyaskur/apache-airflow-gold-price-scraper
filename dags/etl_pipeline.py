from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import json
from datetime import datetime

# Define default DAG arguments
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 2, 1),
    "retries": 1,
}

# Function to extract data from API
def extract_data():
    url = "https://jsonplaceholder.typicode.com/todos/"
    response = requests.get(url)
    todos = response.json()
    with open("/tmp/todos.json", "w") as f:
        json.dump(todos, f)

# Function to transform data (filter completed tasks)
def transform_data():
    with open("/tmp/todos.json", "r") as f:
        todos = json.load(f)
    completed_tasks = [todo for todo in todos if todo["completed"]]
    with open("/tmp/completed_todos.json", "w") as f:
        json.dump(completed_tasks, f)

# Function to load data into PostgreSQL
def load_data():
    hook = PostgresHook(postgres_conn_id="postgres_warehouse")
    with open("/tmp/completed_todos.json", "r") as f:
        completed_todos = json.load(f)
    for todo in completed_todos:
        hook.run("INSERT INTO todos (id, userId, title, completed) VALUES (%s, %s, %s, %s)",
                 parameters=(todo["id"], todo["userId"], todo["title"], todo["completed"]))

# Define the DAG
with DAG(
    "etl_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data
    )

    # Set task dependencies
    extract_task >> transform_task >> load_task
