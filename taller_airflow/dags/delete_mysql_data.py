#   Importar los objetos necesarios para que funcione el DAG
from airflow import DAG     
from airflow.providers.mysql.operators.mysql import MySqlOperator
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
    'delete_mysql_data',
    default_args=default_args,
    description='Un DAG para borrar el contenido de la base de datos',
    schedule_interval='@daily',  # Se ejecutará todos los días
    catchup=False
)

# Definir la consulta SQL
delete_task = MySqlOperator(
    task_id='delete_data',
    mysql_conn_id='mysql_default',  # Nombre de la conexión en Airflow
    sql="""
    SET FOREIGN_KEY_CHECKS = 0;

    SELECT IFNULL(
        GROUP_CONCAT('DROP TABLE ', table_name SEPARATOR '; '),
        'SELECT 1'
    ) INTO @drop_stmt
    FROM information_schema.tables
    WHERE table_schema = 'mydatabase';

    PREPARE stmt FROM @drop_stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET FOREIGN_KEY_CHECKS = 1;
    """, # Borra las tablas dentro de la base de datos
    dag=dag,
)

delete_task  # Ejecuta la tarea
