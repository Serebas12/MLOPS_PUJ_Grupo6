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
    title="Covertype Predictor API – ML Model Serving",
    description="Realizar predicciones usando el modelo más reciente en stage Production",
    version="1.0.0"
)

#Se genera decorador para listar los modelos 

MODEL_DIR = "/app/models/"

@app.get("/listar_modelos")

async def list_models():
    """
    Rastrea el modelo más reciente para su utilización.
    """

# Configurar la URL del servidor de MLflow (ajusta según tu caso)
    try:
        mlflow.set_tracking_uri("http://mlflow:5000") 

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
class CoverTypeInput(BaseModel):
    Elevation: float
    Aspect: float
    Slope: float
    Horizontal_Distance_To_Hydrology: float
    Vertical_Distance_To_Hydrology: float
    Horizontal_Distance_To_Roadways: float
    Hillshade_9am: float
    Hillshade_Noon: float
    Hillshade_3pm: float
    Horizontal_Distance_To_Fire_Points: float
    Wilderness_Area: str
    Soil_Type: str
    model: str

#Se genera el decorador por modelo
@app.post("/predict")

async def predict(input_data: CoverTypeInput):

    """
    Puede realizar la predicción del tipo de cobertura forestal (Cover_Type) utilizando uno de los modelos preentrenados registrados en MLflow.

    -   Elevation: Elevación del terreno en metros.
    -   Aspect: Orientación del terreno en grados (0 a 360).
    -   Slope: Inclinación del terreno en grados.
    -   Horizontal_Distance_To_Hydrology: Distancia horizontal a cuerpos de agua en metros.
    -   Vertical_Distance_To_Hydrology: Distancia vertical a cuerpos de agua en metros.
    -   Horizontal_Distance_To_Roadways: Distancia horizontal a carreteras en metros.
    -   Hillshade_9am: Nivel de sombra proyectada a las 9:00 AM (0 a 255).
    -   Hillshade_Noon: Nivel de sombra proyectada al mediodía (0 a 255).
    -   Hillshade_3pm: Nivel de sombra proyectada a las 3:00 PM (0 a 255).
    -   Horizontal_Distance_To_Fire_Points: Distancia horizontal a zonas de fuego controlado en metros.
    -   Wilderness_Area: Área silvestre a la que pertenece. Valores válidos: Rawah, Neota, Comanche Peak, Cache la Poudre.  
    -   Soil_Type: Tipo de suelo categorizado. Valores válidos: Soil_1 a Soil_40.
    -   model: Modelo que se desea utilizar para la predicción. 

    Devuelve un JSON con la clase de cobertura forestal estimada (Cover_Type), codificada del 1 al 7 según la clasificación del Servicio Forestal de EE.UU.
    """

    ### Predicción modelo 1

    try:
        # Tratamiento de información
        data = pd.DataFrame([{
            'Elevation': int(input_data.Elevation), 
            'Aspect': int(input_data.Aspect), 
            'Slope': int(input_data.Slope), 
            'Horizontal_Distance_To_Hydrology': int(input_data.Horizontal_Distance_To_Hydrology),
            'Vertical_Distance_To_Hydrology': int(input_data.Vertical_Distance_To_Hydrology), 
            'Horizontal_Distance_To_Roadways': int(input_data.Horizontal_Distance_To_Roadways),
            'Hillshade_9am': int(input_data.Hillshade_9am), 
            'Hillshade_Noon': int(input_data.Hillshade_Noon), 
            'Hillshade_3pm': int(input_data.Hillshade_3pm),
            'Horizontal_Distance_To_Fire_Points': int(input_data.Horizontal_Distance_To_Fire_Points), 
            'Wilderness_Area': input_data.Wilderness_Area, 
            'Soil_Type': input_data.Soil_Type
        }])


        os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
        os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'

        mlflow.set_tracking_uri("http://mlflow:5000")

        model_name = input_data.model
        model_production_uri = "models:/{model_name}/production".format(model_name=model_name)

        # Load model as a PyFuncModel.
        loaded_model = mlflow.pyfunc.load_model(model_uri=model_production_uri)

        # Prediccion del modelo
        predict = loaded_model.predict(data)
        resultado = predict[0]

        resultado = int(resultado)

        return {"prediction": resultado}
    except Exception as e:
        return {"prediction": f"Error al cargar el modelo: {e}"}

    