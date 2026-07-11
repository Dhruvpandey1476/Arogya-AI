from fastapi import APIRouter, Request, HTTPException
import uuid
import base64
import io
import logging
from PIL import Image

from schemas.assess_schema import AssessmentRequest, AssessmentResponse, SymptomSearchRequest, SymptomSearchResponse
from modules.llm.prompt_builder import build_assessment_prompt
from modules.llm.ollama_client import OllamaClient
from modules.llm.guardrails import apply_guardrails

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory session store
sessions = {}


@router.post("", response_model=AssessmentResponse)
async def assess(request: Request, body: AssessmentRequest):
    models = request.app.state.models
    session_id = str(uuid.uuid4())

    disease_results = []
    severity = "Low"
    cv_result = None

    # --- ML: Disease Prediction ---
    if models.get("disease_predictor") and body.symptoms:
        try:
            disease_results = models["disease_predictor"].predict(body.symptoms)
        except Exception as e:
            logger.error(f"Disease prediction failed: {e}")

    # --- ML: Severity Classification ---
    if models.get("severity_classifier"):
        try:
            severity = models["severity_classifier"].predict(
                symptoms=body.symptoms,
                duration_days=body.duration_days,
                pain_scale=body.pain_scale,
                fever=body.fever,
                fever_temp=body.fever_temp,
                age=body.age,
            )
        except Exception as e:
            logger.error(f"Severity classification failed: {e}")
            severity = _rule_based_severity(body)

    # --- CV: Skin Classification ---
    if models.get("skin_classifier") and body.image_base64:
        try:
            img_bytes = base64.b64decode(body.image_base64)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            cv_result = models["skin_classifier"].predict(img)
        except Exception as e:
            logger.error(f"Skin classification failed: {e}")

    # --- RAG: Retrieve relevant medical context ---
    rag_context = ""
    sources = []
    if models.get("rag_retriever") and disease_results:
        try:
            top_disease = disease_results[0]["name"] if disease_results else "general health"
            query = f"{top_disease} symptoms treatment first aid"
            rag_docs = models["rag_retriever"].retrieve(query, top_k=5)
            rag_context = "\n\n".join([d["text"] for d in rag_docs])
            sources = list(set([d["source"] for d in rag_docs]))
        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")

    # --- LLM: Generate explanation ---
    prompt = build_assessment_prompt(
        diseases=disease_results,
        severity=severity,
        cv_result=cv_result,
        rag_context=rag_context,
        symptoms=body.symptoms,
        duration_days=body.duration_days,
        age=body.age,
    )

    explanation = "Based on your symptoms, please consult a healthcare professional."
    first_aid_steps = ["Rest and stay hydrated", "Monitor your symptoms", "Seek medical attention if symptoms worsen"]
    specialist = "General Physician"

    try:
        ollama = OllamaClient()
        raw_response = ollama.generate(prompt)
        parsed = apply_guardrails(raw_response)
        explanation = parsed.get("explanation", explanation)
        first_aid_steps = parsed.get("first_aid_steps", first_aid_steps)
        specialist = parsed.get("specialist", specialist)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")

    # Store session for chatbot continuity
    sessions[session_id] = {
        "diseases": disease_results,
        "severity": severity,
        "cv_result": cv_result,
        "rag_context": rag_context,
        "symptoms": body.symptoms,
        "conversation_history": [],
    }

    return AssessmentResponse(
        session_id=session_id,
        diseases=[
            {"name": d["name"], "confidence": d["confidence"], "description": d.get("description", "")}
            for d in disease_results
        ] if disease_results else [],
        severity=severity,
        cv_result=cv_result,
        explanation=explanation,
        sources=sources,
        first_aid_steps=first_aid_steps,
        specialist=specialist,
        disclaimer="Arogya AI is not a substitute for professional medical advice. Always consult a qualified healthcare provider.",
    )


@router.post("/symptom-search", response_model=SymptomSearchResponse)
async def symptom_search(request: Request, body: SymptomSearchRequest):
    models = request.app.state.models
    if not models.get("symptom_embedder"):
        raise HTTPException(status_code=503, detail="Symptom embedder not loaded")
    matched = models["symptom_embedder"].find_similar(body.query, top_k=body.top_k)
    return SymptomSearchResponse(matched_symptoms=matched)


def _rule_based_severity(body: AssessmentRequest) -> str:
    """Fallback severity rules when model not available."""
    if body.pain_scale >= 8:
        return "Emergency"
    if body.fever and body.fever_temp and body.fever_temp > 103:
        return "High"
    if body.duration_days > 7 or body.pain_scale >= 6:
        return "Medium"
    return "Low"


def get_session(session_id: str):
    return sessions.get(session_id)
