# Backend Deployment Options for FastAPI

Since **Vercel cannot host your FastAPI backend** on the free tier, here are the best alternatives:

---

## 🏆 Recommended Options (Free Tier Available)

### 1. Railway.app ⭐ **Best Choice**

**Why Railway:**

- ✅ Easy FastAPI deployment
- ✅ PostgreSQL database included
- ✅ 500 execution hours/month free
- ✅ $5 free credit monthly
- ✅ No cold starts
- ✅ WebSocket support
- ✅ Auto-deploy from GitHub

**Pricing:**

- Free: 500 hours/month + $5 credit
- After free tier: ~$5-10/month for small apps

**Quick Setup:**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
cd backend
railway init
railway up
```

**Perfect for:** Long-running jobs, background processing, your video processing needs

📚 [Railway Documentation](https://docs.railway.app/)

---

### 2. Render.com

**Why Render:**

- ✅ Free tier (with limitations)
- ✅ Auto-deploy from GitHub
- ✅ PostgreSQL database available
- ✅ SSL certificates included
- ❌ Sleeps after 15 min inactivity (free tier)
- ❌ Cold start delays

**Pricing:**

- Free: Unlimited (but with sleep)
- Paid: $7/month (no sleep)

**Perfect for:** Low-traffic apps, development/staging

📚 [Render Documentation](https://render.com/docs)

---

### 3. Fly.io

**Why Fly.io:**

- ✅ Free tier: 3 shared-cpu VMs
- ✅ No cold starts
- ✅ Global deployment
- ✅ PostgreSQL database
- ❌ Steeper learning curve

**Pricing:**

- Free: 3 shared VMs, 3GB storage
- After: Pay-as-you-go

**Perfect for:** Global deployment, production apps

📚 [Fly.io Documentation](https://fly.io/docs/)

---

### 4. Azure App Service (Free F1 Tier)

**Why Azure:**

- ✅ 60 minutes/day compute time
- ✅ 1 GB RAM
- ✅ Custom domain support
- ❌ Limited to 60 min/day (free tier)
- ❌ More complex setup

**Pricing:**

- Free F1: 60 min/day
- Basic B1: ~$13/month (unlimited)

**Perfect for:** Azure ecosystem, Microsoft integration

📚 [Azure App Service Docs](https://learn.microsoft.com/en-us/azure/app-service/)

---

### 5. Google Cloud Run

**Why Cloud Run:**

- ✅ Generous free tier
- ✅ Auto-scaling
- ✅ Pay only for requests
- ❌ Cold starts possible
- ❌ Requires containerization

**Pricing:**

- Free: 2 million requests/month
- After: Pay-per-request

**Perfect for:** Serverless architecture, variable traffic

📚 [Cloud Run Documentation](https://cloud.google.com/run/docs)

---

## ⚙️ Deployment Requirements

Your FastAPI backend needs:

1. **Long-running execution** (AI processing takes minutes)
2. **Background job queue** (orchestrator)
3. **PostgreSQL connection** (psycopg2)
4. **External API calls** (OpenAI, YouTube)
5. **Large dependencies** (yt-dlp, google-api-client)
6. **Persistent connections** (WebSocket/SSE for status updates)

---

## 🔧 Railway Deployment (Recommended Steps)

### 1. Create `railway.json`

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

### 2. Create `Procfile`

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3. Set Environment Variables in Railway

```
DATABASE_URL=postgresql://...
SUPABASE_URL=...
SUPABASE_KEY=...
YOUTUBE_API_KEY=...
OPENAI_API_KEY=...
```

### 4. Deploy

```bash
cd backend
railway init
railway up
```

### 5. Get Your URL

```bash
railway domain
# Output: https://your-app.up.railway.app
```

### 6. Update Vercel

Set in Vercel Dashboard:

```
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

---

## 🐛 Troubleshooting

### Railway Build Fails

**Check:**

1. `requirements.txt` is in backend directory
2. `main.py` exists and has `app = FastAPI()`
3. All environment variables are set

### Database Connection Issues

**Railway PostgreSQL:**

1. Create PostgreSQL service in Railway
2. Copy `DATABASE_URL`
3. Update your `config.py` to use `DATABASE_URL` env var

### CORS Errors

Update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Cost Comparison (Monthly)

| Platform  | Free Tier   | Paid Starting |
| --------- | ----------- | ------------- |
| Railway   | $5 credit   | $5-10         |
| Render    | Unlimited\* | $7            |
| Fly.io    | 3 VMs       | Pay-as-you-go |
| Azure     | 60 min/day  | $13           |
| Cloud Run | 2M requests | Pay-per-use   |

\*With sleep after 15 min inactivity

---

## 🎯 Our Recommendation

**For Your App:** Use **Railway.app**

**Reasons:**

1. ✅ Handles long-running AI processing
2. ✅ No cold starts = better UX
3. ✅ Easy PostgreSQL integration
4. ✅ $5/month credit covers small usage
5. ✅ Simple deployment from GitHub
6. ✅ Good for development and production

**Deployment Order:**

1. Deploy backend to Railway first
2. Get Railway URL
3. Deploy frontend to Vercel with Railway URL
4. Test end-to-end

---

## 🔗 Quick Links

- [Railway Starter Guide](https://docs.railway.app/getting-started)
- [Render Python Guide](https://render.com/docs/deploy-fastapi)
- [Fly.io Python Guide](https://fly.io/docs/python/)
- [FastAPI Deployment Best Practices](https://fastapi.tiangolo.com/deployment/)

---

## 💡 Pro Tips

1. **Environment Variables**: Use platform's secret manager, never commit
2. **Database**: Use platform's managed PostgreSQL for easier setup
3. **Monitoring**: Enable platform's built-in monitoring/logging
4. **Scaling**: Start small, scale as needed
5. **Testing**: Always test with staging environment first

---

**Need help choosing?** Railway.app is the safest bet for your use case! 🚀
