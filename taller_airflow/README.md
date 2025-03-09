primero se debem rear los directorios requeridos por airflow, lo cual se realiza con: 

mkdir dags, logs, plugins

segundo se crea archivo .env crear archivo on UID
"AIRFLOW_UID=50000" | Out-File .env -Encoding ascii


ejecutar docker 
docker compose up airflow-init
docker-compose up


ahora se crea conexión ea mysql en airflow
