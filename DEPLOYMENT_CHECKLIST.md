# 🚀 Deployment Checklist

Complete guide to deploying your YouTube Notes app to production.

---

## 📋 Pre-Deployment Checklist

### ✅ Code & Configuration

- [ ] All code committed to GitHub
- [ ] `.env` files in `.gitignore`
- [ ] Environment variables documented in `.env.example`
- [ ] Backend has health endpoint (`/health`)
- [ ] Frontend builds successfully locally
- [ ] Backend runs successfully locally

### ✅ API Keys & Credentials Ready

- [ ] Supabase URL and Anon Key
- [ ] YouTube Data API v3 Key
- [ ] OpenAI API Key
- [ ] Email whitelist configured

### ✅ Accounts Created

- [ ] Railway.app account (for backend)
- [ ] Vercel account (for frontend)
- [ ] GitHub repository accessible

---

## 🎯 Phase 1: Deploy Backend (Railway)

### Step 1: Prepare Backend

```bash
# Verify files exist
ls backend/railway.json    # Railway config
ls backend/Procfile        # Start command
ls backend/runtime.txt     # Python version
ls backend/requirements.txt # Dependencies

# Test locally
cd backend
python main.py
# Visit http://localhost:8000/health
```

**Expected:** Health endpoint returns `{"status": "healthy"}`

### Step 2: Deploy to Railway

**Option A: Via GitHub (Recommended)**

