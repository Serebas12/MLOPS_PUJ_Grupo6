import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd

#Inicia la aplicación
app = FastAPI(
    title="API de Predicción de especie de Pingüinos",
    description="Esta API tiene 2 modelos que permiten realizar la inferencia de la especie de Pingüinos entre Adelie, Chinstrap y Gentoo",
    version="1.0.0"
)

log_dir_docker = "/app/logs"  # Ruta dentro del contenedor (volumen de Docker)
log_dir_local = "/app/logs_local"  # Ruta mapeada a la máquina host
os.makedirs(log_dir_docker, exist_ok=True)
os.makedirs(log_dir_local, exist_ok=True)
log_file_docker = os.path.join(log_dir_docker, "predictions.log")
log_file_local = os.path.join(log_dir_local, "predictions.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_docker),  # Guarda logs en el volumen
        logging.FileHandler(log_file_local),   # Guarda logs por el bind mount
        #logging.StreamHandler()  # Muestra logs en la consola
    ]
)

logger = logging.getLogger()

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
    - **model**: Modelo que se desea utilizar. Valores validos modelRF y modelSVM. 
    
    Devuelve un JSON con la predicción.
    """

    ### Predicción modelo 1
    if input_data.model =="modelRF":

        #Se carga el modelo 
        try:
            with open("modeloRF.pkl", "rb") as f:
                modelRF = pickle.load(f)
        except Exception as e:
            raise RuntimeError(f"Error al cargar el modelo: {e}")


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
            prediction = modelRF.predict(data)
            resultado = prediction[0]

            logging.info(f"Predicción realizada: {resultado}")
            return {"prediction": resultado}
        except:
            logging.info(f"Predicción realizada: no valido")
            return {"prediction": "no valido"}

    ### Predicción modelo 2    
    elif input_data.model =="modelSVM":

        #Se carga el modelo 
        try:
            with open("modeloSVM.pkl", "rb") as f:
                modeloSVM = pickle.load(f)
        except Exception as e:
            raise RuntimeError(f"Error al cargar el modelo: {e}")

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
            prediction = modeloSVM.predict(data)
            resultado = prediction[0]
            logging.info(f"Predicción realizada: {resultado}")
            return {"prediction": resultado}
        
        except:
            logging.info(f"Predicción realizada: no valido")
            return {"prediction": "no valido"}
        
    else: 
        return {"prediction": "modelo no valido"}