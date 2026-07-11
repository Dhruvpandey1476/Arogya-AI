# Deployment Guide — Arogya AI

Recommended free-tier setup:

| Part | Host | Why |
|------|------|-----|
| **Backend** (FastAPI) | **Render** (Free Web Service) | Supports Python, persistent process, WebSockets, env vars. Docker not required. |
| **Frontend** (React/Vite) | **Vercel** (Free) | Best free static hosting, instant builds, easy env vars. |
| **LLM** | **Groq** (Free API) | No server/GPU needed. |

> Why not one host for both? Render's free tier sleeps after 15 min idle (first request is slow but works — fine for a demo). Vercel serves the frontend fast and always-on. Groq removes the need for any GPU.

---

## 1. Backend on Render

1. Push your repo to GitHub (already done).
2. Go to https://render.com → **New → Web Service** → connect your repo.
3. Settings:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment variables** (Render dashboard → Environment):
   ```
   LLM_PROVIDER=groq
   GROQ_API_KEY=<your-groq-key>
   GROQ_MODEL=llama-3.3-70b-versatile
   CORS_ORIGINS=https://<your-vercel-app>.vercel.app
   ```
   (Add the Vercel URL after step 2 below, then redeploy.)
5. Deploy. Note your backend URL, e.g. `https://arogya-ai.onrender.com`.

**Note on RAM:** Whisper (voice) + Torch can exceed Render's free 512 MB RAM. If the service crashes on voice, set `WHISPER_MODEL_SIZE=tiny`, or disable the `/voice` route for the free demo. Text, symptom, skin, and chat features run fine.

---

## 2. Frontend on Vercel

1. Go to https://vercel.com → **New Project** → import your repo.
2. Settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite (auto-detected)
   - **Build Command:** `npm run build` · **Output:** `dist`
3. **Environment variable:**
   ```
   VITE_API_URL=https://arogya-ai.onrender.com
   ```
   (your Render backend URL from step 1)
4. Deploy. Your app is live at `https://<your-app>.vercel.app`.
5. Copy that URL into the backend's `CORS_ORIGINS` env var on Render and redeploy.

---

## 3. Verify

- Open the Vercel URL → run an assessment (ML + RAG + Groq LLM).
- Open chat → confirm streaming works (WebSocket auto-uses `wss://` from `VITE_API_URL`).

---

## Local development (unchanged)

No env vars needed locally — the frontend falls back to `http://localhost:8000` automatically.

```bash
# backend
cd backend && uvicorn main:app --reload --port 8000
# frontend
cd frontend && npm run dev
```

---

## Alternative free hosts
- **Railway** / **Fly.io** — backend, more RAM than Render but limited free hours/credit.
- **Hugging Face Spaces** — good if you want backend + model in one place (Docker).
- **Netlify** — frontend alternative to Vercel.
