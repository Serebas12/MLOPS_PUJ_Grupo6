from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import numpy as np
from psycopg2.extras import execute_values

CSV_PATH   = "/data/Diabetes.csv"
BATCH_SIZE = 15000
SEED       = 42

default_args = {
    "start_date": datetime(2025, 4, 28),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="raw_data_initial_batch_load",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
    tags=["raw","batch","initial"],
) as dag:

    create_schema = PostgresOperator(
        task_id="create_raw_schema",
        postgres_conn_id="postgres_default",
        sql="CREATE SCHEMA IF NOT EXISTS raw_data;"
    )

    create_table = PostgresOperator(
        task_id="create_raw_table",
        postgres_conn_id="postgres_default",
        sql="""
        CREATE TABLE IF NOT EXISTS raw_data.diabetes_raw (
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
            load_date                   DATE
        );
        """
    )

    def load_in_batches():
        hook = PostgresHook(postgres_conn_id="postgres_default")
        conn = hook.get_conn()
        cursor = conn.cursor()

        rng = np.random.RandomState(SEED)
        today = datetime.utcnow().date()

        for chunk in pd.read_csv(CSV_PATH, chunksize=BATCH_SIZE):
            # renombra guiones a guiones bajos
            chunk.rename(columns=lambda x: x.replace("-", "_"), inplace=True)
            chunk["load_date"] = today
            rand = rng.rand(len(chunk))
            chunk["split"] = np.where(rand < 0.6, "train",
                               np.where(rand < 0.8, "valid", "test"))

            cols   = list(chunk.columns)
            sql    = f"INSERT INTO raw_data.diabetes_raw ({','.join(cols)}) VALUES %s"
            values = [tuple(r) for r in chunk[cols].itertuples(index=False, name=None)]

            execute_values(cursor, sql, values, page_size=1000)
            conn.commit()

        cursor.close()
        conn.close()

    load_data = PythonOperator(
        task_id="load_csv_in_batches",
        python_callable=load_in_batches,
    )

    create_schema >> create_table >> load_data
