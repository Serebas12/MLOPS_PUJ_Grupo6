from fastapi import FastAPI, Response
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
import os
import mlflow
import boto3
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import psycopg2
import pytz
from datetime import datetime

#Inicia la aplicación
app = FastAPI(
    title="Predictor API – ML Model Serving",
    description="Realizar predicciones usando el modelo más reciente en stage Production",
    version="1.0.0"
)

# Métricas Prometheus
REQUEST_COUNT = Counter('predict_requests_total', 'Total de peticiones de predicción')

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
class ModelInput(BaseModel):
    island: str	
    culmen_length_mm: float	
    culmen_depth_mm: float
    flipper_length_mm: float	
    body_mass_g: float	
    sex: str
    model: str	

#Se genera el decorador por modelo
@app.post("/predict")

async def predict(input_data: ModelInput):

    """
    Puede realizar la predicción de la especie de un pingüino, seleccionando uno de los modelos pre entrenados.

    Devuelve un JSON con la predicción.
    """

    ### Predicción modelo 1

    REQUEST_COUNT.inc()

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


        # # --- Guardar en la base de datos postgres ---
        # try:
        #     # Conexión a la base de datos PostgreSQL
        #     connection = psycopg2.connect(
        #         host='mlops-postgres',
        #         database='datadb',
        #         user='admin',
        #         password='supersecret'
        #     )

        #     cursor = connection.cursor()

        #     insert_query = """
        #         INSERT INTO resultados_modelo (island, culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g, sex, model, created_at)
        #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        #     """

        #     # Obtener la hora actual en zona horaria Colombia
        #     colombia_timezone = pytz.timezone("America/Bogota")
        #     created_at_colombia = datetime.now(colombia_timezone)
        #     created_at_utc = created_at_colombia.astimezone(pytz.utc)


        #     values = (
        #         input_data.island,
        #         input_data.culmen_length_mm,
        #         input_data.culmen_depth_mm,
        #         input_data.flipper_length_mm,
        #         input_data.body_mass_g,
        #         input_data.sex,
        #         input_data.model,
        #         created_at_utc
        #     )

        #     cursor.execute(insert_query, values)
        #     connection.commit()

        # except Exception as e:
        #     print(f"Error al guardar en la base de datos: {e}")

        # finally:
        #     if connection:
        #         cursor.close()
        #         connection.close()

        return {"prediction": resultado}
    except Exception as e:
        return {"prediction": f"Error al cargar el modelo: {e}"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)    