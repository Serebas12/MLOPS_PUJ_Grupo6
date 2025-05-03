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

docker exec -it mlflow bash
touch test_s3.py
echo "import os, mlflow
os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://minio:9000'
mlflow.set_tracking_uri('http://mlflow:5000')
with mlflow.start_run():
    with open('/tmp/hello.txt','w') as f: f.write('hola')
    mlflow.log_artifact('/tmp/hello.txt')
    print('Artifact URI:', mlflow.get_artifact_uri())
    print('✅ Artifact logged')
" > test_s3.py
python test_s3.py





Usando jupyter podemos examinar los datos cargados dentro del esquema, donde verificamos en los descriptivos la información junto con la documentación de la misma, así mismo, podemos darnos cuenta que el conjunto de datos está supremamente bien documentado, por lo tanto, consideramos que sólo es necesario hacer el trabajo para corregir los carácteres especiales, o valores "faltantes" que nos permita hacer una adecuación del conjunto de datos y cargarlos en el clean data 
https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008



Notas

para disminuir el consumo de contenedor al mínimo posible para poderlo desplegar en las máquinas, usaremos un solo postgres

levantamos streamlit dentro de un contenedor considerando que este paso es fácil de hacer para continuar con la conterinización de los servicios a usar 

Despliegue del docker compose 

docker compose -f docker-compose-resto.yaml up --build -d






Antes de desplegar el kubernete: 

1. Construccion de imagenes y carga en docker hub, dado que kubernete no permite la construcción de imagenes 

docker build -t sebs1996/fastapi-mlops-p3:latest ./app
docker push sebs1996/fastapi-mlops-p3:latest

docker build -t sebs1996/mlflow-mlops-p3:latest ./mlflow
docker push sebs1996/mlflow-mlops-p3:latest

docker build -t sebs1996/jupyter-mlops-p3:latest ./jupyter
docker push sebs1996/jupyter-mlops-p3:latest
 
 
Se ejecuta el kompose pero se debe cambiar lo siguiente

1. Cambiar puertos para garantizar que estos sean estaticos 

2. configuración de volumenes para que puedan ser tomados por el kubernete, caso especial el archivo de prometheus.yaml 

- se debe crear el configmap 
kubectl create configmap prometheus-config --from-file=prometheus.yml=.\prometheus.yml --dry-run=client -o yaml > prometheus-configmap.yaml

- se debe crear el configmap
kubectl apply -f prometheus-configmap.yaml

- se aplica deployment actualizado 
kubectl apply -f prometheus-deployment.yaml




Para el despliegeue del kubernete:

1. Instalación de Chocolatey 

Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = `
[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))


2. Instalación de minikube

choco install minikube

3. instalación de kompose 

descargarlo de forma oficial en la documentación
https://github.com/kubernetes/kompose/releases

copiarlo en una ruta de sistema y agregarlo en las variables del sistema como una variable nueva e incluirla en el path 

4. convertir el docker-compose 

kompose -f docker-compose-resto.yaml convert -o kompose/


5. Iniciar el minikube 

minikube start

6. despliegue de todos los kompose

kubectl apply -f kompose/

7. para obsercar los servicios

kubectl get services -A

8. verificar la ip del kubernete 
minikube ip

192.168.49.2:32386


192.168.49.2:30158

9. ver si todos los servicios se encuentrar runnig 
kubectl get pods




en caso de fallas, todo se puede eliminar con: 
kubectl delete -f kompose/

eliminar todo el cluster por completo: 
minikube delete
