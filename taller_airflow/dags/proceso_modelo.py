from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime
import os
import pandas as pd
import numpy as np # se carga pensandolo como dependencia
import pickle
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Paso 0: Limpieza de la base de datos
# Limpiamos el esquema que vamos 
def empty_schema():
    # Conectar a MySQL usando el hook configurado en Airflow
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')

    # Limpieza del schema de la base de datos
    # siempre tomar en cuenta al esquema que apuntamos y conectado dentro de airflow
    limpiar_schema = """
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
    """
    mysql_hook.run(limpiar_schema)

    print("Limpieza del esquema realizado.")


# Paso 1: Creación de la tabla
def create_or_clear_table():
    # Conectar a MySQL usando el hook configurado en Airflow
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    
    # Consulta para crear la tabla si no existe
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS penguins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        species VARCHAR(100),
        island VARCHAR(100),
        culmen_length_mm FLOAT(10,2),
        culmen_depth_mm FLOAT(10,2),
        flipper_length_mm INT,
        body_mass_g INT,
        sex VARCHAR(100)
    );
    """
    mysql_hook.run(create_table_sql)
    
    # Si la tabla ya existe, se eliminan todos los registros
    clear_table_sql = "TRUNCATE TABLE penguins;"
    mysql_hook.run(clear_table_sql)
    
    print("Tabla 'penguins' creada (si no existía) y vaciada.")

# Paso 2: Guardado de información de la tabla 
def load_csv_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'penguins_size.csv')
    # Lee el CSV utilizando pandas
    df = pd.read_csv(csv_path)
    # Prepara los datos para la inserción: convertimos cada valor NaN a None
    rows = [
        tuple(x if pd.notna(x) else None for x in row)
        for row in df[['species', 'island', 'culmen_length_mm', 'culmen_depth_mm', 
                       'flipper_length_mm', 'body_mass_g', 'sex']].itertuples(index=False, name=None)
    ]
    
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    
    # Inserta las filas en la tabla 'penguins'
    mysql_hook.insert_rows(
        table='penguins',
        rows=rows,
        target_fields=['species', 'island', 'culmen_length_mm', 'culmen_depth_mm',
                       'flipper_length_mm', 'body_mass_g', 'sex'],
        commit_every=1000
    )
    
    print("Datos del CSV cargados en la tabla 'penguins'.")


# Paso 3: Entrenamiento del modelo
def train_model():
    # Conectar a MySQL y obtener la tabla en un DataFrame
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    query = "SELECT * FROM penguins;"
    df = mysql_hook.get_pandas_df(query)
    
    # Eliminar la columna 'id' ya que es autogenerada
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    
    # Asegurarse de que no existan filas sin la variable target
    df = df.dropna(subset=['species'])
    
    # Separar variables predictoras (X) y la variable objetivo (y)
    X = df.drop(columns=["species"])
    y = df["species"]
    
    # Definir las columnas de tipo texto y numéricas
    text_cols = ["island", "sex"]
    num_cols = ["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"]
    
    # Dividir los datos en conjunto de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Definir el preprocesador: codificación one-hot para variables categóricas y escalado para numéricas
    preprocessor = ColumnTransformer(
        transformers=[
            ("text", OneHotEncoder(handle_unknown="ignore"), text_cols),
            ("num", StandardScaler(), num_cols)
        ]
    )
    
    # Definir el pipeline del modelo: preprocesamiento + clasificador RandomForest
    modelRF = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=10, random_state=42))
    ])
    
    # Entrenar el modelo
    modelRF.fit(X_train, y_train)
    
    # Evaluar el modelo
    y_pred = modelRF.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Precisión Modelo RF:", accuracy)
    
    # Guardar el modelo entrenado en un archivo .pkl
    model_path = os.path.join(os.path.dirname(__file__), "modeloRF.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(modelRF, f)

    print("Modelo guardado en", model_path)


# Configuración del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 5),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    #'retry_delay': timedelta(minutes=2),
}

with DAG(
        dag_id='modelo_penguin',
        description="Pipeline entrenamiento modelo Pinguins",
        schedule_interval="@daily",
        default_args=default_args,
        catchup=False
    )  as dag:

    t0 = PythonOperator(
        task_id='limpiar_base_de_datos',
        python_callable=empty_schema
    )

    t1 = PythonOperator(
        task_id='creacion_tabla',
        python_callable=create_or_clear_table
    )

    t2 = PythonOperator(
        task_id='carga_informacion_inicial',
        python_callable=load_csv_data 
    )

    t3 = PythonOperator(
        task_id='entrenar_modelo',
        python_callable=train_model
    )

    t0 >> t1 >> t2 >> t3