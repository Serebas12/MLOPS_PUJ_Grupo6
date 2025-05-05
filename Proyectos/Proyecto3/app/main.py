from fastapi import FastAPI, Response, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import os
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import psycopg2
import pytz
from datetime import datetime

app = FastAPI(
    title="Predictor API – ML Model Serving: Diabetes Readmission",
    description="Realizar predicciones usando el modelo más reciente en stage Production",
    version="1.0.0"
)

REQUEST_COUNT = Counter('predict_requests_total', 'Total de peticiones de predicción')
POSTGRES_URI = os.getenv("POSTGRES_URI")


class PatientData(BaseModel):
    encounter_id: int = Field(..., description="ID único del encuentro (usar 0 para pruebas)")
    patient_nbr: int = Field(..., description="ID del paciente")
    race: Optional[str]
    gender: str
    age: str
    weight: Optional[str]
    admission_type_id: int
    discharge_disposition_id: int
    admission_source_id: int
    time_in_hospital: int
    payer_code: Optional[str] = None
    medical_specialty: Optional[str] = None
    num_lab_procedures: int
    num_procedures: int
    num_medications: int
    number_outpatient: int
    number_emergency: int
    number_inpatient: int
    diag_1: str
    diag_2: Optional[str] = None
    diag_3: Optional[str] = None
    number_diagnoses: int
    max_glu_serum: str
    a1cresult: str
    metformin: str
    repaglinide: str
    nateglinide: str
    chlorpropamide: str
    glimepiride: str
    acetohexamide: str
    glipizide: str
    glyburide: str
    tolbutamide: str
    pioglitazone: str
    rosiglitazone: str
    acarbose: str
    miglitol: str
    troglitazone: str
    tolazamide: str
    examide: str
    citoglipton: str
    insulin: str
    glyburide_metformin: str = Field(..., alias="glyburide-metformin")
    glipizide_metformin: str = Field(..., alias="glipizide-metformin")
    glimepiride_pioglitazone: str = Field(..., alias="glimepiride-pioglitazone")
    metformin_rosiglitazone: str = Field(..., alias="metformin-rosiglitazone")
    metformin_pioglitazone: str = Field(..., alias="metformin-pioglitazone")
    change: str
    diabetesmed: str

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


def log_to_db(data: PatientData, prediction: str, model_version: str):
    """Inserta en raw_data.patient_predictions (sin la columna readmitted)"""
    conn = cur = None
    try:
        conn = psycopg2.connect(POSTGRES_URI)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_data.patient_predictions (
                encounter_id                INT,
                patient_nbr                 INT,
                race                        TEXT,
                gender                      TEXT,
                age                         TEXT,
                weight                      TEXT,
                admission_type_id           INT,
                discharge_disposition_id    INT,
                admission_source_id         INT,
                time_in_hospital            INT,
                payer_code                  TEXT,
                medical_specialty           TEXT,
                num_lab_procedures          INT,
                num_procedures              INT,
                num_medications             INT,
                number_outpatient           INT,
                number_emergency            INT,
                number_inpatient            INT,
                diag_1                      TEXT,
                diag_2                      TEXT,
                diag_3                      TEXT,
                number_diagnoses            INT,
                max_glu_serum               TEXT,
                a1cresult                   TEXT,
                metformin                   TEXT,
                repaglinide                 TEXT,
                nateglinide                 TEXT,
                chlorpropamide              TEXT,
                glimepiride                 TEXT,
                acetohexamide               TEXT,
                glipizide                   TEXT,
                glyburide                   TEXT,
                tolbutamide                 TEXT,
                pioglitazone                TEXT,
                rosiglitazone               TEXT,
                acarbose                    TEXT,
                miglitol                    TEXT,
                troglitazone                TEXT,
                tolazamide                  TEXT,
                examide                     TEXT,
                citoglipton                 TEXT,
                insulin                     TEXT,
                glyburide_metformin         TEXT,
                glipizide_metformin         TEXT,
                glimepiride_pioglitazone    TEXT,
                metformin_rosiglitazone     TEXT,
                metformin_pioglitazone      TEXT,
                change                      TEXT,
                diabetesmed                 TEXT,
                prediction                  TEXT,
                model_version               TEXT,
                executed_at                 TIMESTAMPTZ
            );
        """)
        payload = data.dict(by_alias=False)
        cols = list(payload.keys()) + ["prediction", "model_version", "executed_at"]
        vals = list(payload.values()) + [
            prediction,
            model_version,
            datetime.now(pytz.timezone("America/Bogota"))
        ]
        ph = ", ".join(["%s"] * len(vals))
        cur.execute(
            f"INSERT INTO raw_data.patient_predictions ({', '.join(cols)}) VALUES ({ph});",
            vals
        )
        conn.commit()
    except Exception as e:
        print(f"[log_to_db] Error al insertar: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()



@app.post("/predict")
async def predict(input_data: PatientData, bg: BackgroundTasks):
    REQUEST_COUNT.inc()

    # 1) Armar DataFrame
    try:
        payload = input_data.dict(by_alias=False)
        df = pd.DataFrame([payload])
    except Exception as e:
        return {"error": f"Error construyendo DataFrame: {e}"}

    # 2) Obtener versión en producción y cargar modelo
    try:
        client = MlflowClient(tracking_uri="http://mlflow:5000")
        prod_versions = client.get_latest_versions("DiabetesReadmissionModel", stages=["Production"])
        if not prod_versions:
            return {"error": "No hay modelo en stage Production"}
        model_version = str(prod_versions[0].version)
        model_uri = f"models:/DiabetesReadmissionModel/Production"
        pyfunc_model = mlflow.pyfunc.load_model(model_uri)
    except Exception as e:
        return {"error": f"Error cargando modelo: {e}"}

    # 3) Predecir
    try:
        resultado = pyfunc_model.predict(df)[0]
    except Exception as e:
        return {"error": f"Error en predicción: {e}"}

    # 4) Log en background si no es prueba
    if input_data.encounter_id != 0:
        bg.add_task(log_to_db, input_data, str(resultado), model_version)

    return {
        "prediction": resultado 
        #"model_uri": model_uri,
        #"model_version": model_version
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
