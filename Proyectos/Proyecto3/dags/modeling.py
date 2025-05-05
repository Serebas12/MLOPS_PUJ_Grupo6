import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import numpy as np
import boto3
from botocore.client import Config
import mlflow
import mlflow.sklearn
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Hiperparámetros para RandomizedSearchCV
param_grid = {
    "classifier__n_estimators": [10, 50],
    "classifier__max_depth": [5, 12],
    "classifier__min_samples_split": [2, 10]
}

# Número de características a seleccionar con SelectKBest
K_BEST = 20

# DAG definition defaults
default_args = {
    'start_date': datetime(2025, 4, 29),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

def train_and_register():
    # —————— 0) Configurar S3 / MinIO ——————
    S3_ENDPOINT = "http://localhost:9000"
    S3_BUCKET   = "mlflows3"
    AWS_KEY     = "admin"
    AWS_SECRET  = "supersecret"

    os.environ['AWS_ACCESS_KEY_ID']      = AWS_KEY
    os.environ['AWS_SECRET_ACCESS_KEY']  = AWS_SECRET
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = S3_ENDPOINT

    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        config=Config(signature_version='s3v4', s3={'addressing_style':'path'})
    )
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except Exception:
        s3.create_bucket(Bucket=S3_BUCKET)
    # ————————————————————————————————

    # 1) Cargar datos limpios
    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_conn()
    df = pd.read_sql(
        "SELECT * FROM clean_data.diabetes_clean WHERE split in ('train','valid','test')",
        con=conn
    )
    conn.close()

    # 2) Separar splits
    df_train = df[df['split'] == 'train']
    df_valid = df[df['split'] == 'valid']
    df_test  = df[df['split'] == 'test']

    # 3) Definir X/y
    drop_cols = ['encounter_id', 'readmitted', 'split', 'load_date', 'processed_date']
    X_train, y_train = df_train.drop(columns=drop_cols), df_train['readmitted']
    X_valid, y_valid = df_valid.drop(columns=drop_cols), df_valid['readmitted']
    X_test,  y_test  = df_test.drop(columns=drop_cols),  df_test['readmitted']

    # 4) Columnas numéricas y categóricas
    num_cols = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = X_train.select_dtypes(include=['object']).columns.tolist()

    # 5) Preprocesamiento
    num_proc = Pipeline([
        ('impute', SimpleImputer(strategy='median')),
        ('scale', StandardScaler())
    ])
    cat_proc = Pipeline([
        ('impute', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=True))
    ])
    preprocessor = ColumnTransformer([
        ('num', num_proc, num_cols),
        ('cat', cat_proc, cat_cols),
    ])

    # 6) Pipeline con SelectKBest y RandomForest
    selector = SelectKBest(score_func=f_classif, k=K_BEST)
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('selector', selector),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    # 7) RandomizedSearchCV: combinar train + valid para búsqueda
    grid_search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_grid,
        n_iter=10,
        cv=2,
        scoring="accuracy",
        n_jobs=1,
        verbose=2,
        random_state=42  ## si queremos hiperparámetros más aleatorios comentamos esta entrada
    )
    X_grid = pd.concat([X_train, X_valid])
    y_grid = pd.concat([y_train, y_valid])

    # —————— 8) Registrar todas las pruebas con autolog ——————
    mlflow.set_tracking_uri('http://localhost:5000')
    mlflow.set_experiment('Diabetes_Readmission_Exp')
    with mlflow.start_run(run_name="random_search", nested=False):
        mlflow.sklearn.autolog()
        grid_search.fit(X_grid, y_grid)
    # ——————————————————————————————————————————————

    # 9) Extraer el mejor modelo y sus métricas
    best_model  = grid_search.best_estimator_
    best_params = grid_search.best_params_
    preds       = best_model.predict(X_test)
    proba       = best_model.predict_proba(X_test)
    metrics = {
        'test_accuracy' : accuracy_score(y_test, preds),
        'test_precision': precision_score(y_test, preds, average='weighted'),
        'test_recall'   : recall_score(y_test, preds, average='weighted'),
        'test_f1'       : f1_score(y_test, preds, average='weighted'),
        'test_auc'      : roc_auc_score(y_test, proba, multi_class='ovr', average='weighted')
    }

    # 10) Registrar y promover sólo el mejor modelo
    with mlflow.start_run(run_name="register_best", nested=False):
        mlflow.log_params(best_params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(best_model, artifact_path='model')
        run_id    = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"
        mv = mlflow.register_model(model_uri, 'DiabetesReadmissionModel')

    client = mlflow.tracking.MlflowClient()
    client.transition_model_version_stage(
        name='DiabetesReadmissionModel',
        version=mv.version,
        stage='Production',
        archive_existing_versions=True
    )

with DAG(
    'model_training_pipeline',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False,
    tags=['training'],
) as dag:

    train_task = PythonOperator(
        task_id='train_and_register',
        python_callable=train_and_register
    )

    train_task
