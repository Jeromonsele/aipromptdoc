# 🚀 Deployment Guide

## Quick Deploy Summary

**Frontend (Vercel):** Set Root Directory to `frontend` and deploy
**Backend (Render):** Use `render.yaml` for one-click deploy

## Frontend → Vercel

### Settings in Vercel Dashboard:

```
Root Directory: frontend
Framework Preset: Next.js
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### If You Get 404 or Build Errors:

**Most common fix:**
1. Vercel Dashboard → Your Project → Settings
2. General → Root Directory
3. Make sure it says: `frontend` (not blank, not `./frontend`)
4. Save
5. Deployments → Redeploy

### After Backend is Deployed:

Add environment variable:
- Key: `NEXT_PUBLIC_API_URL`
- Value: `https://your-render-url.onrender.com`

## Backend → Render.com

### Option 1: Blueprint (Easiest)
1. Dashboard → Blueprints → New Blueprint
2. Connect repo: `Jeromonsele/aipromptdoc`
3. Render detects `render.yaml` automatically
4. Click "Apply"

### Option 2: Manual
1. New Web Service → Connect GitHub
2. Root Directory: `backend`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database

## Testing Deployment

### Test Backend:
```bash
curl https://your-render-url.onrender.com/health
```

Should return:
```json
{
  "status": "ok",
  "db": true,
  "openai_key": false
}
```

### Test Frontend:
Visit your Vercel URL and try the Prompt Doctor.
Demo mode works without backend!

## Current Status

✅ Frontend: Demo mode enabled (works standalone)
✅ Backend: Ready for Render.com deployment
✅ Database: Auto-configured in render.yaml

## Troubleshooting

**Vercel 404:**
- Check Root Directory = `frontend`
- Check Framework = Next.js
- Redeploy

**Backend errors:**
- Check build logs in Render dashboard
- Verify Root Directory = `backend`
- Check DATABASE_URL is set

**CORS errors:**
- Backend needs your Vercel URL in CORS settings
- Will auto-fix with `allow_origins=["*"]` currently set

