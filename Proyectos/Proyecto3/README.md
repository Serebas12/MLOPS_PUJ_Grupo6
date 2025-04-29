
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




en caso de fallas, todo se puede eliminar con: 
kubectl delete -f kompose/

eliminar todo el cluster por completo: 
minikube delete
