#!/bin/bash
# Cambia al directorio deseado. Asegúrate de que este directorio exista.
cd /home/estudiante/Documents/MLOPS_PUJ_Grupo6/taller_mlflow/mlflow || {
  echo "El directorio no existe"
  exit 1
}
# Ejecuta MLflow con la configuración deseada.
exec /usr/bin/python3 -m mlflow server \
  --backend-store-uri postgresql://mlflow_user:mlflow_password@127.0.0.1:5432/mlflow_db \
  --default-artifact-root s3://mlflows3/artifacts \
  --host 0.0.0.0 \
  --port 5000 \
  --serve-artifacts
