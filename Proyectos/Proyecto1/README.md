# Descripción de Proyecto1

En este directorio se encuentra el archivo Dockerfile, encargado de construir la imagen necesaria para configurar el entorno de ejecución del proyecto. Este entorno ha sido diseñado para gestionar el pipeline de **TFX**, proporcionando una configuración reproducible y aislada para el procesamiento y análisis de datos, que además sea estable y permita la correcta ejecución de los recursos necesarios para la reproducción del pipeline desarrollado.

📂 Estructura del Directorio:

```plaintext
📁 Proyecto1 
|── 📁 workspace
    |── 📁images
        |── 📄dockerCompose.png     # Pantallazo del comando de docker-compose
        |── 📄notebook.png          # Pantallazo del notebook dentro del contenedor
    |── 📄Proyecto1.ipynb           # Notebooks de JupyterLab con el desarrollo
    |── 📄pyproject.toml            # Configuración de dependencias con uv
    |── 📄README.md                 # Documentación del proyecto
|── 📄dockerfile                    # Construcción de la imagen para creación de la imagen del contenedor
|── 📄README.md                     # Documentación del proyecto
```

En este caso tenemos seguro lo siguiente:  

-   El Dockerfile garantiza la portabilidad del entorno, permitiendo ejecutar el pipeline de manera consistente en diferentes máquinas.

-   El directorio workspace/ proporciona las guías y notebook necesario para la manipulación del pipeline y la ejecución de TFX dentro de JupyterLab.

Este enfoque facilita la reproducibilidad del experimento y asegura un entorno controlado para el manejo de ML Metadata (MLMD) y la canalización de datos dentro de TFX. 

Para poder correr el contenedor desde la consola sin tener que recurrir directamente con el docker-compose, se puede hacer como:

```Bash
docker build -t ml_dev_img .
docker run -p 8888:8888 --name ml_dev -v ${PWD}:/workspace -it ml_dev_img
```

De esta manera se puede buscar recuperar los archivos que se vayan cambiando o creando dentro del contenedor.

Para finalizar matar el contenedor oprimimos Ctrl+C, esto matará el contenedor.

Para matar el contenedor enviamos el siguiente comando 

```Bash 
docker rm ml_dev
```

Para eliminar la imagen que se construyo para el lanzamiento del contenedor lo haríamos con el comando 

```Bash
docker rmi ml_dev_img
```