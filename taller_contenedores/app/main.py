from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
import os

#Inicia la aplicación
app = FastAPI(
    title="API de Predicción de especie de Pingüinos",
    description="Esta API tiene 2 modelos que permiten realizar la inferencia de la especie de Pingüinos entre Adelie, Chinstrap y Gentoo",
    version="1.0.0"
)

#Se genera decorador para listar los modelos 


MODEL_DIR = "/home/jovyan/work/"

@app.get("/listar_modelos")

async def list_models():
    """
    Lista todos los archivos .pkl en el directorio de trabajo.
    """
    try:
        modelos = [f.replace(".pkl", "") for f in os.listdir(MODEL_DIR) if f.endswith(".pkl")]
        return {"modelos_disponibles": modelos}
    except Exception as e:
        return {"error": f"No se pudieron listar los modelos: {str(e)}"}


#Datos requeridos de la solicitud
class PenguinsInput(BaseModel):
    island: str	
    culmen_length_mm: float	
    culmen_depth_mm: float
    flipper_length_mm: float	
    body_mass_g: float	
    sex: str
    model: str	


#Se genera el decorador por modelo
@app.post("/predict")

async def predict(input_data: PenguinsInput):

    """
    Puede realizar la predicción de la especie de un pingüino, seleccionando uno de los modelos pre entrenados.
    
    - **island**: Isla a la que pertenece el pingüino. Valores validos Biscoe, Dream y Torgersen.
    - **sex**: Sexo del pingüinos. Valores validos MALE, FEMALE.
    - **culmen_length_mm**: Longitud del culmen en mm.
    - **culmen_depth_mm**: Profundidad del culmen en mm.
    - **flipper_length_mm**: Profundidad de la aleta en mm.
    - **body_mass_g**: Masa corporal en mm.
    - **model**: Modelo que se desea utilizar. 

    Devuelve un JSON con la predicción.
    """

    ### Predicción modelo 1

        #Se carga el modelo 
    try:
        with open(f"/home/jovyan/work/{input_data.model}.pkl", "rb") as f:
            model = pickle.load(f)
    except:
        return  {"prediction": "Modelo no encontrado / no valido"}

    try:
        # Tratamiento de información
        data = pd.DataFrame([{
            "island": input_data.island,
            "sex": input_data.sex,
            "culmen_length_mm": input_data.culmen_length_mm,
            "culmen_depth_mm": input_data.culmen_depth_mm,
            "flipper_length_mm": input_data.flipper_length_mm,
            "body_mass_g": input_data.body_mass_g
        }])

        # Prediccion del modelo
        prediction = model.predict(data)
        resultado = prediction[0]

        return {"prediction": resultado}
    except:
        return {"prediction": "no valido"}

    
