# Deploy Seeshuraj Avatar API to Render

## 1. Create a new Render Web Service
- Go to https://render.com → New → Web Service
- Connect this GitHub repo
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Free

## 2. Add Environment Variables in Render Dashboard

| Key | Value |
|-----|-------|
| `XAI_API_KEY` | Get from https://console.x.ai |
| `SPEECH_KEY` | Azure Portal → Speech resource → Keys and Endpoint |
| `SPEECH_REGION` | e.g. `westeurope` or `eastus` |
| `SPEECH_VOICE` | `en-US-AriaNeural` (free neural voice) |
| `ALLOWED_ORIGINS` | `["https://seeshuraj.github.io"]` |

## 3. Update your portfolio frontend
In `index.html`, before `</body>`:
```html
<script>
  window.__AVATAR_API_URL = "https://seeshuraj-avatar-api.onrender.com";
</script>
<script src="./avatar.js" defer></script>
```

## 4. Test locally
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real keys
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
```

## 5. Health check
`GET /health` returns `{"status":"ok","model":"grok-3-fast-beta","tts":true}`

## Architecture
```
Browser (Web Speech API STT)
  → POST /api/avatar-chat {message, history}
  → RAG keyword retrieval (rag.py)
  → Grok-3-fast-beta (llm.py via xAI OpenAI-compat API)
  → Azure AriaNeural TTS (tts.py) → base64 WAV
  ← {answer_text, audio_base64, latency_ms}
Browser plays audio + shows speech bubble
```
