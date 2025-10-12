# Railway Backend Deployment Guide

Quick guide to deploy your FastAPI backend to Railway.app (recommended hosting for this project).

---

## 🎯 Why Railway for This Project?

✅ **Perfect for long-running AI jobs** (no timeouts)  
✅ **$5/month free credit** (500 hours execution)  
✅ **No cold starts** (always warm, fast responses)  
✅ **PostgreSQL included** (easy database setup)  
✅ **Auto-deploy from GitHub** (CI/CD built-in)  
✅ **WebSocket support** (for real-time status updates)

---

## 📋 Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub account (repo already connected)
- Backend code pushed to GitHub

---

## 🚀 Deployment Steps

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

This will open your browser to authenticate.

### Step 3: Create Railway Configuration

Create `backend/railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Step 4: Create Procfile

Create `backend/Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Add Health Check Endpoint

Add to `backend/main.py`:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "youtube-notes-backend"
    }
```

### Step 6: Initialize Railway Project

```bash
cd backend
railway init
```

Follow prompts:

- **Project name**: `yt-note-backend`
- **Environment**: `production`

### Step 7: Add PostgreSQL (Optional - if not using Supabase)

```bash
railway add --plugin postgresql
```

This creates a PostgreSQL database and sets `DATABASE_URL` automatically.

### Step 8: Set Environment Variables

```bash
# Supabase
railway variables set SUPABASE_URL=your_supabase_url
railway variables set SUPABASE_KEY=your_supabase_key

# YouTube API
railway variables set YOUTUBE_API_KEY=your_youtube_key

# OpenAI
railway variables set OPENAI_API_KEY=your_openai_key

# Python environment
railway variables set PYTHON_VERSION=3.11
```

Or set them in Railway Dashboard:

1. Go to your project
2. Click "Variables" tab
3. Add each variable

### Step 9: Deploy!

```bash
railway up
```

This will:

1. Upload your code
2. Install dependencies from `requirements.txt`
3. Build the application
4. Start the server
5. Give you a public URL

### Step 10: Get Your URL

```bash
railway domain
```

Output: `https://yt-note-backend-production.up.railway.app`

**Copy this URL** - you'll need it for Vercel frontend!

---

## 🔧 Alternative: Deploy via GitHub (Recommended)

### Step 1: Connect GitHub Repository

1. Go to [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo"
3. Select your repository: `Kisara-k/yt-note`
4. Choose branch: `azure-deploy` or `main`

### Step 2: Configure Service

1. **Root Directory**: Click "Add Variable" → Set to `backend`
2. **Build Command**: (auto-detected from `Procfile`)
3. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables

In Railway Dashboard:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
YOUTUBE_API_KEY=your_api_key
OPENAI_API_KEY=sk-xxx
PYTHON_VERSION=3.11
```

### Step 4: Generate Domain

1. Click "Settings"
2. Scroll to "Domains"
3. Click "Generate Domain"
4. Copy the URL

### Step 5: Enable Auto-Deploy

✅ Already enabled! Every push to `azure-deploy` branch will auto-deploy.

---

## 📊 Monitor Your Deployment

### View Logs

```bash
railway logs
```

Or in Dashboard: Click "Logs" tab

### Check Metrics

Dashboard shows:

- CPU usage
- Memory usage
- Network traffic
- Deployment history

---

## 🐛 Troubleshooting

### Build Fails: "requirements.txt not found"

**Fix:** Ensure `requirements.txt` is in `backend/` directory

```bash
# Check
ls backend/requirements.txt

# Should show the file
```

### Build Fails: "Module not found"

**Fix:** Missing dependency in `requirements.txt`

```bash
# Add to backend/requirements.txt
pip freeze | grep <module-name>
```

### App Crashes: "Address already in use"

**Fix:** Use `$PORT` environment variable (Railway provides this)

```python
# main.py
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Database Connection Error

**Fix:** Update `config.py` to use Railway's `DATABASE_URL`

```python
import os

# Railway provides DATABASE_URL automatically
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/yt_notes")

# Or if using Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

### CORS Errors

**Fix:** Add Vercel domain to CORS

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yt-note.vercel.app",  # Your Vercel URL
        "https://yourdomain.com",      # Custom domain if you have one
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 💰 Cost Management

### Free Tier ($5 credit/month)

- 500 execution hours
- Shared resources
- 1 GB RAM
- 1 vCPU

**Estimated usage for your app:**

- ~100-300 hours/month (light usage)
- **Should stay within free tier!**

### Monitor Usage

Dashboard → "Usage" tab shows:

- Execution hours used
- Credit remaining
- Estimated cost

### Set Usage Alerts

1. Settings → "Usage Limits"
2. Set limit: $10/month
3. Get email alert when approaching limit

---

## 🔗 Connect to Vercel Frontend

After deployment, update Vercel environment variable:

```bash
# In Vercel Dashboard
NEXT_PUBLIC_API_URL=https://yt-note-backend-production.up.railway.app
```

Then redeploy Vercel frontend:

```bash
# Trigger redeploy
vercel --prod --cwd frontend
```

---

## ✅ Verify Deployment

### Test Health Endpoint

```bash
curl https://your-app.up.railway.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-12T10:30:00",
  "service": "youtube-notes-backend"
}
```

### Test API Endpoint

```bash
curl https://your-app.up.railway.app/api/videos
```

Should return video data or appropriate error.

---

## 🚀 Advanced: Custom Domain

### Step 1: Add Domain in Railway

1. Settings → Domains
2. Click "Custom Domain"
3. Enter: `api.yourdomain.com`

### Step 2: Configure DNS

Add CNAME record:

```
Type: CNAME
Name: api
Value: your-app.up.railway.app
```

### Step 3: Wait for SSL

Railway automatically provisions SSL (5-10 minutes).

---

## 🔄 CI/CD Setup

Railway automatically deploys when you push to GitHub!

**Deployment Flow:**

1. Push code to `azure-deploy` branch
2. Railway detects change
3. Builds new version
4. Runs tests (if configured)
5. Deploys if successful
6. Zero downtime deployment

### Disable Auto-Deploy (if needed)

1. Settings → "Deployments"
2. Toggle off "Auto-deploy"

---

## 📝 Files Created

Create these files in `backend/` directory:

✅ **`railway.json`** - Railway configuration  
✅ **`Procfile`** - Start command  
✅ **`runtime.txt`** (optional) - Python version

---

## 🎓 Best Practices

1. **Environment Variables**: Always use env vars, never hardcode
2. **Logging**: Use structured logging (Railway captures stdout)
3. **Health Checks**: Implement `/health` endpoint
4. **Error Handling**: Proper error responses with status codes
5. **Monitoring**: Check Railway metrics regularly

---

## 📚 Useful Commands

```bash
# View logs
railway logs

# View logs (follow mode)
railway logs -f

# Run command in Railway environment
railway run python manage.py migrate

# Open Railway dashboard
railway open

# Check service status
railway status

# Link local project to Railway
railway link

# Unlink project
railway unlink
```

---

## 🆘 Need Help?

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Status Page**: [status.railway.app](https://status.railway.app)

---

## ✨ You're Done!

Your backend is now deployed on Railway! 🎉

**Next steps:**

1. ✅ Backend deployed on Railway
2. 🔄 Update `NEXT_PUBLIC_API_URL` in Vercel
3. 🚀 Deploy frontend to Vercel
4. 🧪 Test end-to-end
5. 🌐 Set up custom domain (optional)

---

**Happy deploying!** 🚀
