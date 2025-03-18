## Configuración de la Red para la Comunicación entre Contenedores

Una vez desplegados los contenedores de todos los servicios, podemos comenzar a desarrollar en **JupyterLab**. Sin embargo, antes de hacerlo, es necesario **crear una red compartida** que garantice la comunicación entre los contenedores.

A diferencia de los talleres anteriores, en este caso **cada contenedor fue desplegado de manera independiente**, por lo que se requiere una red común. Para ello, ejecuta el siguiente comando para crear la red **`mi_red_compartida`**:

```bash
docker network create mi_red_compartida
```

Después de crear la red **`mi_red_compartida`**, es necesario conectar los contenedores a esta red para garantizar su comunicación. Esto permitirá que cada servicio pueda interactuar utilizando su nombre de contenedor como host dentro del entorno de Docker.

Ejecuta los siguientes comandos para conectar cada contenedor a la red:

```bash
docker network connect mi_red_compartida mysql_model_data
docker network connect mi_red_compartida jupyterlab
docker network connect mi_red_compartida mlflow_postgres
docker network connect mi_red_compartida Minio
```
Para asegurarnos de que los servicios han sido agregados correctamente a la red **`mi_red_compartida`**, podemos inspeccionar su configuración con el siguiente comando:

```bash
docker network inspect mi_red_compartida
```

## Desarrollo en Jupyter Notebook

Con la comunicación entre los contenedores establecida, podemos comenzar el desarrollo en nuestra instancia de **JupyterLab**. Para ello, se crea el notebook **`mlflow_pipeline.ipynb`**, donde se detalla cada paso del proceso para lograr el entrenamiento del modelo. A manera de resumen a continuación se muestran los principales puntos, el detalle del código ejecutado se puede encontrar en el notebook mencionado.

1. **Carga de datos:** Se extrae la información directamente desde la base de datos **MySQL**, alojándola en un **DataFrame de pandas**.  

2. **Selección del conjunto de datos:** Se divide la información en **datos de entrenamiento y validación**.  

3. **Preprocesamiento de datos:** Se define la transformación de **variables categóricas y numéricas**, integrándolas en un **Pipeline de Scikit-Learn**.  

4. **Optimización del modelo con GridSearchCV:**  
   - Se define un **`GridSearchCV`** con la combinación de parámetros seleccionados.  
   - Se prueban **3 valores** para los hiperparámetros:
     - `classifier__n_estimators`
     - `classifier__max_depth`
     - `classifier__min_samples_split`
   - Esto genera un total de **27 experimentos**.

5. **Entrenamiento y registro en MLflow:**  
   - Se establece la **conexión con MLflow**.  
   - Se entrena el modelo y se almacenan todos los experimentos en **MLflow** dentro del experimento `mlflow_penguins_vf`.  
   - Se habilita **autologging** para registrar automáticamente todos los detalles del entrenamiento.  
   - Se selecciona el **mejor modelo** y se registra con el nombre `modelo_penguins`.  
   - Se usa `max_tuning_runs` para garantizar que todas las ejecuciones sean almacenadas correctamente en MLflow.


Además del registro en **MLflow**, se garantiza que **todos los artefactos generados** durante el proceso de entrenamiento, como modelos, métricas y configuraciones, sean almacenados en **MinIO**. Esto permite una gestión eficiente y centralizada de los resultados del entrenamiento.

El uso de **MinIO** asegura que los archivos sean accesibles de manera estructurada y puedan ser recuperados fácilmente para futuras evaluaciones o despliegues del modelo.

## MlFlow

Una vez ejecutado el proceso en nuestro notebook, podemos acceder a la **interfaz de MLflow** para confirmar que las ejecuciones se han registrado correctamente.

<div align="center">
  <img src="images/mlflow_experimentos.png" alt="Experimentos MLflow" width="1000"/>
</div>

Adicionalmente, se verifica que el mejor modelo haya sido registrado correctamente

<div align="center">
  <img src="images/mlflow_mejor_modelo.png" alt="MLflow registro" width="1000"/>
</div>

Finalmente, se cambia el Stage del modelo a Production, para garantizar que posteriormente pueda ser consumido por el API. 

<div align="center">
  <img src="images/mlflow_produccion.png" alt="MLflow registro" width="1000"/>
</div>

## FastAPI

Una vez que el modelo ha sido **disponibilizado en MLflow**, procedemos a la creación de una **API** que permita realizar predicciones basadas en el modelo entrenado. Para ello, utilizaremos **FastAPI** como base, reutilizando el código desarrollado en talleres anteriores, pero aplicando los siguientes cambios:

1. **Actualización de dependencias**  
   - Se actualiza el archivo `requirements.txt` para garantizar la compatibilidad con los modelos desarrollados y la librería **MLflow**.  

2. **Modificación del método `GET /listar_modelos`**  
   - Se ajusta este endpoint para listar **todos los modelos disponibles en MLflow**.  

3. **Modificación del método `POST /predict`**  
   - Permite usar un modelo desde la lista de modelos disponibles en MLflow.  
   - Carga el modelo seleccionado directamente desde **MLflow Model Registry**.  
   - Realiza la predicción en base a los datos proporcionados.  

Con estos cambios, la API podrá gestionar múltiples modelos y realizar predicciones de manera eficiente utilizando MLflow como backend.

Para el despliegue de **FastAPI**, utilizamos **Docker Compose**, manteniendo la estructura del taller en la que cada servicio se despliega de manera independiente. Esto permite una gestión modular y escalable de los componentes. Para construir y desplegar el contenedor de la API, ejecuta el siguiente comando:

```bash
sudo docker-compose -f docker-compose-fastapi.yaml up --build -d
```

Al igual que con los otros contenedores, es fundamental garantizar que la **API de modelos** esté en la misma red para permitir la comunicación con los demás servicios. Para ello, conectamos el contenedor a la red **`mi_red_compartida`** con el siguiente comando:

```bash
docker network connect mi_red_compartida api_models
```

Una vez que la API ha sido completamente desplegada, podemos realizar una prueba para asegurarnos de que está funcionando correctamente y puede procesar solicitudes de predicción.

<div align="center">
  <img src="images/fastapi_get.png" alt="MLflow registro" width="1000"/>
</div>

<div align="center">
  <img src="images/fastapi_post.png" alt="MLflow registro" width="1000"/>
</div>