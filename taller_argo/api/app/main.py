from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Cargar modelo entrenado
model = joblib.load("app/model.pkl")

# Mapeo fijo de clases
# Se deja quemado por optimización de recursos, buscamos la API lo más lígera posible
species_names = ["Adelie", "Chinstrap", "Gentoo"]

# Crear app
app = FastAPI(
    title="API de Predicción de especie de Pingüinos",
    description="Predice especie de pingüino según características morfológicas",
    version="1.0.1"
)

# Métrica Prometheus
PREDICTION_COUNTER = Counter("predict_requests_total", "Número de predicciones realizadas")

# Entrada de usuario
class PenguinInput(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

# Endpoint de predicción
@app.post("/predict")
async def predict(penguin: PenguinInput):
    PREDICTION_COUNTER.inc()
    data = np.array([[penguin.bill_length_mm, penguin.bill_depth_mm,
                      penguin.flipper_length_mm, penguin.body_mass_g]])
    prediction_index = model.predict(data)[0]
    return {"prediction": species_names[int(prediction_index)]}

# Endpoint de métricas Prometheus
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
