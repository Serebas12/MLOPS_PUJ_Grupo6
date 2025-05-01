Iniciamos la red host para la comunicación de airflow con los demás servicios 

```bash
docker network create airflow_backend
```

Iniciamos con el proceso arrancando el todos los servicios en docker compose con los servicios generales (airflow por seperado) usando 

```bash 
sudo docker compose -f docker-compose-resto.yaml up --build -d
```

```bash
sudo docker compose -f docker-compose-resto.yaml down --rmi all -v
```

revisamos la exposición de los servicios entrando a sus puertos en el localhost 

(tomar encuenta, estamos usando el mismo puerto que se usa dentro de docker como en el localhost, esto nos puede facilitar el proceso de conexiones más adelante)

```bash 
http://localhost:8989       fastapi
http://localhost:8501       streamlit
http://localhost:3000       grafana
http://localhost:5000       mlflow
http://localhost:9090       promehteus
http://localhost:9001       minio
```

Se levanta airflow con 
```bash
sudo docker compose -f docker-compose-airflow.yaml up airflow-init
sudo docker compose -f docker-compose-airflow.yaml up --build -d
```

```bash
sudo docker compose -f docker-compose-airflow.yaml down --rmi all -v
```

```bash 
http://localhost:8080
```


docker compose -f docker-compose-airflow.yaml exec airflow-scheduler ls -l /opt/airflow/dags


```bash 
sudo docker compose -f docker-compose-jupyter.yaml up --build -d
```

```bash
sudo docker compose -f docker-compose-jupyter.yaml down --rmi all -v
```

```bash
http://localhost:8888       jupyter
```


el primer dag en correr por única vez es raw_data_initial_batch_load, este DAG realiza la primer carga de los datos en la tabla de la rawdata, con este procedimiento garantizamos que se carga los datos a la rawdata y esperamos a que termine, sólo se necesita correr una primera vez

Luego seguimos con el DAG clean_data_pipeline, el cual se encarga de hacer la carga de datos de la rawdata, hace la limpieza de los mismos y los carga, es importante sólo encenderlo después de que finalice raw_data_initial_batch_load, así garantizamos que el flujo de consumo de datos quede activo, adicional, tenemos las columnas load_date y processed_date que son las columnas que nos permiten hacer seguimiento de la carga y flujo de datos en las cargas de datos


docker exec -it proyecto3-postgres-1 bash
psql -U airflow -d airflow
psql -U admin -d supersecret
\dn
\dt raw_data.*
SELECT COUNT(*) FROM raw_data.diabetes_raw;
DROP TABLE raw_data.diabetes_raw;
SELECT COUNT(*) FROM raw_data.diabetes_clean;
DROP TABLE raw_data.diabetes_clean;


Luego entramos a minio, y acá creamos el bucket `mlflows3` para que se guarden los objetos del proceso de entrenamiento de modelos del experimento





Usando jupyter podemos examinar los datos cargados dentro del esquema, donde verificamos en los descriptivos la información junto con la documentación de la misma, así mismo, podemos darnos cuenta que el conjunto de datos está supremamente bien documentado, por lo tanto, consideramos que sólo es necesario hacer el trabajo para corregir los carácteres especiales, o valores "faltantes" que nos permita hacer una adecuación del conjunto de datos y cargarlos en el clean data 
https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008



Notas

para disminuir el consumo de contenedor al mínimo posible para poderlo desplegar en las máquinas, usaremos un solo postgres

levantamos streamlit dentro de un contenedor considerando que este paso es fácil de hacer para continuar con la conterinización de los servicios a usar 

