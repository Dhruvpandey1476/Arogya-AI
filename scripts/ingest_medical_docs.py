"""
Shortcut script — runs the RAG ingestion pipeline.
Usage: python scripts/ingest_medical_docs.py
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from modules.rag.ingestion import ingest
ingest()

