IP para interconectar los diferentes servicios 
10.43.101.192
Dentro de esta ip se disponibilizan los puertos para la disponibilización de la comunicación entre estos

primer paso, inicilizar la base de datos usando docker (para terminos de continuar con el uso de esta herramienta)
como se disponibiliza un docker compose especializado sólo para mysql, es necesario inicializar con el comando 
sudo docker compose -f docker-compose-mysql.yml up --build -d 
para destruir la base de datos por completo se hace (se borra también el volumen persistente)
sudo docker compose -f docker-compose-mysql.yml down -v --rmi all

para acceder a la base de datos dentro del contenedor el comando es 
sudo docker exec -it mysql_model_data bash
accedemos a la base de datos con
mysql -u admin -psupersecret mydatabase
revisar que haya cargado la data correctamente 
SHOW TABLES;
SELECT * FROM penguins LIMIT 10;
SELECT COUNT(*) FROM penguins;

luego salimos de la interfaz con exit

Segundo paso, inicialización de mlflow por systemd
se instala postgresql en la vm
sudo apt install postgresql-client-common
se instala la instancia para que python reconozca postgresql
pip install psycopg2-binary

para seguir el proceso de crear las bases de datos en docker para mantener la reproducibilidad de la imagen, inicializamos docker compose de la base de datos postgresql, el comando es
sudo docker compose -f docker-compose-postgresql.yml up --build -d
sudo docker compose -f docker-compose-postgresql.yml down -v --rmi all
Luego instalamos las dependencias necesarias 
sudo pip install mlflow awscli boto3
Luego ejecutamos uno a uno los siguientes comandos, esto recargara los daemon, habilitara el servicio, inicializará el servicio y nos mostrara el status del servicio inicializado
sudo systemctl daemon-reload
sudo systemctl enable /home/estudiante/Documents/MLOPS_PUJ_Grupo6/taller_mlflow/mlflow_serv.service
sudo systemctl start mlflow_serv.service
sudo systemctl status mlflow_serv.service 
en caso de caida para levantar de nuevo mlflow
sudo systemctl daemon-reload
sudo systemctl restart mlflow_serv.service
logs 
sudo journalctl -u mlflow_serv.service -b
forzar que se detenga un systemd
sudo systemctl stop mlflow_serv.service
linea borrada del .service
WorkingDirectory=/home/estudiante/Documents/MLOPS_PUJ_Grupo6/taller_mlflow/mlflow

seguimiento de procesos activos
sudo ss -tlnp | grep :5000

tercer paso levantamiento de minio 
el docker compose se puede utilizar el mismo, por lo tanto sólo es necesario levantarlo con el comando 
sudo docker compose -f docker-compose.yaml up --build -d
sudo docker compose -f docker-compose.yaml down -v --rmi all

cuarto paso
levantamiento de jupyterlab 
creamos una carpeta llamada jupyterlab con el propósito de dejar tanto el dockerfile como los notebooks que necesitemos 
cd JupyterLab
sudo docker build -t jupyterlab .
sudo docker run -it --name jupyterlab --rm -e TZ=America/Bogota --network host -p 8888:8888 -v $PWD:/work jupyterlab:latest


ip addr
