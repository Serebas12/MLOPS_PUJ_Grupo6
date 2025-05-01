from locust import HttpUser, task, between

class UsuarioDeCarga(HttpUser):
    wait_time = between(1, 2.5)
    #host = "http://inference:8989"

    @task
    def hacer_inferencia(self):
        payload = {
            "Elevation": 2723,
            "Aspect": 127,
            "Slope": 16,
            "Horizontal_Distance_To_Hydrology": 190,
            "Vertical_Distance_To_Hydrology": 69,
            "Horizontal_Distance_To_Roadways": 1560,
            "Hillshade_9am": 245,
            "Hillshade_Noon": 228,
            "Hillshade_3pm": 108,
            "Horizontal_Distance_To_Fire_Points": 845,
            "Wilderness_Area": "Rawah",
            "Soil_Type": "C7746",
            "model": "modelo_covertype_vf"
        }
        # Enviar una petición POST al endpoint /predict
        response = self.client.post("/predict", json=payload)
        # Opcional: validación de respuesta
        if response.status_code != 200:
            print("❌ Error en la inferencia:", response.text)
