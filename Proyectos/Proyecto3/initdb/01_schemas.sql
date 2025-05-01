-- 01_create_airflow.sql
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;

-- 02_create_mlflow.sql
CREATE USER mlflow WITH PASSWORD 'supersecret';
CREATE DATABASE mlflow OWNER mlflow;

-- Crea el esquema raw_data si no existe
CREATE SCHEMA IF NOT EXISTS raw_data;

--  creción del esquema clean_data
CREATE SCHEMA IF NOT EXISTS clean_data;

