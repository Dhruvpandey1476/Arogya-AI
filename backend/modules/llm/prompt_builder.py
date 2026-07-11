from typing import List, Dict, Optional


SYSTEM_PERSONA = """You are Arogya AI, a health triage and awareness assistant. You help people understand their symptoms, learn about potential health conditions, and know when to seek medical care.

STRICT RULES:
1. NEVER prescribe specific medications or dosages
2. ALWAYS recommend consulting a qualified doctor for diagnosis and treatment
3. NEVER contradict the ML model's assessment without strong justification from retrieved medical evidence
4. Stay strictly within health and medical topics
5. Be empathetic, clear, and non-alarmist
6. Base your explanations on the retrieved medical context provided — do not invent medical facts
7. If unsure, say so honestly and recommend professional evaluation
"""


def build_assessment_prompt(
    diseases: List[Dict],
    severity: str,
    cv_result: Optional[Dict],
    rag_context: str,
    symptoms: List[str],
    duration_days: int,
    age: int,
) -> str:
    disease_str = "\n".join([
        f"  - {d['name']}: {d['confidence']}% confidence"
        for d in diseases
    ]) if diseases else "  - Insufficient symptoms for prediction"

    cv_str = ""
    if cv_result:
        cv_str = f"""
SKIN IMAGE ANALYSIS:
  Condition: {cv_result['condition']}
  Confidence: {cv_result['confidence']}%
  Risk Level: {cv_result['risk_level']}
"""

    symptoms_str = ", ".join([s.replace("_", " ") for s in symptoms]) if symptoms else "Not specified"

    prompt = f"""{SYSTEM_PERSONA}

=== PATIENT ASSESSMENT DATA ===
Age: {age} years
Symptoms reported: {symptoms_str}
Duration: {duration_days} day(s)
Severity classification: {severity}

ML MODEL PREDICTIONS:
{disease_str}
{cv_str}

RETRIEVED MEDICAL CONTEXT:
{rag_context if rag_context else "General medical knowledge applies."}

=== YOUR TASK ===
Based on the ML predictions and retrieved medical context above, provide a structured JSON response with:
{{
  "explanation": "A clear 3-4 sentence explanation of what the predicted condition likely is and why the patient is experiencing these symptoms. Be empathetic and clear.",
  "first_aid_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
  "specialist": "Name of the appropriate medical specialist to consult",
  "when_to_emergency": "One sentence describing symptoms that would require emergency care"
}}

Respond ONLY with valid JSON. No preamble, no markdown, no extra text."""

    return prompt


def build_chat_prompt(
    user_message: str,
    conversation_history: List[Dict],
    session_context: Dict,
    rag_context: str,
) -> str:
    diseases = session_context.get("diseases", [])
    severity = session_context.get("severity", "Unknown")
    cv_result = session_context.get("cv_result")
    symptoms = session_context.get("symptoms", [])

    disease_str = ", ".join([d["name"] for d in diseases[:2]]) if diseases else "undetermined"
    symptoms_str = ", ".join([s.replace("_", " ") for s in symptoms[:5]]) if symptoms else "not specified"

    cv_str = ""
    if cv_result:
        cv_str = f"Skin finding: {cv_result['condition']} ({cv_result['confidence']}% confidence, {cv_result['risk_level']} risk)"

    # Format conversation history (last 8 turns max to save tokens)
    history_str = ""
    for msg in conversation_history[-8:]:
        role = "Patient" if msg["role"] == "user" else "Arogya AI"
        history_str += f"{role}: {msg['content']}\n"

    prompt = f"""{SYSTEM_PERSONA}

=== PATIENT CONTEXT FROM ASSESSMENT ===
Predicted conditions: {disease_str}
Symptoms: {symptoms_str}
Severity: {severity}
{cv_str}

=== RELEVANT MEDICAL INFORMATION ===
{rag_context if rag_context else "Use general medical knowledge."}

=== CONVERSATION HISTORY ===
{history_str}
Patient: {user_message}

=== YOUR RESPONSE ===
Arogya AI: """

    return prompt
