#       Desarrollo Proyecto 2

Este repositorio incluye los archivos y configuraciones esenciales para el despliegue de un entorno de **Airflow**, **MLflow**, **MinIO**, **FastAPI** y **Streamlit**, permitiendo la construcción de un flujo completo para la ingesta, modelado, registro y despliegue de modelos de machine learning, todo orquestado desde un DAG de Airflow.

La arquitectura propuesta permite experimentar con la trazabilidad, versionamiento y producción de modelos ML, siguiendo buenas prácticas de ingeniería de datos y MLOps.

---

##      Estructura del Proyecto

A continuación se muestra la estructura del proyecto bajo el formato jerárquico con íconos:

```plaintext
📁 PROYECTO2
│
├── 📁 airflow                  # Configuración del orquestador de tareas (Airflow)
│   ├── 📄 Dockerfile
│   └── 📄 requirements.txt
│
├── 📁 app                      # API FastAPI para servir el modelo entrenado
│   ├── 📄 Dockerfile
│   ├── 📄 main.py
│   └── 📄 requirements.txt
│
├── 📁 dags                     # DAG de entrenamiento, registro y publicación del modelo
│   └── 📄 modeling_covertype.py
│
├── 📁 external                 # API alterna que simula la fuente de datos externa
│   ├── 📁 data                 # Datos de ejemplo para el servicio simulado
│   ├── 📄 Dockerfile
│   ├── 📄 main.py
│   └── 📄 requirements.txt
│
├── 📁 jupyterlab               # Entorno para experimentación manual del pipeline
│   ├── 📄 Dockerfile
│   └── 📄 requirements.txt
│
├── 📁 logs                     # Archivos generados por Airflow durante la ejecución
│   ├── 📁 dag_id=DAG_p2
│   ├── 📁 dag_id=mlflow_test_dag
│   ├── 📄 dag_processor_manager
│   └── 📄 scheduler
│
├── 📁 mlflow                   # Configuración adicional para el servidor de MLflow
│   ├── 📄 Dockerfile
│   └── 📁 plugins
│
├── 📄 .env                     # Variables de entorno para configuración de servicios
├── 📄 borrador_modelo.ipynb    # Notebook inicial de exploración del modelo
├── 📄 docker-compose-external.yaml   # Orquestación de la API alterna
├── 📄 docker-compose-p2.yaml         # Despliegue completo del entorno de producción
├── 📄 Puerto 80 Cerrado.png   # Imagen de referencia para errores comunes
├── 📄 README.md                # Este archivo
└── 📄 streamlit_app.py         # Interfaz de usuario para consumo del modelo
```

Esta organización modular permite una gestión eficiente de cada componente del flujo de datos y facilita la escalabilidad del entorno.

---

##      Despliegue de API Alterna

La API alterna simula el comportamiento de la fuente de datos del profesor. Entrega lotes de datos cada minuto, lo que permite probar escenarios de ingesta continua dentro del DAG de Airflow.

```bash
docker compose -f docker-compose-external.yaml up --build -d
```

Para detenerla:

```bash
docker compose -f docker-compose-external.yaml down -v --rmi all
```

Verificación de servicio:

```bash
curl http://localhost:80/
curl "http://localhost:80/data?group_number=6"
```

---

##      Despliegue del Esquema Completo

Se orquestan los siguientes servicios:
- **Airflow**: planificación y ejecución del pipeline
- **MySQL (x2)**: almacenamiento de datos y metadata de MLflow
- **MLflow**: tracking, registro y gestión del modelo
- **MinIO**: almacenamiento de artefactos con compatibilidad S3
- **FastAPI**: API REST para servir el modelo entrenado

### Comandos para levantar el entorno

```bash
sudo docker compose -f docker-compose-p2.yaml up airflow-init
sudo docker compose -f docker-compose-p2.yaml up --build -d
```

Para desmontar completamente el stack:

```bash
sudo docker compose -f docker-compose-p2.yaml down -v --rmi all
```

### Accesos a servicios

| Servicio     | URL                       | Usuario   | Contraseña     |
|--------------|----------------------------|-----------|----------------|
| Airflow      | http://localhost:8080     | airflow   | airflow        |
| MLflow       | http://localhost:5000     | mlflow    | mlflow         |
| MinIO        | http://localhost:9001     | admin     | supersecret    |
| FastAPI      | http://localhost:8989     | -         | -              |

Verificación general de contenedores:

```bash
docker ps -a
```

Logs de contenedores:

```bash
docker logs <nombre-del-contenedor>
```

Logs esperados en MLflow para conexión a MySQL:

```text
INFO [alembic.runtime.migration] Context impl MySQLImpl.
INFO [alembic.runtime.migration] Running upgrade  -> <hash>
```

> ⚠️ Puede que los primeros intentos de conexión fallen. Lo importante es que finalmente se observe la conexión exitosa en los logs.

---

##      Configuración de Airflow

Desde la UI de Airflow se debe crear una conexión a MySQL:

- **Connection ID**: `mysql_default`
- **Connection Type**: `MySQL`
- **Host**: `mysql-data-store`
- **Schema**: `datadb`
- **Login**: `admin`
- **Password**: `supersecret`
- **Port**: `3306`

El DAG `DAG_p2` es el encargado de:
- Ingresar datos desde la API
- Entrenar un modelo con `GridSearchCV`
- Evaluarlo y registrar métricas
- Publicarlo en **MLflow Model Registry**
- Promoverlo automáticamente al stage **Production**
- Almacenar artefactos en **MinIO**

---

##      Visualización e Inferencia con Streamlit

Para levantar la interfaz de usuario que permite hacer predicciones con el modelo entrenado:

```bash
streamlit run streamlit_app.py --server.port 8503
```

Luego acceder desde:

```bash
http://localhost:8503
```

Esta aplicación permite ingresar valores manualmente, enviar datos al modelo publicado y visualizar las predicciones al instante.

---

##      Aclaraciones del Código

Este proyecto nace a partir de las bases proporcionadas por el profesor. Se realizaron ajustes clave para permitir:

- Un entorno dockerizado y replicable
- Un esquema de orquestación con dependencias entre servicios
- Entrenamiento supervisado automatizado vía Airflow
- Registro de métricas y artefactos en MLflow y MinIO
- Promoción automática del mejor modelo al stage "Production"
- Consumo del modelo vía FastAPI y visualización con Streamlit

Gracias a este enfoque, se garantiza la reproducibilidad del experimento, la trazabilidad de los modelos y una estructura modular para posibles integraciones futuras en ambientes de desarrollo reales o en producción.

