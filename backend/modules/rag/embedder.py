from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)

_model = None

def get_embedder():
    global _model
    if _model is None:
        logger.info("Loading RAG embedding model...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed_texts(texts):
    model = get_embedder()
    return model.encode(texts, convert_to_numpy=True)


def embed_query(query: str):
    model = get_embedder()
    return model.encode([query], convert_to_numpy=True)[0]
