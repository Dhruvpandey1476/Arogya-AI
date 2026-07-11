from pydantic import BaseModel, Field
from typing import List, Optional


class AssessmentRequest(BaseModel):
    symptoms: List[str] = Field(..., description="List of symptom names")
    symptom_text: Optional[str] = Field(None, description="Free-text symptom description")
    duration_days: int = Field(1, ge=1, le=365, description="Duration of symptoms in days")
    pain_scale: int = Field(0, ge=0, le=10, description="Pain level 0-10")
    fever: bool = Field(False, description="Whether patient has fever")
    fever_temp: Optional[float] = Field(None, description="Fever temperature in Celsius")
    age: int = Field(25, ge=0, le=120, description="Patient age")
    image_base64: Optional[str] = Field(None, description="Base64 encoded skin image")


class DiseaseResult(BaseModel):
    name: str
    confidence: float
    description: str


class CVResult(BaseModel):
    condition: str
    confidence: float
    risk_level: str  # benign / monitor / concerning


class AssessmentResponse(BaseModel):
    session_id: str
    diseases: List[DiseaseResult]
    severity: str  # Low / Medium / High / Emergency
    cv_result: Optional[CVResult]
    explanation: str
    sources: List[str]
    first_aid_steps: List[str]
    specialist: str
    disclaimer: str


class SymptomSearchRequest(BaseModel):
    query: str
    top_k: int = Field(10, ge=1, le=20)


class SymptomSearchResponse(BaseModel):
    matched_symptoms: List[str]
