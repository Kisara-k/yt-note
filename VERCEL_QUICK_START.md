# Quick Vercel Deployment Reference

## 🚨 Key Limitation Found

**FastAPI backend CANNOT run on Vercel free tier** due to:

- 10-second timeout (your video processing takes minutes)
- 250 MB bundle size limit (your dependencies are too large)
- No background jobs/websockets support
- Stateless architecture (you need stateful processing)

## ✅ Solution: Split Deployment

1. **Frontend** → Vercel (this guide)
2. **Backend** → Railway/Render/Fly.io

---

## 📦 One-Command Deployment

### Prerequisites

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login
```

### Deploy

```bash
# From project root
vercel --cwd frontend

# For production
vercel --prod --cwd frontend
```

---

## 🌐 Via Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import repo: `Kisara-k/yt-note`
3. Configure:
   - Root: `frontend`
   - Framework: Next.js
   - Build: `pnpm build`
   - Install: `pnpm install`
4. Add env vars:
   ```
   NEXT_PUBLIC_SUPABASE_URL
   NEXT_PUBLIC_SUPABASE_ANON_KEY
   NEXT_PUBLIC_API_URL
   ```
5. Deploy! 🚀

---

## ⚙️ Environment Variables

Set these in Vercel Dashboard (Settings → Environment Variables):

| Variable                        | Example                   | Where to Get             |
| ------------------------------- | ------------------------- | ------------------------ |
| `NEXT_PUBLIC_SUPABASE_URL`      | `https://xyz.supabase.co` | Supabase Dashboard       |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGc...`              | Supabase Dashboard → API |
| `NEXT_PUBLIC_API_URL`           | `https://api.railway.app` | Your deployed backend    |

---

## 🐛 Common Issues

### Build Fails

```bash
# Locally test build
cd frontend
pnpm install
pnpm build
```

### CORS Errors

Update backend `main.py`:

```python
allow_origins=[
    "https://your-app.vercel.app",
    "https://yourdomain.com",
]
```

### Env Vars Not Working

1. Must start with `NEXT_PUBLIC_`
2. Redeploy after adding variables
3. Check Vercel Dashboard → Deployments → Environment Variables

---

## 📁 Files Created

✅ `vercel.json` - Vercel configuration  
✅ `.vercelignore` - Exclude backend from deployment  
✅ `frontend/.env.example` - Template for env vars  
✅ `frontend/package.json` - Added `packageManager: "pnpm@9.0.0"`

---

## 🔗 Next Steps

1. ✅ Created deployment files
2. 🔄 Deploy backend to Railway/Render first
3. 📝 Update `NEXT_PUBLIC_API_URL` with backend URL
4. 🚀 Deploy frontend to Vercel
5. ✨ Test the application

---

## 📚 Full Details

See `VERCEL_DEPLOYMENT_GUIDE.md` for complete step-by-step instructions.

---

## 💰 Free Tier Limits

| Resource          | Free Limit       |
| ----------------- | ---------------- |
| Bandwidth         | 100 GB/month     |
| Function Duration | 10 seconds       |
| Builds            | Unlimited        |
| SSL               | Free & automatic |

**Your frontend will fit easily! 🎉**
