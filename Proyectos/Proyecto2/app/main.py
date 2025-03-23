from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
import os
import mlflow
import boto3

#Inicia la aplicación
app = FastAPI(
    title="API de Predicción de especie de Pingüinos",
    description="Esta API tiene 2 modelos que permiten realizar la inferencia de la especie de Pingüinos entre Adelie, Chinstrap y Gentoo",
    version="1.0.0"
)

#Se genera decorador para listar los modelos 

MODEL_DIR = "/app/models/"

@app.get("/listar_modelos")

async def list_models():
    """
    Lista todos los archivos .pkl en el directorio de trabajo.
    """

# Configurar la URL del servidor de MLflow (ajusta según tu caso)
    try:
        mlflow.set_tracking_uri("http://0.0.0.0:5000") 

        # Obtener la lista de modelos registrados en MLflow
        models = mlflow.search_registered_models()

        # Mostrar los modelos disponibles
        res_model=[]
        for model in models:
            res_model.append(model.name)

        return {"modelos_disponibles": res_model}
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


        os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://0.0.0.0:9000"
        os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'

        mlflow.set_tracking_uri("http://0.0.0.0:5000")

        model_name = input_data.model
        model_production_uri = "models:/{model_name}/production".format(model_name=model_name)

        # Load model as a PyFuncModel.
        loaded_model = mlflow.pyfunc.load_model(model_uri=model_production_uri)

        # Prediccion del modelo
        predict = loaded_model.predict(data)
        resultado = predict[0]

        return {"prediction": resultado}
    except Exception as e:
        return {"prediction": f"Error al cargar el modelo: {e}"}

    