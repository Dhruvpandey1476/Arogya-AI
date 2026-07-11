# 🩺 Arogya AI — Multimodal Health Triage System

> A three-layer AI health assistant: ML predicts, deep learning sees, RAG-grounded LLM explains.

---

## Architecture

```
User Input (Symptoms / Voice / Skin Image)
        │
        ├── NLP: Sentence-Transformer Symptom Embedder
        ├── ML:  XGBoost + RF + SVM Ensemble → Top 3 Disease Predictions
        ├── ML:  XGBoost Severity Classifier → Low/Medium/High/Emergency
        └── CV:  EfficientNet-B0 Fine-tuned → Skin Condition + Risk Level
                         │
                         ▼
              RAG: ChromaDB + MiniLM Retriever
              → Top 5 medical document chunks
                         │
                         ▼
              LLM: Groq (Llama 3.3 70B) — or local Ollama fallback
              → RAG-grounded explanation + first aid + specialist
                         │
                         ▼
              React Frontend with WebSocket Chat
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS + Framer Motion |
| State | Zustand |
| Backend | FastAPI + Uvicorn |
| ML | XGBoost + scikit-learn (VotingClassifier) |
| CV | PyTorch + EfficientNet-B0 (ISIC 2018 dataset) |
| NLP Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | ChromaDB (local persistent) |
| LLM | Groq API (Llama 3.3 70B) for deploy · Ollama/Phi-3 Mini local fallback |
| Voice | OpenAI Whisper (local) |
| Translation | deep-translator |

---

## Setup (Pre-Hackathon — Do This Before You Arrive)

### 1. Clone and install dependencies

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Configure the LLM (Groq — recommended for deploy)

```bash
cd backend
cp .env.example .env
```

Then edit `.env` and paste a free Groq key from https://console.groq.com/keys:

```
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

**Local, offline alternative (optional):** install [Ollama](https://ollama.com), then set
`LLM_PROVIDER=ollama` in `.env` and run:

```bash
ollama serve
ollama pull phi3:mini
```

### 3. Train the ML models

```bash
cd backend

# Download disease-symptom dataset from Kaggle:
# https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset
# Place as: backend/data/raw/disease_symptom.csv

python modules/ml/train/train_disease.py
python modules/ml/train/train_severity.py
```

### 4. Train the skin CV classifier (optional — requires GPU)

```bash
# Download ISIC 2018 Task 3 from Kaggle and place images as:
# backend/data/raw/skin_images/{class_name}/*.jpg

python modules/cv/train/train_skin.py

# Or use a pre-trained model from HuggingFace — see train_skin.py comments
```

### 5. Ingest medical documents into ChromaDB

```bash
python scripts/ingest_medical_docs.py
# This uses 20 built-in medical knowledge articles (no external files needed)
# Optionally add .txt files to backend/data/raw/medical_docs/ for richer context
```

### 6. Verify everything is ready

```bash
python scripts/verify_setup.py
```

---

## Running the App

```bash
# Terminal 1 — Backend (uses Groq via .env; no local LLM needed)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev

# (Only if LLM_PROVIDER=ollama) run `ollama serve` in a separate terminal
```

Open http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Model status check |
| POST | `/assess` | Full ML+CV+RAG+LLM assessment |
| POST | `/assess/symptom-search` | Semantic symptom search |
| POST | `/voice` | Audio → Whisper transcription |
| WS | `/ws/chat/{session_id}` | Streaming health chatbot |

---

## Project Structure

```
arogya-ai/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Paths and settings
│   ├── routers/                   # API route handlers
│   ├── modules/
│   │   ├── ml/                    # Disease + severity ML models
│   │   ├── cv/                    # EfficientNet skin classifier
│   │   ├── nlp/                   # Symptom embedder + translator
│   │   ├── rag/                   # ChromaDB retriever + ingestion
│   │   └── llm/                   # Ollama client + prompt builder
│   ├── models/                    # Saved model weights (.pkl, .pt)
│   ├── vectorstore/               # ChromaDB persistent storage
│   └── schemas/                   # Pydantic request/response models
│
├── frontend/
│   └── src/
│       ├── pages/                 # LandingPage, AssessmentPage, ChatPage
│       ├── components/
│       │   ├── assessment/        # SymptomSelector, VoiceRecorder, ImageUploader, ResultCard
│       │   ├── chat/              # ChatWindow, MessageBubble, ChatInput
│       │   └── ui/                # SeverityBadge, ConfidenceBar, DisclaimerBanner
│       ├── store/                 # Zustand global state
│       └── services/              # Axios API layer
│
└── scripts/                       # verify_setup.py, ingest_medical_docs.py
```

---

## Demo Script (For Judges)

1. **Open Assessment page** → Select 5-6 symptoms from the selector
2. **Click Skin Image tab** → Upload a sample skin image
3. **Click Run Assessment** → Watch ML models + RAG + LLM run
4. **Show result card** → Point out confidence bars, severity badge, RAG sources
5. **Click "Discuss with Arogya"** → Chat with contextual follow-ups
6. **Judges ask questions** → Show real-time streaming response

**Key pitch line:** *"Unlike LLM chatbots that hallucinate medical facts, Arogya AI uses trained models to predict and retrieved WHO/MedlinePlus documents to explain. The LLM only speaks from evidence."*

---

## Disclaimer

Arogya AI is a health awareness and triage tool, not a medical diagnostic device. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

*Built with ❤️ for hackathon — Dhruv Pandey*
