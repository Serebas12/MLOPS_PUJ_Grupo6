#           Desarrollo Proyecto 3   

Este repositorio contiene los archivos, configuraciones y recursos necesarios para desplegar un entorno completo de MLOps utilizando Kubernetes, integrando los servicios de Airflow, MLflow, Prometheus, Grafana, FastAPI y Streamlit. Este ecosistema robusto permite implementar un flujo de trabajo integral que abarca la ingesta, procesamiento, modelado, registro, despliegue y monitoreo de modelos de machine learning, todo gestionado y automatizado mediante DAGs orquestados con Airflow.

El proyecto forma parte del curso de Operaciones de Machine Learning de la Pontificia Universidad Javeriana y tiene como objetivo no solo encontrar el mejor modelo posible para el conjunto de datos propuesto (encuentros hospitalarios relacionados con diabetes en EE.UU. entre 1999 y 2008), sino también diseñar e implementar una arquitectura moderna que refleje las mejores prácticas de MLOps, poniendo énfasis en la trazabilidad, el versionamiento, la automatización y la escalabilidad.

El flujo del proceso incluye:

*   La recolección e ingestión de datos mediante pipelines controlados por Airflow.

*   El almacenamiento de datos en bases especializadas.

*   El preprocesamiento y entrenamiento periódico de modelos.

*   El registro automático de los resultados en MLflow.

*   La selección y publicación automática del modelo óptimo al entorno de producción.

*   El consumo del modelo en línea a través de una API desarrollada en FastAPI.

*   La exposición de resultados al usuario final mediante una interfaz interactiva construida con Streamlit.

*   Y la integración de herramientas de monitoreo como Prometheus y Grafana, junto a pruebas de carga con Locust, para garantizar la resiliencia y desempeño del sistema en condiciones reales de operación.

La entrega final incluye el código fuente en un repositorio público, el despliegue funcional sobre Kubernetes, y una sustentación en video explicando la arquitectura, los procesos implementados y las métricas obtenidas, demostrando así la capacidad del sistema para operar como un flujo MLOps completamente automatizado y trazable.

---

##          Estructura del Directorio

A continuación presentamos la estructura del directorio del proyecto, donde organizamos los diferentes objetos y elementos necesarios para el despliegue de todos los servicios, usando inicialmente **Docker** para crear la arquitectura base y realizar nuestras primeras pruebas, y luego, mediante el uso de Kompose traducir los scripts en los respectivos manifiestos para desplegar **Kubernetes**

También se recalca la necesidad de haber realizado el escrito de 3 `docker-compose`, con el objetivo de poder desplegar `aiflow`, `jupyterlab` y el resto de los servicios, esto con el propósito de poderlos traducir y llevar a Kubernetes. 

```plaintext
📁 PROYECTO3
├── 📁 airflow 
│   ├── 📄 Dockerfile
│   └── 📄 requirements.txt
├── 📁 app 
│   ├── 📄 Dockerfile
│   ├── 📄 main.py
│   └── 📄 requirements.txt
├── 📁 dags 
│   ├── 📄 cleandata_pipeline.py
│   ├── 📄 insert_rawdata_init.py
│   └── 📄 modeling.py
├── 📁 data 
│   └── 📄 Diabetes.csv
├── 📁 images                                   #   Imagenes
├── 📁 initdb 
│   ├── 📄 01_schemas.sql
│   └── 📄 Dockerfile
├── 📁 jupyter 
│   ├── 📄 ProfileReport_2025-04-30_diabetes_class.html
│   ├── 📄 dockerfile
│   ├── 📄 penguins_size.csv
│   ├── 📄 pruebas.ipynb
│   ├── 📄 pruebas2.ipynb
│   └── 📄 requirements.txt
├── 📁 kompose 
│   ├── 📄 fast-api-deployment.yaml 
│   ├── 📄 fast-api-service.yaml 
│   ├── 📄 grafana-deployment.yaml 
│   ├── 📄 grafana-service.yaml 
│   ├── 📄 locust-deployment.yaml 
│   ├── 📄 locust-service.yaml 
│   ├── 📄 minio-deployment.yaml 
│   ├── 📄 minio-service.yaml 
│   ├── 📄 minio-data-persistentvolumeclaim.yaml 
│   ├── 📄 mlflow-deployment.yaml 
│   ├── 📄 mlflow-service.yaml 
│   ├── 📄 mlops-postgres-deployment.yaml 
│   ├── 📄 mlops-postgres-service.yaml 
│   ├── 📄 postgres-mlflow-persistentvolumeclaim.yaml
│   ├── 📄 prometheus-configmap.yaml 
│   ├── 📄 prometheus-deployment.yaml 
│   ├── 📄 prometheus-service.yaml 
│   ├── 📄 streamlit-deployment.yaml 
│   └── 📄 streamlit-service.yaml 
├── 📁 locust 
│   ├── 📄 Dockerfile
│   ├── 📄 locustfile.py
│   └── 📄 requirements-locust.txt 
├── 📁 mlflow 
│   └── 📄 Dockerfile
├── 📁 streamlit 
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   └── 📄 streamlit_app.py
├── 📄 .env 
├── 📄 README.md 
├── 📄 docker-compose-airflow.yaml 
├── 📄 docker-compose-jupyter.yaml 
├── 📄 docker-compose-kubernete.yaml 
├── 📄 docker-compose-resto-back.yaml 
└── 📄 prometheus.yml 
```

