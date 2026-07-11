import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class RAGRetriever:
    def __init__(self, chroma_db_path: str):
        self.client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False),
        )
        try:
            self.collection = self.client.get_collection("medical_docs")
            count = self.collection.count()
            logger.info(f"RAG collection loaded: {count} chunks")
        except Exception:
            logger.warning("medical_docs collection not found. Run ingestion script first.")
            self.collection = None

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve top-k relevant chunks for a query."""
        if not self.collection:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count()),
            )

            docs = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                docs.append({
                    "text": doc,
                    "source": metadata.get("source", "Medical Knowledge Base"),
                    "relevance": 1 - results["distances"][0][i] if results.get("distances") else 1.0,
                })
            return docs

        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return []
