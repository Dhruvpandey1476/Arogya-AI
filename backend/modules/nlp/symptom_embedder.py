from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

from modules.ml.disease_predictor import SYMPTOMS

logger = logging.getLogger(__name__)


class SymptomEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # Pre-compute embeddings for all canonical symptoms
        self.canonical_symptoms = SYMPTOMS
        readable = [s.replace("_", " ") for s in self.canonical_symptoms]
        self.symptom_embeddings = self.model.encode(readable, convert_to_numpy=True)
        logger.info(f"Embedded {len(self.canonical_symptoms)} symptoms")

    def find_similar(self, query: str, top_k: int = 10) -> List[str]:
        """Map free-text query to closest canonical symptoms by cosine similarity."""
        query_emb = self.model.encode([query], convert_to_numpy=True)
        scores = np.dot(self.symptom_embeddings, query_emb.T).flatten()
        scores /= (
            np.linalg.norm(self.symptom_embeddings, axis=1) *
            np.linalg.norm(query_emb) + 1e-9
        )
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.canonical_symptoms[i] for i in top_indices if scores[i] > 0.3]

    def text_to_symptoms(self, text: str) -> List[str]:
        """Extract symptom keywords from free text and map to canonical symptoms."""
        # First check for direct substring matches
        text_lower = text.lower().replace("-", "_")
        direct_matches = [s for s in self.canonical_symptoms if s.replace("_", " ") in text_lower]

        # Then add semantic matches
        semantic_matches = self.find_similar(text, top_k=5)

        # Combine and deduplicate
        all_matches = list(set(direct_matches + semantic_matches))
        return all_matches[:10]
