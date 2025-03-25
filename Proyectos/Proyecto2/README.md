
la fuente de datos desde la local
docker compose -f docker-compose-external.yaml up --build -d 
docker compose -f docker-compose-external.yaml down -v --rmi all 
revisar que existe expuesto el servicio en el localhost
curl http://localhost/
revisión de la recolección de los datos
curl "http://localhost/data?group_number=6"
el código está modificado para entregar datos cada minuto 
el propio código avisa cuando ya se encuentra todo el conjunto de datos consumido



primer servicio desplegado por el docker compose es airflow, que es el de codificación más extensa 
despliegue completo 
sudo 
docker compose -f docker-compose-p2.yaml up airflow-init 
sudo 
docker compose -f docker-compose-p2.yaml up --build -d 
destrucción del proyecto para actualizarlo
sudo 
docker compose -f docker-compose-p2.yaml down -v --rmi all 

entrar a airflow 
http://localhost:8080
clave de acceso airflow
user: airflow
password: airflow
posgres: airflow

entrar a mlflow
http://localhost:5000
clave de acceso mlflow
user: mlflow
password: mlflow

entrar a minio
http://localhost:9001
clave minio
user: admin
password: supersecret

entrar a fastapi
http://localhost:8989


Para verificar que todo se encuentra en línea, con el comando de abajo revisamos que todos los servicios solicitados tengan puerto activo y sea el que se le asigno 
docker ps -a
en caso de algún error o conflicto se usa 
docker logs <mombre del contenedor>

entramos a los servicios por medio de sus puertos asignados en el localhost, y nos logueamos si es necesario

dentro de los logs de mlflow debemos verificar que dentro del proceso de conexión con mysql se encuentre 

INFO [alembic.runtime.migration] Context impl MySQLImpl.
INFO [alembic.runtime.migration] Running upgrade  -> ... (el número acá es un hash2 asignado por la conexión con mysql)

Importante considerar que pueden haber errores al principio de los logs entre la conexión de mlflow y mysql, pero más adelante se debe evidenciar los logs mencionados

luego entramos a minio y creamos el bucket mlflows3

entramos a airflow y verificamos la existencia del DAG, luego corremos el DAG y verificamos que se vea reflejado en mlflow el experimento, este .py también permite ver una prueba de conectividad, al guardar un artefacto en minio, por lo tanto en minio se puede verificar la conexión.

Para corroborar la correcta conexión a api toca tener ya resultados por lo tanto se necesita empezar a crear el DAG para el pipeline del modelo a colocar en producción

para iniciar con el proceso, dentro de la interfaz de airflow, creamos la conexión a la base de datos con los siguientes datos

connection id: mysql_default
connection type: mysql
description: Almacenamiento de los datos obtenidos desde la api
host: mysql-data-store
schema: datadb
login: admin
password: supersecret
port: 3306


luego se entra a minio y se crea el bucket **mlflows3**

regresamos a airflow y damos correr a DAG_p2 


from datetime import datetime
import requests
import json
import os
API_URL = "http://host.docker.internal:80/data?group_number=6"
response = requests.get(API_URL)
print(response.status_code)

docker exec -it mysql-data-store bash
mysql -u root -proot
use datadb;
select count(1) from covertype_data;








