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