1. Go to [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo"
3. Select: `Kisara-k/yt-note`
4. Root Directory: `backend`
5. Click "Deploy"

**Option B: Via CLI**

```bash
npm install -g @railway/cli
railway login
cd backend
railway init
railway up
```

### Step 3: Configure Environment Variables

In Railway Dashboard, add:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=sk-xxx
PORT=8000
```

### Step 4: Get Backend URL

In Railway Dashboard:

1. Settings → Domains
2. Click "Generate Domain"
3. **Copy URL**: `https://yt-note-backend-production.up.railway.app`

### Step 5: Verify Backend Works

```bash
# Test health endpoint
curl https://your-backend-url.up.railway.app/health

# Expected response:
# {"status":"healthy","timestamp":"...","service":"youtube-notes-backend"}
```

**✅ Backend Deployed:** [ ]

---

## 🎨 Phase 2: Deploy Frontend (Vercel)

### Step 1: Prepare Frontend

```bash
# Test build locally
cd frontend
pnpm install
pnpm build

# Expected: Build succeeds with no errors
```

### Step 2: Deploy to Vercel

**Option A: Via Dashboard (Recommended)**

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import Git Repository: `Kisara-k/yt-note`
3. Configure Project:
   - Framework Preset: **Next.js**
   - Root Directory: **frontend**
   - Build Command: `pnpm build`
   - Output Directory: `.next`
   - Install Command: `pnpm install`
4. Click "Deploy"

**Option B: Via CLI**

```bash
npm install -g vercel
vercel login
vercel --cwd frontend
```

### Step 3: Add Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
```

**Important:** Use the Railway URL from Phase 1, Step 4!

### Step 4: Redeploy with Environment Variables

After adding variables:

1. Go to Deployments tab
2. Click "..." on latest deployment
3. Click "Redeploy"

Or via CLI:

```bash
vercel --prod --cwd frontend
```

### Step 5: Get Frontend URL

Vercel provides URL like:

- `https://yt-note-xyz.vercel.app`
- Or your custom domain

**✅ Frontend Deployed:** [ ]

---

## 🔗 Phase 3: Connect Frontend & Backend

### Step 1: Update CORS on Backend

Edit `backend/api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yt-note-xyz.vercel.app",  # Your Vercel URL
        "https://yourdomain.com",          # Custom domain if any
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2: Commit and Push

```bash
git add backend/api.py
git commit -m "Update CORS for production"
git push origin azure-deploy
```

Railway will auto-deploy with new CORS settings.

### Step 3: Verify Connection

Visit your Vercel URL and test:

1. Can you log in? (Supabase auth)
2. Can you fetch video info? (Backend API)
3. Can you process a video? (Full flow)

**✅ Frontend ↔ Backend Connected:** [ ]

---

## 🧪 Phase 4: Testing

### Test Authentication

- [ ] Can log in with authorized email
- [ ] Cannot log in with unauthorized email
- [ ] Session persists on refresh
- [ ] Can log out successfully

### Test Video Processing

- [ ] Can enter YouTube URL
- [ ] Video info fetches correctly
- [ ] Can process video (background job)
- [ ] AI enrichment works
- [ ] Can view chunks

### Test Note Taking

- [ ] Can create new note
- [ ] Can edit existing note
- [ ] Auto-save works
- [ ] Can load saved notes

### Test Performance

- [ ] Page loads quickly
- [ ] No console errors
- [ ] API responses under 2 seconds
- [ ] Images load properly

**✅ All Tests Pass:** [ ]

---

## 🌐 Phase 5: Custom Domain (Optional)

### For Frontend (Vercel)

1. In Vercel Dashboard → Settings → Domains
2. Add domain: `yournotes.com`
3. Configure DNS:
   ```
   Type: CNAME
   Name: www (or @)
   Value: cname.vercel-dns.com
   ```
4. Wait for SSL certificate (automatic)

### For Backend (Railway)

1. In Railway Dashboard → Settings → Domains
2. Add custom domain: `api.yournotes.com`
3. Configure DNS:
   ```
   Type: CNAME
   Name: api
   Value: your-backend.up.railway.app
   ```
4. Wait for SSL certificate (automatic)

### Update Frontend Environment Variable

Update in Vercel:

```
NEXT_PUBLIC_API_URL=https://api.yournotes.com
```

Redeploy frontend after updating.

**✅ Custom Domain Set Up:** [ ]

---

## 📊 Phase 6: Monitoring & Maintenance

### Set Up Monitoring

**Railway:**

- [ ] Check "Usage" tab regularly
- [ ] Set spending limit ($10/month recommended)
- [ ] Enable email notifications

**Vercel:**

- [ ] Monitor "Analytics" tab
- [ ] Check bandwidth usage
- [ ] Review function logs

**Supabase:**

- [ ] Monitor database size
- [ ] Check active connections
- [ ] Review auth logs

### Set Up Alerts

**Railway:**

1. Settings → Usage Limits
2. Set limit: $10/month
3. Enable email alerts

**Vercel:**

1. Settings → Usage
2. Set bandwidth alert: 80 GB
3. Enable email notifications

### Regular Checks (Weekly)

- [ ] Check Railway usage (should be under 100 hours/week)
- [ ] Check Vercel bandwidth (should be under 25 GB/week)
- [ ] Review error logs (both platforms)
- [ ] Test key user flows

**✅ Monitoring Set Up:** [ ]

---

## 🐛 Troubleshooting Guide

### Frontend Won't Build

**Error:** `Module not found`

```bash
cd frontend
rm -rf node_modules .next
pnpm install
pnpm build
```

**Error:** `Type error in ...`

- Check TypeScript errors
- Fix type issues
- Rebuild

### Backend Crashes on Railway

**Check logs:**

```bash
railway logs
```

**Common issues:**

- Missing environment variable
- Database connection failed
- Import error (missing dependency)

**Solutions:**

1. Verify all env vars set
2. Check `requirements.txt` complete
3. Restart service: Railway Dashboard → Restart

### CORS Errors

**Symptom:** Network request blocked in browser console

**Solution:**

1. Update `backend/api.py` CORS origins
2. Include both HTTP and HTTPS
3. Include all domains (Vercel URL + custom domain)
4. Push changes to trigger redeploy

### API Timeout

**Symptom:** Request takes > 30 seconds

**Check:**

1. Railway logs for errors
2. Database connection status
3. External API rate limits (OpenAI, YouTube)

**Solution:**

- Implement proper error handling
- Add request timeouts
- Use background jobs for long operations

### Supabase Connection Issues

**Symptom:** Auth fails or database errors

**Check:**

1. Supabase project not paused
2. Correct URL and key in env vars
3. RLS policies allow access

**Solution:**

1. Unpause project if needed
2. Verify credentials
3. Update RLS policies

---

## 💰 Cost Tracking

### Expected Costs (Monthly)

| Service   | Free Tier           | Your Usage | Cost         |
| --------- | ------------------- | ---------- | ------------ |
| Railway   | 500 hrs + $5 credit | ~200 hrs   | $0           |
| Vercel    | 100 GB bandwidth    | ~5 GB      | $0           |
| Supabase  | 500 MB DB           | ~50 MB     | $0           |
| **Total** | -                   | -          | **$0/month** |

### When to Upgrade

**Railway ($10/month):**

- Using > 500 hours/month
- Need more memory/CPU
- Want priority support

**Vercel Pro ($20/month):**

- Using > 100 GB bandwidth
- Need advanced features
- Want custom domains on team

**Supabase Pro ($25/month):**

- Database > 500 MB
- Need > 50 connections
- Want daily backups

---

## 🎉 Post-Deployment

### Share Your App

- [ ] Share Vercel URL with testers
- [ ] Collect feedback
- [ ] Fix issues
- [ ] Iterate

### Document

- [ ] Update README with production URL
- [ ] Document deployment process (this file!)
- [ ] Create user guide
- [ ] Write changelog

### Promote

- [ ] Share on social media
- [ ] Post on Reddit/HackerNews
- [ ] Write blog post
- [ ] Demo video

---

## 📚 Quick Reference

### Important URLs

| Service  | Dashboard                                                | Logs             |
| -------- | -------------------------------------------------------- | ---------------- |
| Railway  | [railway.app](https://railway.app)                       | `railway logs`   |
| Vercel   | [vercel.com/dashboard](https://vercel.com/dashboard)     | Dashboard → Logs |
| Supabase | [supabase.com/dashboard](https://supabase.com/dashboard) | Dashboard → Logs |

### Deployment Commands

```bash
# Backend (Railway)
cd backend
railway up

# Frontend (Vercel)
cd frontend
vercel --prod

# View logs
railway logs        # Backend
# (Vercel logs in dashboard)
```

---

## ✅ Final Checklist

- [ ] Backend deployed on Railway
- [ ] Frontend deployed on Vercel
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] All features tested
- [ ] Monitoring set up
- [ ] Custom domain (optional)
- [ ] Documentation updated
- [ ] Team notified
- [ ] Users invited

---

## 🆘 Need Help?

**Documentation:**

- `VERCEL_DEPLOYMENT_GUIDE.md` - Detailed Vercel guide
- `RAILWAY_SETUP_GUIDE.md` - Detailed Railway guide
- `BACKEND_DEPLOYMENT_OPTIONS.md` - Alternative hosting
- `DEPLOYMENT_SUMMARY.md` - Overview

**Support:**

- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Vercel Discord: [vercel.com/discord](https://vercel.com/discord)
- GitHub Issues: Create issue in your repo

---

**🎊 Congratulations!** Your app is now live in production! 🚀

---

Last Updated: October 12, 2025
