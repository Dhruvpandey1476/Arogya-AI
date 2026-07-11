import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ---- Minimal .env loader (no external dependency) ----
_ENV_FILE = BASE_DIR / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        # don't override variables already set in the real environment
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# Model paths
DISEASE_MODEL_PATH = BASE_DIR / "models" / "disease_model.pkl"
SEVERITY_MODEL_PATH = BASE_DIR / "models" / "severity_model.pkl"
SYMPTOM_ENCODER_PATH = BASE_DIR / "models" / "symptom_encoder.pkl"
SKIN_MODEL_PATH = BASE_DIR / "models" / "skin_classifier" / "efficientnet_skin.pt"
SKIN_LABELS_PATH = BASE_DIR / "models" / "skin_classifier" / "class_labels.json"

# Vector store
CHROMA_DB_PATH = str(BASE_DIR / "vectorstore" / "chroma_db")

# ---- LLM provider ----
# Use "groq" for deployment, "ollama" for local. Auto-detects groq if a key is present.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq" if GROQ_API_KEY else "ollama")

# Ollama settings (local fallback)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:latest")

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# RAG settings
RAG_TOP_K = 5
RAG_CHUNK_SIZE = 300
RAG_CHUNK_OVERLAP = 50

# Session store (in-memory for hackathon)
SESSION_TTL_SECONDS = 3600

# Whisper model size: tiny, base, small, medium
WHISPER_MODEL_SIZE = "base"

# Data paths
DISEASE_DATASET_PATH = BASE_DIR / "data" / "raw" / "disease_symptom.csv"
MEDICAL_DOCS_PATH = BASE_DIR / "data" / "raw" / "medical_docs"
SEVERITY_DATASET_PATH = BASE_DIR / "data" / "processed" / "severity_synthetic.csv"
