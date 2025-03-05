# Descripción de Proyectos

Este directorio está diseñado para almacenar y organizar todos los proyectos desarrollados a lo largo del curso, manteniendo una estructura modular en la que cada proyecto se gestiona dentro de su propio directorio.

Estructura y funcionalidades clave:

-   Cada proyecto cuenta con su propio directorio, facilitando la gestión y ejecución de múltiples experimentos dentro del mismo entorno.

-   El archivo docker-compose.yaml permite orquestar la ejecución de cada proyecto, definiéndolos como servicios independientes dentro de un mismo entorno de contenedores.

-   Se facilita la conexión entre servicios, permitiendo la comunicación entre distintos componentes como por ejemplo el pipeline de TFX.

-   Posibilidad de crear un volumen compartido, optimizando el almacenamiento de datos y permitiendo que los proyectos accedan a los mismos recursos sin duplicar información innecesaria.

Ventajas de esta configuración:

-   Permite la ejecución y administración centralizada de múltiples proyectos dentro de diferentes contenedores de Docker.

-   Facilita la colaboración y reutilización de recursos entre diferentes experimentos.

-   Proporciona un entorno aislado y reproducible, asegurando que cada pipeline de TFX se ejecute con la configuración esperada.

Este enfoque modular optimiza la escalabilidad y flexibilidad del desarrollo, permitiendo ampliar la infraestructura según las necesidades del curso y los proyectos en ejecución.

La configuración de la carpeta viene dada como:

```plaintext
📁 Proyectos 
    📁 Proyecto1 
    |── 📁images
        |── 📄dockerCompose.png         # Pantallazo del comando de docker-compose
        |── 📄notebook.png              # Pantallazo del notebook dentro del contenedor
    |── 📄Proyecto1.ipynb               # Notebooks de JupyterLab con el desarrollo
    |── 📄pyproject.toml                # Configuración de dependencias con uv
    |── 📄dockerfile                    # Construcción de la imagen para creación de la imagen del contenedor
    |── 📄README.md                     # Documentación del proyecto sobre el manejo del dockerfile
|── 📄docker-compose.yaml               # archivo de docker-compose para administrar todos los proyectos
|── 📄README.md                         # Documentación del proyecto acerca del docker-compose.yaml
```


Para poder inicializar docker-compose para que lance todos los servicios que hallamos diligenciado se hace como:

```Bash
docker-compose up --build -d
```

Esto permite iniciar docker-compose para que construya la imagen correspondiente de cada proyecto desarrollado y aliste dado el caso los volumenes necesarios.

Para matar todos los contenedores lanzados con docker-compose se utiliza el siguiente comando:

```Bash
docker-compose down
```
Esto matará todos los contenedores lanzados, pero no borrará ninguna imagen ni volumen creado previamente, esto nos da la posibilidad de poder recuperar los archivos modificados dentro del contenedor y almacenados dentro del volumen.

En dado caso, que uno quiera borrar los volumenes con los cuales se hayan inicializado con el docker-compose, e iniciar nuevamente con la configuración inicial del proyecto el comando para matar los contenedores junto con los volumenes es:

```Bash 
docker-compose down -v
```
Para mayor detalle sobre el desarrollo de los proyectos, dentro del directorio de cada uno se encuentra el correspondiente README.md con el detalle de cada uno.
