from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routers import assess, chat, voice, health
from modules.ml.disease_predictor import DiseasePredictor
from modules.ml.severity_classifier import SeverityClassifier
from modules.cv.skin_classifier import SkinClassifier
from modules.rag.retriever import RAGRetriever
from modules.nlp.symptom_embedder import SymptomEmbedder
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instances
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Arogya AI models...")
    try:
        models["disease_predictor"] = DiseasePredictor(config.DISEASE_MODEL_PATH)
        logger.info("Disease predictor loaded")
    except Exception as e:
        logger.warning(f"Disease predictor not loaded: {e}. Train model first.")
        models["disease_predictor"] = None

    try:
        models["severity_classifier"] = SeverityClassifier(config.SEVERITY_MODEL_PATH)
        logger.info("Severity classifier loaded")
    except Exception as e:
        logger.warning(f"Severity classifier not loaded: {e}. Train model first.")
        models["severity_classifier"] = None

    try:
        models["skin_classifier"] = SkinClassifier(
            config.SKIN_MODEL_PATH, config.SKIN_LABELS_PATH
        )
        logger.info("Skin classifier loaded")
    except Exception as e:
        logger.warning(f"Skin classifier not loaded: {e}. Train model first.")
        models["skin_classifier"] = None

    try:
        models["rag_retriever"] = RAGRetriever(config.CHROMA_DB_PATH)
        logger.info("RAG retriever loaded")
    except Exception as e:
        logger.warning(f"RAG retriever not loaded: {e}. Run ingestion script first.")
        models["rag_retriever"] = None

    try:
        models["symptom_embedder"] = SymptomEmbedder()
        logger.info("Symptom embedder loaded")
    except Exception as e:
        logger.warning(f"Symptom embedder not loaded: {e}")
        models["symptom_embedder"] = None

    app.state.models = models
    logger.info("Arogya AI startup complete")
    yield
    logger.info("Arogya AI shutting down")


app = FastAPI(
    title="Arogya AI",
    description="Multimodal AI Health Triage System",
    version="1.0.0",
    lifespan=lifespan,
)

# Origins: localhost for dev + any extra from CORS_ORIGINS env (comma-separated), e.g. your deployed frontend URL.
import os
_extra_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"] + _extra_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(assess.router, prefix="/assess", tags=["Assessment"])
app.include_router(chat.router, prefix="/ws", tags=["Chat"])
app.include_router(voice.router, prefix="/voice", tags=["Voice"])


@app.get("/")
async def root():
    return {"message": "Arogya AI Backend Running", "version": "1.0.0"}
