import pandas as pd
import pymysql
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta

# Configuración del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 5),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'load_csv_to_mysql',
    default_args=default_args,
    description='Carga datos de penguins_size.csv a MySQL después de borrar las tablas',
    schedule_interval='@daily',
    catchup=False
)

# Sensor para esperar a que `drop_mysql_tables` termine
wait_for_delete_data = ExternalTaskSensor(
    task_id='wait_for_delete_data',
    external_dag_id='delete_data',  # DAG que borra las tablas
    external_task_id='delete_task',  # Espera a que todo el DAG termine
    mode='poke',
    poke_interval=60,
    timeout=600,
    dag=dag,
)

# Función para crear la tabla y cargar datos desde el CSV
def load_csv_to_mysql():
    # Ruta del archivo CSV en la carpeta DAGs
    file_path = "/opt/airflow/dags/penguins_size.csv"
    
    # Leer el archivo CSV
    df = pd.read_csv(file_path)

    # Conectar a MySQL
    connection = pymysql.connect(
        host="mysql",
        user="mysqluser",
        password="airflow",
        database="mydatabase"
    )
    cursor = connection.cursor()

    # Crear la tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS penguins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            species VARCHAR(25),
            island VARCHAR(25),
            culmen_length_mm INT,
            culmen_depth_mm INT, 
            flipper_length_mm INT,
            body_mass_g INT, 
            sex VARCHAR(25)
        )
    """)

    # Insertar datos en la tabla
    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO penguins (
                species, island, culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g, sex
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row["species"], row["island"], row["culmen_length_mm"], row["culmen_depth_mm"],
                row["flipper_length_mm"], row["body_mass_g"], row["sex"]
            )
        )

    # Confirmar cambios y cerrar conexión
    connection.commit()
    cursor.close()
    connection.close()
    print("Datos insertados correctamente.")

# Tarea en Airflow para cargar el CSV después de que las tablas hayan sido eliminadas
load_csv_task = PythonOperator(
    task_id='load_csv_task',
    python_callable=load_csv_to_mysql,
    dag=dag,
)

# Establecer la dependencia: Primero debe ejecutarse `drop_mysql_tables`
wait_for_delete_data >> load_csv_task
