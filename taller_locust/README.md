Retomamos el proyecto 2 ya desarrollado, con la excepción de que no utilizaremos streamlit 
para esta parte para el levantamiento de los servicios y demás todo es tal cual ya lo desarrollado en el p2

iniciamos con la exportación de la imagen de fastapi de inferencia para poderla usar, en este caso usamos los comandos 

debemos poder activar y/o verificar que se encuentra activa la sesión con
```bash
docker login
```

verificamos el nombre de la imagen de inferencia usando fastapi con el comando 
```bash
docker ps -a
```

Luego, desde el comando que tenemos, debemos etiquetar la imagen que bamos a cargar al docker hub con el comando 
```bash
docker tag proyecto2-fast_api:latest blutenherz/repo_inference_p2:inference_p2
```

Publicamos la imagen de docker hub por medio del siguiente comando
```bash
docker push blutenherz/repo_inference_p2:inference_p2
```

Podemos observar la imagen publicada en el enlace 
```bash
https://hub.docker.com/repository/docker/blutenherz/repo_inference_p2/tags
```

Iniciamos el docker compose de inferencia trayendo la imagen construida desde docker hub
```bash
docker compose -f docker-compose-inference.yaml up --build -d
```

bajar por completo el docker compose 
```bash
docker compose -f docker-compose-inference.yaml down -v --rmi all
```
Luego de iniciar el docker compose de la inferencia, buscamos el bridge activo del proyecto 2 con 

```bash
docker network ls
```

Luego, de haber identificado el bridge de proyecto 2, conectamos el nuevo contenedor de manera manual con 

```bash
docker network connect proyecto2_default inference
```

Luego entramos a la interfaz de la api y podemos hacer pruebas para identificar que se logro la conexión por medio del enlace 
```bash 
http://localhost:8000/docs
```

construimos el docker compose de locust con el comando 
```bash
docker compose -f docker-compose-locust.yaml up --build -d
```

para eliminarlo 
```bash
docker compose -f docker-compose-locust.yaml down -v --rmi all
```

Luego de construir el docker compose de locust, podemos entrar a la ui mediante el enlace 

```bash
http://localhost:8089
```

Luego para conectar los contenedores creados lo hacemos por medio de un network externo

Creamos primero la red
```bash
docker network create testnet
```

conectamos los contenedores al network
```bash
docker network connect testnet inference
docker network connect testnet locust
```

Para empezar a buscar cual es la capacidad mínima para la api de inferencia iniciamos la prueba con 10k usuarios con aumento de 500, los recursos iniciales son:

![Recursos Iniciales](images/initial_deploy.png)

Con lo anterior, obtenemos los siguientes resultados

lo que implica que tenemos bastante demora en respuesta, así que lanzamos la api sin restricciones de recursos y al obtener los mismos resultados concluimos que la función predict es la que se tarda más de lo esperado, debido que dentro de la función predict estamos cargando el modelo desde el bucket de minio, además de revisar el registro en mlflow, lo que por detrás consume tiempo adicional y posibilita esta suma en los tiempos de respuesta. Es un hallazgo que debemos mejorar para un próximo desarrollo, sacando el llamado del modelo por fuera del atributo post para que el modelo se mantenga en memoria mientras se usa en la función predict.

con lo anterior, además de la prueba con 1024M y 1 cpu tenemos el mismo resultado probaremos con réplicas, lo cual necesitamos:

inicial docker swarm para eso tenemos el comando 
```bash
docker swarm init
```

destruimos el docker compose con el que lanzamos la inferencia y lo lanzamos con docker swarm
```bash
docker stack deploy -c docker-compose-inference.yaml p2stack
```
