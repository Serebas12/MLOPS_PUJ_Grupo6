from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

#Inicia la aplicación
app = FastAPI()

#Datos requeridos de la solicitud
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

#Se carga el modelo 
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    raise RuntimeError(f"Error al cargar el modelo: {e}")

#Se genera el decorador por modelo
@app.post("/predict/model1")

async def predict(input_data: IrisInput):
    try:
        # Tratamiento de información
        data = np.array([
            input_data.sepal_length,
            input_data.sepal_width,
            input_data.petal_length,
            input_data.petal_width
        ]).reshape(1, -1)

        # Prediccion del modelo
        prediction = model.predict(data)
        # Convertir la predicción a entero (ya que scikit-learn retorna un array)
        result = int(prediction[0])
        return {"prediction": result}
    except:
        return {"prediction": "no valido"}