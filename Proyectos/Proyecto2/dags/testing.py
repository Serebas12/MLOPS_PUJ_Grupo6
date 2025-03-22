from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import mlflow
import pickle

def log_mlflow():
    mlflow.set_tracking_uri("http://mlflow:5000")  # Nombre del servicio del docker-compose
    mlflow.set_experiment("desde_airflow")
    data = {"mensaje": "esto es una prueba"}
    with open("output.pkl", "wb") as f:
        pickle.dump(data, f)
    with mlflow.start_run():
        mlflow.log_param("batch_size", 32)
        mlflow.log_metric("loss", 0.15)
        mlflow.log_artifact("output.pkl")

with DAG(
    dag_id="mlflow_test_dag",
    start_date=datetime(2025, 3, 21),
    schedule_interval=None,
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id="log_mlflow_run",
        python_callable=log_mlflow
    )

    t1
