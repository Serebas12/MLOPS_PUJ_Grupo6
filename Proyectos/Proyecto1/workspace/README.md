# Descripción del Workspace

Este repositorio contiene un notebook de JupyterLab que desarrolla un **pipeline** de **TFX** (**TensorFlow Extended**) para el procesamiento de datos, transformación de características y almacenamiento de metadatos mediante **ML Metadata** (**MLMD**).

El pipeline desarrollado dentro de este notebook permite la ingesta, validación, transformación y análisis de datos, asegurando trazabilidad y reproducibilidad en el proceso de Machine Learning.

La distribución de esta carpeta se ve de la siguiente manera: 

📁 workspace
|── 📁images
    |── 📄dockerCompose.png     # Pantallazo del comando de docker-compose
    |── 📄notebook.png          # Pantallazo del notebook dentro del contenedor
|── 📄Proyecto1.ipynb           # Notebooks de JupyterLab con el desarrollo
|── 📄pyproject.toml            # Configuración de dependencias con uv
|── 📄README.md                 # Documentación del proyecto


##  Requisitos Previos

Antes de ejecutar el notebook, asegúrate de contar con los siguientes requisitos:

Docker y Docker Compose (para entornos reproducibles)
VS CODE, PyCharm, o cualquier software o terminal que permita correr Docker
uv 

**Nota:** el notebook necesita correr en un entorno estable, por ende se recomienda que este notebook se corra dentro de los parámetros configurados en el dockerfile, debido que por medio de la librería uv se logra mantener la estabilidad de la instalación del entorno, sobre todo por TFX, que se pueden obtener incompatibilidades fácilmente con otras librerías escenciales como NumPy.

Componente	Descripción
ExampleGen	Ingresa datos en formato CSV y los convierte a TFRecords.
StatisticsGen	Calcula estadísticas sobre los datos ingeridos.
SchemaGen	Infere automáticamente un esquema de datos.
ExampleValidator	Detecta anomalías en los datos basándose en el esquema.
Transform	Aplica transformaciones de características y normalización.
ML Metadata (MLMD)	Almacena y gestiona metadatos del pipeline, permitiendo el análisis de la trazabilidad.
Para ejecutar el pipeline dentro de JupyterLab, sigue estos pasos:

Clona este repositorio

```Bash
git clone https://github.com/Serebas12/MLOPS_PUJ_Grupo6/Proyectos.git
cd Proyectos
```

Para inicializar el entorno seguro por medio de docker-compose y poder acceder a este notebook por medio del navegador. (**Nota** se recomienda correr el comando de docker-compose cuando se encuentra en el mismo directorio del archivo docker-compose.yaml) [guía rapida para navegar entre carpetas en terminal](https://terminalcheatsheet.com/es/guides/navigate-terminal)

```Bash
docker-compose --build -d
```
![Ejemplo en Consola](images/dockerCompose.png.png)


Luego de haber iniciado el docker-compose, en cualquier navegador con acceso a la terminal donde se encuentra activo el contenedor de docker, se accede a la url localhost:8888/lab, luego de acceder, aparecera la interfaz de JupyterLab, acá el notebook que contiene todo el proceso del manejo del pipeline de TFX y manejo de MLMD se llama Proyecto1.ipynb, acá adentro encontrara todo el desarrollo, paso a paso de como se puede manejar TFX, y breves descripciones sobre el proceso.

![Notebook](images/notebook.png.png)


📄 Referencias

-   [covertype data](https://archive.ics.uci.edu/ml/datasets/covertype)

-   [univariate feature selection](https://scikit-learn.org/stable/modules/feature_selection.html#univariate-feature-selection)

-   [pipeline components](https://www.tensorflow.org/tfx/api_docs/python/tfx/v1/components)

-   [TFX](https://www.tensorflow.org/tfx/guide?hl=es)

-   [MLMD](https://www.tensorflow.org/tfx/guide/mlmd?hl=es)