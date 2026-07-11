import pickle
import numpy as np
from pathlib import Path
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

SEVERITY_LEVELS = ["Low", "Medium", "High", "Emergency"]

# Symptoms that increase severity
HIGH_RISK_SYMPTOMS = {
    "chest_pain", "breathlessness", "coma", "paralysis", "stomach_bleeding",
    "altered_sensorium", "weakness_of_one_body_side", "slurred_speech",
    "loss_of_balance", "acute_liver_failure", "fast_heart_rate"
}

MEDIUM_RISK_SYMPTOMS = {
    "high_fever", "vomiting", "diarrhoea", "dehydration", "yellowish_skin",
    "yellowing_of_eyes", "stiff_neck", "severe_headache", "neck_pain"
}


class SeverityClassifier:
    def __init__(self, model_path: Path):
        with open(model_path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.feature_names = data.get("feature_names", [])
        logger.info(f"Severity classifier loaded from {model_path}")

    def predict(
        self,
        symptoms: List[str],
        duration_days: int,
        pain_scale: int,
        fever: bool,
        fever_temp: Optional[float],
        age: int,
    ) -> str:
        features = self._build_features(symptoms, duration_days, pain_scale, fever, fever_temp, age)
        prediction = self.model.predict(features)[0]
        return SEVERITY_LEVELS[int(prediction)]

    def _build_features(self, symptoms, duration_days, pain_scale, fever, fever_temp, age):
        normalized_symptoms = set(s.lower().replace(" ", "_") for s in symptoms)

        high_risk_count = len(normalized_symptoms & HIGH_RISK_SYMPTOMS)
        medium_risk_count = len(normalized_symptoms & MEDIUM_RISK_SYMPTOMS)
        symptom_count = len(symptoms)
        fever_flag = int(fever)
        fever_val = fever_temp if fever_temp else 37.0
        elderly = int(age >= 65)
        child = int(age <= 12)

        return np.array([[
            pain_scale, duration_days, symptom_count,
            high_risk_count, medium_risk_count,
            fever_flag, fever_val,
            elderly, child,
        ]])


def rule_based_severity(
    symptoms: List[str],
    duration_days: int,
    pain_scale: int,
    fever: bool,
    fever_temp: Optional[float],
    age: int,
) -> str:
    """Fallback when model not available."""
    normalized = set(s.lower().replace(" ", "_") for s in symptoms)

    if pain_scale >= 9 or normalized & {"chest_pain", "breathlessness", "coma", "altered_sensorium"}:
        return "Emergency"

    if (fever and fever_temp and fever_temp > 103) or pain_scale >= 7:
        return "High"

    if duration_days > 7 or pain_scale >= 5 or normalized & MEDIUM_RISK_SYMPTOMS:
        return "Medium"

    return "Low"
