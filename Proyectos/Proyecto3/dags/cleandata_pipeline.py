from datetime import datetime, timedelta, date
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import numpy as np
from psycopg2.extras import execute_values


# Configuración del DAG
default_args = {
    'start_date': datetime(2025, 4, 29),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Función de limpieza y upsert incremental
def clean_and_upsert():
    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_conn()  # DBAPI2 connection
    cursor = conn.cursor()

    # Leer última fecha procesada
    control_sql = 'SELECT MAX(processed_date) AS last_date FROM clean_data.pipeline_control'
    control_df = pd.read_sql(control_sql, con=conn)
    last_date = control_df.at[0, 'last_date']
    if pd.isna(last_date):
        last_date = date(1900, 1, 1)

    # Leer nuevos registros raw
    sql_raw = f"""
        SELECT *
        FROM raw_data.diabetes_raw
        WHERE load_date > '{last_date}'::date
    """
    df = pd.read_sql(sql_raw, con=conn)
    if df.empty:
        cursor.close()
        conn.close()
        return

    # Limpieza de variable objetivo
    df['readmitted'] = df['readmitted'].fillna('NonMeasured')
    df['readmitted'] = (
        df['readmitted']
          .replace({'>30': 'more30', '<30': 'less30'})
          .str.replace(r'[^\w]', '', regex=True)
    )

    # listas de columnas categóricas y remplazos
    feature_cat_cols = [
        'race', 'gender', 'age', 'weight', 'admission_type_id', 'discharge_disposition_id',
        'admission_source_id', 'payer_code', 'medical_specialty', 'diag_1', 'diag_2', 'diag_3',
        'max_glu_serum', 'A1Cresult', 'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide',
        'glimepiride', 'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone',
        'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide', 'examide', 'citoglipton',
        'insulin', 'glyburide_metformin', 'glipizide_metformin', 'glimepiride_pioglitazone',
        'metformin_rosiglitazone', 'metformin_pioglitazone', 'change', 'diabetesMed'
        #'readmitted', 'split'
    ]
    for col in feature_cat_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                      .str.replace(r'[^\w\s]', '', regex=True)
                      .replace({'': 'NonInfo'})
            )

    # Reemplazos específicos
    df['max_glu_serum'] = df['max_glu_serum'].fillna('NonMeasured')
    df['a1cresult'] = df['a1cresult'].fillna('NonMeasured')
    for col in ['weight', 'race', 'payer_code', 'medical_specialty', 'diag_1', 'diag_2', 'diag_3']:
        if col in df.columns:
            df[col] = df[col].replace('?', 'NonInfo')

    # Split producción
    df['split'] = df['split'].fillna('oot')
    df['processed_date'] = date.today()

    # Bulk upsert
    cols = list(df.columns)
    cols_str = ','.join(cols)
    update_cols = [c for c in cols if c != 'encounter_id']
    update_str = ','.join([f"{c}=EXCLUDED.{c}" for c in update_cols])
    insert_sql = (
        f"INSERT INTO clean_data.diabetes_clean ({cols_str}) VALUES %s "
        f"ON CONFLICT (encounter_id) DO UPDATE SET {update_str};"
    )
    values = [tuple(r) for r in df[cols].itertuples(index=False, name=None)]
    execute_values(cursor, insert_sql, values, page_size=1000)
    conn.commit()
    cursor.close()
    conn.close()


with DAG(
    'clean_data_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['clean'],
) as dag:
    
    # 1) Asegurar esquema y tabla clean_data.diabetes_clean
    create_schema = PostgresOperator(
        task_id='create_clean_schema',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE SCHEMA IF NOT EXISTS clean_data;
        CREATE TABLE IF NOT EXISTS clean_data.diabetes_clean (
            encounter_id                TEXT PRIMARY KEY,
            patient_nbr                 TEXT,
            race                        TEXT,
            gender                      TEXT,
            age                         TEXT,
            weight                      TEXT,
            admission_type_id           TEXT,
            discharge_disposition_id    TEXT,
            admission_source_id         TEXT,
            time_in_hospital            INTEGER,
            payer_code                  TEXT,
            medical_specialty           TEXT,
            num_lab_procedures          INTEGER,
            num_procedures              INTEGER,
            num_medications             INTEGER,
            number_outpatient           INTEGER,
            number_emergency            INTEGER,
            number_inpatient            INTEGER,
            diag_1                      TEXT,
            diag_2                      TEXT,
            diag_3                      TEXT,
            number_diagnoses            INTEGER,
            max_glu_serum               TEXT,
            A1Cresult                   TEXT,
            metformin                   TEXT,
            repaglinide                 TEXT,
            nateglinide                 TEXT,
            chlorpropamide              TEXT,
            glimepiride                 TEXT,
            acetohexamide               TEXT,
            glipizide                   TEXT,
            glyburide                   TEXT,
            tolbutamide                 TEXT,
            pioglitazone                TEXT,
            rosiglitazone               TEXT,
            acarbose                    TEXT,
            miglitol                    TEXT,
            troglitazone                TEXT,
            tolazamide                  TEXT,
            examide                     TEXT,
            citoglipton                 TEXT,
            insulin                     TEXT,
            glyburide_metformin         TEXT,
            glipizide_metformin         TEXT,
            glimepiride_pioglitazone    TEXT,
            metformin_rosiglitazone     TEXT,
            metformin_pioglitazone      TEXT,
            change                      TEXT,
            diabetesMed                 TEXT,
            readmitted                  TEXT,
            split                       TEXT,
            load_date                   DATE,
            processed_date              DATE
            );
        """
    )

    # 2) Reconstruir control de pipeline
    delete_control = PostgresOperator(
        task_id='delete_old_control',
        postgres_conn_id='postgres_default',
        sql="""
        DROP TABLE IF EXISTS clean_data.pipeline_control;
        CREATE TABLE clean_data.pipeline_control (processed_date DATE);
        """
    )

    # 3) Limpieza y upsert incremental
    clean_task = PythonOperator(
        task_id='clean_and_upsert',
        python_callable=clean_and_upsert,
    )

    # 4) Actualizar control de pipeline
    update_control = PostgresOperator(
        task_id='update_control',
        postgres_conn_id='postgres_default',
        sql="INSERT INTO clean_data.pipeline_control (processed_date) VALUES (CURRENT_DATE);"
    )

    # Definir dependencias
    create_schema >> delete_control >> clean_task >> update_control
