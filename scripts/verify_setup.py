"""
Pre-hackathon verification script.
Run this to confirm everything is ready before you walk in.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

def check(label, fn):
    try:
        result = fn()
        status = PASS if result else WARN
        print(f"{status}  {label}")
        return bool(result)
    except Exception as e:
        print(f"{FAIL}  {label}: {e}")
        return False

print("\n=== Arogya AI Pre-Hackathon Verification ===\n")

# Python dependencies
check("Python 3.10+", lambda: sys.version_info >= (3, 10))

try:
    import numpy, pandas, sklearn, xgboost, torch, torchvision
    check("Core ML libraries (numpy, pandas, sklearn, xgboost, torch)", lambda: True)
except ImportError as e:
    check("Core ML libraries", lambda: (_ for _ in ()).throw(e))

try:
    import sentence_transformers
    check("Sentence Transformers", lambda: True)
except ImportError as e:
    check("Sentence Transformers", lambda: (_ for _ in ()).throw(e))

try:
    import chromadb
    check("ChromaDB", lambda: True)
except ImportError as e:
    check("ChromaDB", lambda: (_ for _ in ()).throw(e))

try:
    import fastapi, uvicorn
    check("FastAPI + Uvicorn", lambda: True)
except ImportError as e:
    check("FastAPI + Uvicorn", lambda: (_ for _ in ()).throw(e))

try:
    import whisper
    check("OpenAI Whisper", lambda: True)
except ImportError:
    print(f"{WARN}  Whisper not installed (optional). Run: pip install openai-whisper")

# Model files
import config
models_to_check = [
    ("Disease prediction model", config.DISEASE_MODEL_PATH),
    ("Severity classifier", config.SEVERITY_MODEL_PATH),
    ("Skin classifier weights", config.SKIN_MODEL_PATH),
    ("Skin class labels", config.SKIN_LABELS_PATH),
]

print()
for label, path in models_to_check:
    exists = Path(path).exists()
    status = PASS if exists else FAIL
    print(f"{status}  {label}: {path}")
    if not exists:
        print(f"     → Run the training script first!")

# ChromaDB
print()
chroma_path = Path(config.CHROMA_DB_PATH)
if chroma_path.exists() and any(chroma_path.iterdir()):
    print(f"{PASS}  ChromaDB vector store: {chroma_path}")
else:
    print(f"{FAIL}  ChromaDB not populated. Run: python backend/modules/rag/ingestion.py")

# Ollama
print()
try:
    import httpx
    resp = httpx.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=3)
    tags = resp.json().get("models", [])
    model_names = [m["name"] for m in tags]
    if config.OLLAMA_MODEL in model_names or any(config.OLLAMA_MODEL.split(":")[0] in n for n in model_names):
        print(f"{PASS}  Ollama running with model: {config.OLLAMA_MODEL}")
    else:
        print(f"{WARN}  Ollama running but model '{config.OLLAMA_MODEL}' not found.")
        print(f"     Available: {model_names}")
        print(f"     Run: ollama pull {config.OLLAMA_MODEL}")
except Exception:
    print(f"{FAIL}  Ollama not running. Start with: ollama serve")
    print(f"     Then pull model: ollama pull {config.OLLAMA_MODEL}")

print("\n=== Done ===\n")
print("If all checks pass, you're ready! Start with:")
print("  Backend:  cd backend && uvicorn main:app --reload")
print("  Frontend: cd frontend && npm run dev\n")
