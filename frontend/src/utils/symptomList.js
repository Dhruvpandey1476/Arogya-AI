export const SYMPTOM_CATEGORIES = {
  "General": [
    "fatigue", "weight_loss", "weight_gain", "lethargy", "malaise",
    "restlessness", "anxiety", "mood_swings", "high_fever", "mild_fever",
    "sweating", "shivering", "chills", "dehydration",
  ],
  "Head & Neurological": [
    "headache", "dizziness", "loss_of_balance", "spinning_movements",
    "unsteadiness", "stiff_neck", "neck_pain", "slurred_speech",
    "altered_sensorium", "weakness_of_one_body_side", "visual_disturbances",
    "blurred_and_distorted_vision", "pain_behind_the_eyes", "loss_of_smell",
    "lack_of_concentration",
  ],
  "Respiratory": [
    "cough", "breathlessness", "phlegm", "mucoid_sputum", "rusty_sputum",
    "blood_in_sputum", "throat_irritation", "runny_nose", "congestion",
    "sinus_pressure", "continuous_sneezing", "patches_in_throat",
  ],
  "Chest & Heart": [
    "chest_pain", "fast_heart_rate", "palpitations",
  ],
  "Digestive": [
    "nausea", "vomiting", "diarrhoea", "constipation", "indigestion",
    "acidity", "stomach_pain", "abdominal_pain", "belly_pain",
    "loss_of_appetite", "increased_appetite", "passage_of_gases",
    "swelling_of_stomach", "distention_of_abdomen", "stomach_bleeding",
    "internal_itching",
  ],
  "Skin": [
    "itching", "skin_rash", "nodal_skin_eruptions", "yellowish_skin",
    "red_spots_over_body", "dischromic_patches", "pus_filled_pimples",
    "blackheads", "skin_peeling", "silver_like_dusting", "blister",
    "red_sore_around_nose", "yellow_crust_ooze", "bruising",
  ],
  "Eyes": [
    "redness_of_eyes", "watering_from_eyes", "yellowing_of_eyes",
    "sunken_eyes", "puffy_face_and_eyes",
  ],
  "Musculoskeletal": [
    "joint_pain", "muscle_pain", "back_pain", "knee_pain", "hip_joint_pain",
    "muscle_weakness", "muscle_wasting", "swelling_joints", "movement_stiffness",
    "weakness_in_limbs", "painful_walking", "cramps",
  ],
  "Urinary": [
    "burning_micturition", "spotting_urination", "yellow_urine", "dark_urine",
    "bladder_discomfort", "foul_smell_of_urine", "continuous_feel_of_urine",
    "polyuria",
  ],
  "Other": [
    "irregular_sugar_level", "excessive_hunger", "cold_hands_and_feets",
    "enlarged_thyroid", "brittle_nails", "swollen_extremeties",
    "swollen_legs", "swollen_blood_vessels", "prominent_veins_on_calf",
    "depression", "irritability", "abnormal_menstruation",
    "ulcers_on_tongue", "drying_and_tingling_lips",
  ],
}

export const ALL_SYMPTOMS = Object.values(SYMPTOM_CATEGORIES).flat()

export const formatSymptom = (s) =>
  s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
