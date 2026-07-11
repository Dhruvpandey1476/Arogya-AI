import json
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)

UNSAFE_KEYWORDS = [
    "suicide", "self-harm", "kill yourself", "overdose on purpose",
    "how to make poison", "weapon", "harm others",
]

OUT_OF_SCOPE_KEYWORDS = [
    "stock market", "cryptocurrency", "politics", "election", "religion",
    "legal advice", "court case", "relationship advice", "dating",
]


def is_safe_query(query: str) -> bool:
    """Check if query is health-related and safe."""
    query_lower = query.lower()

    for kw in UNSAFE_KEYWORDS:
        if kw in query_lower:
            logger.warning(f"Unsafe query blocked: {kw}")
            return False

    return True


def is_health_related(query: str) -> bool:
    """Check if query is within the health domain."""
    query_lower = query.lower()
    for kw in OUT_OF_SCOPE_KEYWORDS:
        if kw in query_lower:
            return False
    return True


def apply_guardrails(raw_response: str) -> Dict:
    """Parse LLM JSON response and apply safety guardrails."""
    # Strip markdown code fences if present
    cleaned = raw_response.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("LLM response was not valid JSON, extracting text")
        # Attempt to extract content from free-form response
        parsed = {
            "explanation": cleaned[:500] if cleaned else "Please consult a healthcare professional for a proper evaluation.",
            "first_aid_steps": [
                "Rest and stay hydrated",
                "Monitor your symptoms carefully",
                "Avoid self-medicating without professional guidance",
                "Seek medical attention if symptoms worsen or persist",
            ],
            "specialist": "General Physician",
            "when_to_emergency": "Seek emergency care if you experience severe difficulty breathing, chest pain, loss of consciousness, or extremely high fever.",
        }

    # Enforce disclaimer — always add it
    disclaimer_phrases = ["consult a doctor", "medical professional", "healthcare provider", "not a substitute"]
    explanation = parsed.get("explanation", "")
    if not any(p in explanation.lower() for p in disclaimer_phrases):
        parsed["explanation"] += " Please consult a qualified healthcare professional for accurate diagnosis and treatment."

    # Sanitize first aid steps
    steps = parsed.get("first_aid_steps", [])
    sanitized_steps = []
    for step in steps:
        # Remove any specific drug dosage recommendations
        step = re.sub(r"\b\d+\s*mg\b", "prescribed dosage", step, flags=re.IGNORECASE)
        sanitized_steps.append(step)
    parsed["first_aid_steps"] = sanitized_steps if sanitized_steps else [
        "Rest and stay hydrated",
        "Monitor your symptoms",
        "Consult a doctor for proper diagnosis",
    ]

    return parsed
