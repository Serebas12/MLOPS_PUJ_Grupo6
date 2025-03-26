from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime
import os
import time
import requests
import json
import pandas as pd
import numpy as np # se carga pensandolo como dependencia
import pickle
import mlflow
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# Configuración del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 22),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    #'retry_delay': timedelta(minutes=2),
}

# URL del API que quieres consumir
#API_URL = "http://10.43.101.108:80/data?group_number=6"
API_URL = "http://host.docker.internal:80/data?group_number=6"
# Tiempo de espera para la lectura de datos
MIN_UPDATE_TIME = 60 

# Paso 1: Creación de la tabla
def create_table():
    # Conectar a MySQL usando el hook configurado en Airflow
    mysql_hook = MySqlHook(mysql_conn_id = 'mysql_default')
    
    # Consulta para crear la tabla si no existe
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS covertype_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Elevation INT,
        Aspect INT,
        Slope INT,
        Horizontal_Distance_To_Hydrology INT,
        Vertical_Distance_To_Hydrology INT,
        Horizontal_Distance_To_Roadways INT,
        Hillshade_9am INT,
        Hillshade_Noon INT,
        Hillshade_3pm INT,
        Horizontal_Distance_To_Fire_Points INT,
        Wilderness_Area VARCHAR(15),
        Soil_Type VARCHAR(15),
        Cover_Type INT
    );
    """
    mysql_hook.run(create_table_sql)

    print("Tabla 'covertype' creada (si no existía).")


def load_api_data(**kwargs):
    for i in range(10):
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()['data']
            mysql_hook = MySqlHook(mysql_conn_id = 'mysql_default')
            mysql_hook.insert_rows(
                table = 'covertype_data',
                rows = data,
                target_fields = [
                    'Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology', 
                    'Vertical_Distance_To_Hydrology', 'Horizontal_Distance_To_Roadways', 
                    'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm', 
                    'Horizontal_Distance_To_Fire_Points', 'Wilderness_Area', 
                    'Soil_Type', 'Cover_Type'
                ],
                commit_every = 1000
            )
            print(f"Batch {response.json()['batch_number']} cargado exitosamente")
            time.sleep(MIN_UPDATE_TIME)

        elif response.status_code == 400:
            raise Exception(f"Sin datos disponibles. Código {response.status_code}")
    

def train_model():
    time.sleep(60)
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    query = "SELECT * FROM covertype_data;"
    df = mysql_hook.get_pandas_df(query)
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # Separar X e y
    X = df.drop(columns=["Cover_Type"])
    y = df["Cover_Type"]

    # Definir columnas categóricas y numéricas
    categorical_cols = ["Wilderness_Area", "Soil_Type"]
    minmax_cols = ["Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm", "Aspect"]
    all_num_cols = [col for col in X.columns if col not in categorical_cols]
    standard_cols = [col for col in all_num_cols if col not in minmax_cols]

    # Preprocesamiento combinado
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("minmax", MinMaxScaler(), minmax_cols),
            ("standard", StandardScaler(), standard_cols)
        ]
    )

    # Definir pipeline y búsqueda de hiperparámetros
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(random_state=42))
    ])

    param_grid = {
        "classifier__n_estimators": [10, 50, 80],
        "classifier__max_depth": [5, 8, 12],
        "classifier__min_samples_split": [2, 5, 10]
    }

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=3,
        scoring="accuracy",
        n_jobs=-1,
        verbose=2
    )

    # Separación de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Configurar MLflow y MinIO
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("covertype_training_experiment")

    # Entrenamiento con tracking de MLflow
    mlflow.sklearn.autolog(log_model_signatures=True, log_input_examples=True, registered_model_name="modelo_covertype_vf", max_tuning_runs=27)

    with mlflow.start_run(run_name="autolog_pipe_model_reg") as run:
        grid_search.fit(X_train, y_train)

with DAG(
    dag_id="DAG_p2",
    default_args = default_args,
    schedule_interval = "@once",  # 
    catchup = False,
    description = "DAG de consumo de datos por API y entrenamiento de modelo",
) as dag:

    t1 = PythonOperator(
        task_id = "crear_tabla",
        python_callable = create_table,
        provide_context = True,
    )

    t2 = PythonOperator(
        task_id = "consumir_datos_api",
        python_callable = load_api_data,
        provide_context = True,
    )

    t3 = PythonOperator(
        task_id = "modelar_datos",
        python_callable = train_model,
        provide_context = True,
    )

    t1 >> t2 >> t3