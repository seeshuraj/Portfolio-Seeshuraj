# Deploy to Render

## 1. Push this repo to GitHub

```bash
git add .
git commit -m "feat: avatar backend"
git push origin main
```

## 2. Create Render Web Service

1. Go to https://dashboard.render.com → **New Web Service**
2. Connect repo: `seeshuraj/Portfolio-Seeshuraj`
3. Set **Root Directory**: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Plan: **Free**

## 3. Add Environment Variables in Render Dashboard

| Key | Value |
|-----|-------|
| `NVIDIA_API_KEY` | From https://build.nvidia.com |
| `SPEECH_KEY` | Azure Portal → Speech resource → Keys |
| `SPEECH_REGION` | e.g. `westeurope` |
| `SPEECH_VOICE` | `en-US-AriaNeural` |
| `ALLOWED_ORIGINS` | `["https://seeshuraj.github.io"]` |

## 4. Health check

Render auto-checks `GET /health` — no extra config needed.

## 5. Update frontend

In `index.html`, set:
```js
window.__AVATAR_API_URL = 'https://seeshuraj-avatar-api.onrender.com';
```

API docs available at: `https://seeshuraj-avatar-api.onrender.com/docs`
