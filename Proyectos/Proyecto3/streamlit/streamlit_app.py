import streamlit as st
import requests

API_URL = "http://fast-api:8989"
DEFAULT_MODEL = "DiabetesReadmissionModel"   

st.title("Proyecto 3")

# ──────────────────────────────
# Ingreso de datos para predicción
# ──────────────────────────────
st.header("Ingreso de datos")

numeric_fields = [
    "encounter_id", "patient_nbr", "admission_type_id", "discharge_disposition_id",
    "admission_source_id", "time_in_hospital", "num_lab_procedures",
    "num_procedures", "num_medications", "number_outpatient", "number_emergency",
    "number_inpatient", "number_diagnoses"
]

text_fields = [
    "race", "gender", "age", "weight", "payer_code", "medical_specialty",
    "diag_1", "diag_2", "diag_3", "max_glu_serum", "a1cresult", "metformin",
    "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
    "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
    "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide",
    "examide", "citoglipton", "insulin", "glyburide-metformin",
    "glipizide-metformin", "glimepiride-pioglitazone",
    "metformin-rosiglitazone", "metformin-pioglitazone", "change", "diabetesmed"
]

with st.form("prediction_form"):
    numeric_values = {}
    text_values = {}

    # Campos numéricos (2 por fila)
    for i in range(0, len(numeric_fields), 2):
        c1, c2 = st.columns(2)
        for col, field in zip((c1, c2), numeric_fields[i:i+2]):
            numeric_values[field] = col.number_input(
                field.replace("_", " ").title(), min_value=0, value=0, step=1
            )

    # Campos de texto (2 por fila)
    for i in range(0, len(text_fields), 2):
        c1, c2 = st.columns(2)
        for col, field in zip((c1, c2), text_fields[i:i+2]):
            text_values[field] = col.text_input(
                field.replace("_", " ").title(), value=""
            )

    submit_button = st.form_submit_button("Realizar predicción")

# ──────────────────────────────
# Enviar y mostrar resultado
# ──────────────────────────────
if submit_button:
    payload = {
        **numeric_values,
        **text_values,
        "model": DEFAULT_MODEL           
    }

    r = requests.post(f"{API_URL}/predict", json=payload)

    if r.status_code == 200:
        prediction = r.json().get("prediction", "Sin resultado")
        st.success(f"Predicción: {prediction}")
    else:
        st.error("Error al realizar la predicción.")
