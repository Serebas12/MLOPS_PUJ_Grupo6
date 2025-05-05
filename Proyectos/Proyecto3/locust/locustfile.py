from locust import HttpUser, task, between
import random

class DiabetesUser(HttpUser):
    wait_time = between(1, 2.5)

    # Listas de valores válidos para variables categóricas
    races = ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other", "?"]
    genders = ["Male", "Female", "Unknown/Invalid"]
    ages = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]
    glu = ["None", "Norm", ">200", ">300"]
    a1c = ["None", "Norm", ">7", ">8"]
    meds4 = ["No", "Steady", "Up", "Down"]
    yesno = ["Yes", "No"]
    # aliases con guiones
    alias_meds = {
        "glyburide-metformin": meds4,
        "glipizide-metformin": meds4,
        "glimepiride-pioglitazone": meds4,
        "metformin-rosiglitazone": meds4,
        "metformin-pioglitazone": meds4,
    }

    @task
    def predict(self):
        payload = {
            "encounter_id": 0,
            "patient_nbr": random.randint(100000, 999999),
            "race": random.choice(self.races),
            "gender": random.choice(self.genders),
            "age": random.choice(self.ages),
            "weight": random.choice(["?", str(random.randint(45, 120))]),
            "admission_type_id": random.randint(1, 8),
            "discharge_disposition_id": random.randint(1, 30),
            "admission_source_id": random.randint(1, 25),
            "time_in_hospital": random.randint(1, 14),
            "payer_code": random.choice([None, "MCG", "Medicare", "Private"]),
            "medical_specialty": random.choice([None, "Cardiology", "InternalMedicine", "Surgery", "Orthopedics"]),
            "num_lab_procedures": random.randint(1, 100),
            "num_procedures": random.randint(0, 6),
            "num_medications": random.randint(1, 30),
            "number_outpatient": random.randint(0, 10),
            "number_emergency": random.randint(0, 5),
            "number_inpatient": random.randint(0, 5),
            "diag_1": f"{random.randint(1, 999)}.{random.randint(0,99):02d}",
            "diag_2": None,
            "diag_3": None,
            "number_diagnoses": random.randint(1, 10),
            "max_glu_serum": random.choice(self.glu),
            "a1cresult": random.choice(self.a1c),
            "metformin": random.choice(self.meds4),
            "repaglinide": random.choice(self.meds4),
            "nateglinide": random.choice(self.meds4),
            "chlorpropamide": random.choice(self.meds4),
            "glimepiride": random.choice(self.meds4),
            "acetohexamide": random.choice(self.meds4),
            "glipizide": random.choice(self.meds4),
            "glyburide": random.choice(self.meds4),
            "tolbutamide": random.choice(self.meds4),
            "pioglitazone": random.choice(self.meds4),
            "rosiglitazone": random.choice(self.meds4),
            "acarbose": random.choice(self.meds4),
            "miglitol": random.choice(self.meds4),
            "troglitazone": random.choice(self.meds4),
            "tolazamide": random.choice(self.meds4),
            "examide": random.choice(self.meds4),
            "citoglipton": random.choice(self.meds4),
            "insulin": random.choice(self.meds4),
            "change": random.choice(["No", "Ch"]),
            "diabetesmed": random.choice(self.yesno),
        }

        # añadir dinámicamente los aliases con guiones
        for alias, choices in self.alias_meds.items():
            payload[alias] = random.choice(choices)

        response = self.client.post("/predict", json=payload)
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