Esta organización modular permite una gestión eficiente de cada componente del flujo de datos y facilita la escalabilidad del entorno.

##          Primera Fase (Despliegue por Docker)

Como primer pase del proceso de despliegue, realizamos todo el levantamiento inicial de los servicios utilizando **Docker**, ya que esto nos permite validar en un entorno controlado que las imágenes construidas funcionan correctamente antes de trasladarlas a un entorno más complejo como **Kubernetes**. De esta forma, aseguramos que cada contenedor tiene el comportamiento esperado y que las dependencias entre servicios están resueltas.

###         Paso 1: Crear Red Compartida    

Primero creamos una red interna en Docker que permitirá que todos los servicios definidos en los distintos docker-compose se comuniquen entre sí:

```bash
sudo docker network create airflow_backend
```

Esta red se usará para interconectar los servicios como Airflow, PostgreSQL, MLflow, Streamlit y otros, garantizando que puedan referenciarse por nombre de contenedor.

###         Paso 2: Desplegar Airflow   

Airflow es el orquestador central del pipeline. Su despliegue incluye también la base de datos PostgreSQL para almacenar metadatos de ejecución. Iniciamos el servicio con los siguientes comandos:

```bash
sudo docker compose -f docker-compose-airflow.yaml up airflow-init
sudo docker compose -f docker-compose-airflow.yaml up --build -d
```

El primer comando (airflow-init) prepara la base de datos y las configuraciones iniciales. El segundo comando levanta los contenedores en modo desacoplado (-d) y reconstruye las imágenes si es necesario (--build).

###         Paso 3: Desplegar servicios complementarios

Una vez Airflow está en ejecución, procedemos a levantar todos los servicios adicionales definidos para el entorno MLOps (MLflow, Prometheus, Grafana, FastAPI, Streamlit, etc.) con:

```bash
sudo docker compose -f docker-compose-kubernete.yaml up --build -d
```

Esto asegura que todos los servicios estén disponibles y accesibles dentro de la red Docker.

###         Paso 4: Desplegar JupyterLab (Opcional)

Si queremos habilitar un entorno interactivo para exploración, desarrollo y prueba de código, podemos desplegar JupyterLab:

```bash
sudo docker compose -f docker-compose-jupyter.yaml up --build -d
```

Este contenedor nos permite conectarnos a los datos y servicios ya levantados para realizar pruebas manuales o análisis exploratorio.

###         Bajar Servicios 

En caso de necesitar apagar o reconstruir los servicios, usamos los siguientes comandos para derribar los entornos específicos, eliminando también las imágenes y volúmenes asociados:

```bash
sudo docker compose -f docker-compose-airflow.yaml down --rmi all -v        # Para bajar airflow
sudo docker compose -f docker-compose-kubernete.yaml down --rmi all -v      # Para bajar servicios complementarios
sudo docker compose -f docker-compose-jupyter.yaml down --rmi all -v        # Para bajar jupyterlab
```

###         Revisión del Estado y Exposición de los Servicios   

Una vez levantados todos los servicios mediante Docker, iniciamos la etapa de revisión para asegurarnos de que cada componente se está ejecutando correctamente y es accesible desde los puertos configurados en `localhost`.

Podemos validar la exposición accediendo desde un navegador web a las siguientes direcciones:

```bash 
http://localhost:8989       # fastapi
http://localhost:8501       # streamlit
http://localhost:3000       # grafana
http://localhost:5000       # mlflow
http://localhost:9090       # promehteus
http://localhost:9001       # minio
http://localhost:8888       # jupyter
```

Es importante comprobar que al acceder a cada uno de estos endpoints, los servicios levantan sus respectivas interfaces y que no presentan errores de conexión, tiempo de espera o conflictos de puerto. Este paso asegura que la arquitectura montada en Docker funciona como se espera antes de avanzar al despliegue en Kubernetes.


Estando dentro del endpoint de minio, creamos un bucket llamado mlflows3, donde se almacenara los artefactos correspondientes a los modelos entrenados a traves de airflow 






```bash 

```


docker compose -f docker-compose-airflow.yaml exec airflow-scheduler ls -l /opt/airflow/dags


```bash 
sudo docker compose -f docker-compose-jupyter.yaml up --build -d
```

```bash
sudo docker compose -f docker-compose-jupyter.yaml down --rmi all -v
```

```bash

```


el primer dag en correr por única vez es raw_data_initial_batch_load, este DAG realiza la primer carga de los datos en la tabla de la rawdata, con este procedimiento garantizamos que se carga los datos a la rawdata y esperamos a que termine, sólo se necesita correr una primera vez

Luego seguimos con el DAG clean_data_pipeline, el cual se encarga de hacer la carga de datos de la rawdata, hace la limpieza de los mismos y los carga, es importante sólo encenderlo después de que finalice raw_data_initial_batch_load, así garantizamos que el flujo de consumo de datos quede activo, adicional, tenemos las columnas load_date y processed_date que son las columnas que nos permiten hacer seguimiento de la carga y flujo de datos en las cargas de datos


docker exec -it proyecto3-mlops-postgres-1 bash
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

