import streamlit as st
import requests

# URL base de tu API (ajustar si estás en local o diferente URL)
API_URL = "http://fast-api:8989"

st.title("Proyecto 3")

# Paso 1: Obtener la lista de modelos disponibles
st.header("1. Selección de modelo")

# Inicializar session_state si no existe
if "modelos" not in st.session_state:
    response = requests.get(f"{API_URL}/listar_modelos")
    if response.status_code == 200:
        st.session_state.modelos = response.json().get("modelos_disponibles", [])
    else:
        st.session_state.modelos = []

# Botón para actualizar lista de modelos
if st.button("Actualizar lista de modelos"):
    response = requests.get(f"{API_URL}/listar_modelos")
    if response.status_code == 200:
        st.session_state.modelos = response.json().get("modelos_disponibles", [])
    else:
        st.error("No se pudieron listar los modelos disponibles.")

# Mostrar los modelos disponibles con un modelo seleccionado por defecto
definir_modelo = st.selectbox(
    "Selecciona un modelo:",
    options=st.session_state.get("modelos", []),
    index=0 if st.session_state.get("modelos") else None
)

# Paso 2: Formulario para predicción
st.header("2. Ingreso de datos para predicción")

with st.form("prediction_form"):
    island = st.selectbox("Isla", options=["Biscoe", "Dream", "Torgersen"])
    sex = st.selectbox("Sexo", options=["MALE", "FEMALE"])
    culmen_length_mm = st.number_input("Longitud del culmen (mm)", min_value=0.0)
    culmen_depth_mm = st.number_input("Profundidad del culmen (mm)", min_value=0.0)
    flipper_length_mm = st.number_input("Longitud de la aleta (mm)", min_value=0.0)
    body_mass_g = st.number_input("Masa corporal (g)", min_value=0.0)
    
    submit_button = st.form_submit_button("Realizar predicción")

# Al enviar el formulario
if submit_button:
    if not definir_modelo:
        st.error("Por favor selecciona un modelo antes de predecir.")
    else:
        # Construimos el payload
        payload = {
            "island": island,
            "sex": sex,
            "culmen_length_mm": culmen_length_mm,
            "culmen_depth_mm": culmen_depth_mm,
            "flipper_length_mm": flipper_length_mm,
            "body_mass_g": body_mass_g,
            "model": definir_modelo
        }

        # Llamamos al API de predicción
        response = requests.post(f"{API_URL}/predict", json=payload)

        if response.status_code == 200:
            prediction = response.json().get("prediction", "Sin resultado")
            st.success(f"Predicción: {prediction}")
        else:
            st.error("Error al realizar la predicción.")
