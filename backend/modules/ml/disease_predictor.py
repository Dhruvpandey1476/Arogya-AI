import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Full 132-symptom list from Kaggle disease-symptom dataset
SYMPTOMS = [
    "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering",
    "chills", "joint_pain", "stomach_pain", "acidity", "ulcers_on_tongue", "muscle_wasting",
    "vomiting", "burning_micturition", "spotting_urination", "fatigue", "weight_gain",
    "anxiety", "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness",
    "lethargy", "patches_in_throat", "irregular_sugar_level", "cough", "high_fever",
    "sunken_eyes", "breathlessness", "sweating", "dehydration", "indigestion", "headache",
    "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "pain_behind_the_eyes",
    "back_pain", "constipation", "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
    "yellowing_of_eyes", "acute_liver_failure", "fluid_overload", "swelling_of_stomach",
    "swelled_lymph_nodes", "malaise", "blurred_and_distorted_vision", "phlegm",
    "throat_irritation", "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion",
    "chest_pain", "weakness_in_limbs", "fast_heart_rate", "pain_during_bowel_movements",
    "pain_in_anal_region", "bloody_stool", "irritation_in_anus", "neck_pain", "dizziness",
    "cramps", "bruising", "obesity", "swollen_legs", "swollen_blood_vessels",
    "puffy_face_and_eyes", "enlarged_thyroid", "brittle_nails", "swollen_extremeties",
    "excessive_hunger", "extra_marital_contacts", "drying_and_tingling_lips", "slurred_speech",
    "knee_pain", "hip_joint_pain", "muscle_weakness", "stiff_neck", "swelling_joints",
    "movement_stiffness", "spinning_movements", "loss_of_balance", "unsteadiness",
    "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort", "foul_smell_of_urine",
    "continuous_feel_of_urine", "passage_of_gases", "internal_itching", "toxic_look_(typhos)",
    "depression", "irritability", "muscle_pain", "altered_sensorium", "red_spots_over_body",
    "belly_pain", "abnormal_menstruation", "dischromic_patches", "watering_from_eyes",
    "increased_appetite", "polyuria", "family_history", "mucoid_sputum", "rusty_sputum",
    "lack_of_concentration", "visual_disturbances", "receiving_blood_transfusion",
    "receiving_unsterile_injections", "coma", "stomach_bleeding", "distention_of_abdomen",
    "history_of_alcohol_consumption", "fluid_overload.1", "blood_in_sputum",
    "prominent_veins_on_calf", "palpitations", "painful_walking", "pus_filled_pimples",
    "blackheads", "scurring", "skin_peeling", "silver_like_dusting", "small_dents_in_nails",
    "inflammatory_nails", "blister", "red_sore_around_nose", "yellow_crust_ooze",
]

DISEASE_DESCRIPTIONS = {
    "Fungal infection": "A skin or systemic infection caused by fungi, often presenting with itching and rashes.",
    "Allergy": "An immune response to allergens causing symptoms like sneezing, rash, or breathing difficulties.",
    "GERD": "Gastroesophageal reflux disease causing stomach acid to flow back into the esophagus.",
    "Chronic cholestasis": "A liver condition where bile flow is reduced or stopped.",
    "Drug Reaction": "An adverse reaction to medication, ranging from mild to severe.",
    "Peptic ulcer disease": "Sores in the stomach lining or upper small intestine.",
    "AIDS": "Advanced HIV infection severely damaging the immune system.",
    "Diabetes": "A metabolic disease causing high blood sugar due to insulin issues.",
    "Gastroenteritis": "Inflammation of the stomach and intestines, often from infection.",
    "Bronchial Asthma": "A respiratory condition causing airways to narrow and swell.",
    "Hypertension": "High blood pressure that can damage blood vessels and organs over time.",
    "Migraine": "A neurological condition causing severe recurring headaches.",
    "Cervical spondylosis": "Age-related wear affecting spinal disks in the neck.",
    "Paralysis (brain hemorrhage)": "Loss of movement caused by bleeding in the brain.",
    "Jaundice": "A condition where skin and eyes turn yellow due to excess bilirubin.",
    "Malaria": "A mosquito-borne disease caused by Plasmodium parasites.",
    "Chicken pox": "A highly contagious viral infection causing an itchy blister rash.",
    "Dengue": "A mosquito-borne tropical disease causing fever and joint pain.",
    "Typhoid": "A bacterial infection spread through contaminated food or water.",
    "Hepatitis A": "A viral liver infection spread through contaminated food/water.",
    "Hepatitis B": "A serious viral liver infection that can become chronic.",
    "Hepatitis C": "A viral infection causing liver inflammation, sometimes serious.",
    "Hepatitis D": "A liver infection that only occurs with hepatitis B.",
    "Hepatitis E": "A liver disease caused by the Hepatitis E virus.",
    "Alcoholic hepatitis": "Liver inflammation from excessive alcohol consumption.",
    "Tuberculosis": "A serious infectious disease primarily affecting the lungs.",
    "Common Cold": "A viral infection of the upper respiratory tract.",
    "Pneumonia": "An infection inflaming the air sacs in one or both lungs.",
    "Dimorphic hemorrhoids (piles)": "Swollen veins in the rectum or anus causing discomfort.",
    "Heart attack": "A blockage of blood flow to the heart muscle.",
    "Varicose veins": "Twisted, enlarged veins usually in legs due to poor blood flow.",
    "Hypothyroidism": "Underactive thyroid gland not producing enough hormones.",
    "Hyperthyroidism": "Overactive thyroid gland producing too much hormone.",
    "Hypoglycemia": "Abnormally low blood sugar levels.",
    "Osteoarthritis": "Degeneration of joint cartilage causing pain and stiffness.",
    "Arthritis": "Inflammation of one or more joints causing pain and stiffness.",
    "(Vertigo) Paroxysmal Positional Vertigo": "A condition causing brief episodes of dizziness.",
    "Acne": "A skin condition causing pimples, blackheads, and whiteheads.",
    "Urinary tract infection": "An infection in any part of the urinary system.",
    "Psoriasis": "A skin disease causing red, itchy scaly patches.",
    "Impetigo": "A highly contagious skin infection causing sores and blisters.",
}


class DiseasePredictor:
    def __init__(self, model_path: Path):
        with open(model_path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.label_encoder = data["label_encoder"]
            self.feature_names = data.get("feature_names", SYMPTOMS)
        logger.info(f"Disease predictor loaded from {model_path}")

    def _encode_symptoms(self, symptoms: List[str]) -> np.ndarray:
        """Convert symptom list to binary feature vector."""
        # Normalize symptom names
        normalized = [s.lower().replace(" ", "_") for s in symptoms]
        vector = np.zeros(len(self.feature_names))
        for i, feat in enumerate(self.feature_names):
            if feat in normalized:
                vector[i] = 1
        return vector.reshape(1, -1)

    def predict(self, symptoms: List[str], top_k: int = 3) -> List[Dict]:
        """Predict top-k diseases from symptoms."""
        X = self._encode_symptoms(symptoms)

        # Get class probabilities
        proba = self.model.predict_proba(X)[0]
        top_indices = np.argsort(proba)[::-1][:top_k]

        results = []
        for idx in top_indices:
            disease_name = self.label_encoder.inverse_transform([idx])[0]
            confidence = round(float(proba[idx]) * 100, 1)
            results.append({
                "name": disease_name,
                "confidence": confidence,
                "description": DISEASE_DESCRIPTIONS.get(disease_name, "A medical condition requiring professional evaluation."),
            })
        return results


def get_all_symptoms() -> List[str]:
    return SYMPTOMS
