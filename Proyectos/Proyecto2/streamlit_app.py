import streamlit as st
import requests

# URL base de la API desplegada en el contenedor
API_URL = "http://localhost:8989"

st.title("Proyecto 2 - Modelo Covertype")

# Sección para listar modelos disponibles
st.header("Modelos Disponibles")
try:
    response = requests.get(f"{API_URL}/listar_modelos")
    if response.status_code == 200:
        data = response.json()
        modelos = data.get("modelos_disponibles", [])
        if modelos:
            st.write("Seleccione uno de los modelos desplegados en mlflow, los cuales se encuentran disponibles en la siguiente lista")
            selected_model = st.selectbox("Modelos", modelos)
        else:
            st.error("No se encontraron modelos disponibles.")
    else:
        st.error(f"Error al obtener modelos: {response.text}")
except Exception as e:
    st.error(f"Error en la conexión con la API: {e}")

# Sección para realizar la predicción
st.header("Realizar Predicción")

with st.form("predict_form"):
    st.subheader("Ingrese los datos para la predicción")
    
    col1, col2 = st.columns(2)

    # Primera columna
    with col1:
        elevation = st.number_input("Elevation", value=0, step=1)
        st.caption("Elevación en metros sobre el nivel del mar")

        aspect = st.number_input("Aspect", value=0, step=1)
        st.caption("Orientación del terreno en grados azimuth")

        slope = st.number_input("Slope", value=0, step=1)
        st.caption("Inclinación del terreno en grados")

        horizontal_distance_to_hydrology = st.number_input("Horizontal_Distance_To_Hydrology.", value=0, step=1)
        st.caption("Distancia horizontal en metros a la fuente de agua más cercana")

        vertical_distance_to_hydrology = st.number_input("Vertical_Distance_To_Hydrology.", value=0, step=1)
        st.caption("Distancia vertical en metros a la fuente de agua más cercana")

    # Segunda columna
    with col2:
        horizontal_distance_to_roadways = st.number_input("Horizontal_Distance_To_Roadways.", value=0, step=1)
        st.caption("Distancia horizontal en metros a la carretera más cercana")

        hillshade_9am = st.number_input("Hillshade_9am", value=0, step=1)
        st.caption("Índice de sombra a las 9 AM")

        hillshade_noon = st.number_input("Hillshade_Noon", value=0, step=1)
        st.caption("Índice de sombra al mediodía")

        hillshade_3pm = st.number_input("Hillshade_3pm", value=0, step=1)
        st.caption("Índice de sombra a las 3 PM.")

        horizontal_distance_to_fire_points = st.number_input("Horizontal_Distance_To_Fire_Points", value=0, step=1)
        st.caption("Distancia horizontal en metros a puntos de incendios cercanos")

    # Campos de texto
    wilderness_area = st.text_input("Wilderness_Area", value="")
    st.caption("Área silvestre")

    soil_type = st.text_input("Soil_Type", value="")
    st.caption("Tipo de suelo")

    submitted = st.form_submit_button("Predecir")
    
    if submitted:
        # 1. Validación de campos de texto no vacíos
        if wilderness_area.strip() == "" or soil_type.strip() == "":
            st.error("Por favor, complete la información para Wilderness_Area y Soil_Type antes de predecir.")
            st.stop()

        # 2. Validación de rangos numéricos
        if elevation < 0:
            st.error("Elevation debe ser >= 0.")
            st.stop()
        
        # Aspect típicamente 0 a 360
        if aspect < 0:
            st.error("Aspect debe ser >= 0.")
            st.stop()
        
        if slope < 0:
            st.error("Slope debe ser >= 0.")
            st.stop()
        
        if horizontal_distance_to_hydrology < 0:
            st.error("Horizontal_Distance_To_Hydrology debe ser >= 0.")
            st.stop()
        
        if vertical_distance_to_hydrology < 0:
            st.error("Vertical_Distance_To_Hydrology debe ser >= 0.")
            st.stop()
        
        if horizontal_distance_to_roadways < 0:
            st.error("Horizontal_Distance_To_Roadways debe ser >= 0.")
            st.stop()
        
        # Hillshade en rango 0 a 255
        if not (0 <= hillshade_9am <= 255):
            st.error("Hillshade_9am debe estar entre 0 y 255.")
            st.stop()
        
        if not (0 <= hillshade_noon <= 255):
            st.error("Hillshade_Noon debe estar entre 0 y 255.")
            st.stop()
        
        if not (0 <= hillshade_3pm <= 255):
            st.error("Hillshade_3pm debe estar entre 0 y 255.")
            st.stop()
        
        if horizontal_distance_to_fire_points < 0:
            st.error("Horizontal_Distance_To_Fire_Points debe ser >= 0.")
            st.stop()

        # Si todas las validaciones se cumplen, armamos el payload
        payload = {
            "Elevation": elevation,
            "Aspect": aspect,
            "Slope": slope,
            "Horizontal_Distance_To_Hydrology": horizontal_distance_to_hydrology,
            "Vertical_Distance_To_Hydrology": vertical_distance_to_hydrology,
            "Horizontal_Distance_To_Roadways": horizontal_distance_to_roadways,
            "Hillshade_9am": hillshade_9am,
            "Hillshade_Noon": hillshade_noon,
            "Hillshade_3pm": hillshade_3pm,
            "Horizontal_Distance_To_Fire_Points": horizontal_distance_to_fire_points,
            "Wilderness_Area": wilderness_area,   
            "Soil_Type": soil_type,               
            "model": selected_model
        }
        
        # Llamada a la API
        try:
            pred_response = requests.post(f"{API_URL}/predict", json=payload)
            if pred_response.status_code == 200:
                result = pred_response.json()
                st.success(f"Predicción: {result.get('prediction', 'No se obtuvo predicción.')}")
            else:
                st.error(f"Error en la predicción: {pred_response.text}")
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")
