#           Taller Argo

Inicializar la api a modo de prueba
```bash
py -3.9 -m venv venv
venv/Scripts/activate
cd api
pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload
```

Modo de acceso
```plaintext
localhost:8000
```

Pruebas de la API
```plaintext
{
  "bill_length_mm": 45.1,
  "bill_depth_mm": 14.5,
  "flipper_length_mm": 210,
  "body_mass_g": 4200
}
{
  "bill_length_mm": 50.2,
  "bill_depth_mm": 15.1,
  "flipper_length_mm": 220,
  "body_mass_g": 5400
}
{
  "bill_length_mm": 38.2,
  "bill_depth_mm": 18.1,
  "flipper_length_mm": 180,
  "body_mass_g": 3750
}
```

Inicialización de un contenedor de prueba que guarde la API
```bash
deactivate
docker build -t api-fastapi .
docker run -p 8989:8989 --name api-run -it api-fastapi
```

Borrar tanto el contenedor como la imagen de la API
```bash
docker rm api-run
docker rmi api-fastapi
```

Prueba del testerload con la api, se adiciona el docker compose sólo para este propósito
corroboramos las solicitudes por segundo y matamos los contenedores
```bash
cd ..
docker compose up --build 
```

Eliminamos la prueba por completo 
```bash
docker compose down --rmi all 
```

