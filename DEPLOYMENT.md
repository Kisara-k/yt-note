# Production Deployment Guide

This guide covers deploying the yt-note application to production using Railway (backend) and Vercel (frontend).

## � Deployment Concepts for Beginners

Before we start, let's understand key concepts you'll encounter:

### What is Backend vs Frontend?

- **Frontend (Next.js on Vercel)**: The website users see in their browser
  - HTML, CSS, JavaScript that runs in the user's browser
  - Example: The buttons, forms, and UI you interact with
- **Backend (FastAPI on Railway)**: The server that processes requests and talks to the database
  - Python code that runs on a server (not in user's browser)
  - Example: Saving notes, fetching videos, calling OpenAI API

### What is an Environment Variable?

Think of it as a **secret configuration** that changes between environments:

```
Development (your laptop):  BACKEND_URL = http://localhost:8000
Production (live website):  BACKEND_URL = https://your-app.railway.app
```

- **Why use them?** So you don't hardcode secrets (like API keys) in your code
- **Where are they stored?** Railway and Vercel dashboards (not in your code!)
- **Who can see them?** Only people with access to the Railway/Vercel project

### What is CORS (Cross-Origin Resource Sharing)?

**The Problem:**

```
Your Frontend:  https://my-app.vercel.app
Your Backend:   https://my-api.railway.app
                ↑ Different domains!
```

By default, browsers **block** frontend from calling backend (security measure).

**The Solution:**
CORS tells the backend: "These specific websites are allowed to call me"

```python
# Backend says: "Only my-app.vercel.app can call me"
CORS_ORIGINS = "https://my-app.vercel.app"
```

**Real Example:**

- ✅ **WITH CORS**: Your Vercel frontend can fetch data from Railway backend
- ❌ **WITHOUT CORS**: Browser shows error: "CORS policy: No 'Access-Control-Allow-Origin' header"

### What is a Port?

Think of it like an **apartment number** in a building:

```
Railway Building (Server):
- Port 3000: Your API is listening here 📞
- Port 5432: Database is listening here 🗄️
- Port 80:   Web traffic comes in here 🌐
```

- **Why $PORT?** Railway assigns ports dynamically, so we use `$PORT` variable
- **Never hardcode!** Don't use `8000` in production - use `$PORT`

### What is a Service Role Key?

Supabase has **two types of keys**:

1. **`anon` key (PUBLIC)** ❌ DON'T USE IN BACKEND

   - Limited permissions, meant for frontend
   - Respects Row Level Security (RLS)
   - Example: Users can only see their own data

2. **`service_role` key (SECRET)** ✅ USE IN BACKEND
   - Full database access, bypasses RLS
   - **NEVER expose to frontend!**
   - Example: Backend can see and modify all data

**Think of it like:**

- `anon` key = Guest pass (limited access)
- `service_role` key = Master key (full access)

### What is Row Level Security (RLS)?

Database security that controls **who can see what data**:

```sql
-- Without RLS:
SELECT * FROM videos;  -- ❌ Anyone can see ALL videos

-- With RLS:
SELECT * FROM videos;  -- ✅ Users only see their own videos
```

**In this app:**

- RLS is ENABLED (defense in depth)
- But NO POLICIES (only service_role can access)
- Result: Only your backend can access data, users cannot

### What is JWT (JSON Web Token)?

A **secure way to prove identity** without storing sessions on the server:

```
User logs in → Backend creates JWT → Sends to frontend
Frontend stores JWT → Includes it in every request
Backend verifies JWT → "Yep, this user is legit!"
```

**Example JWT:**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIn0.signature
     ↑ Header          ↑ Payload (user data)    ↑ Signature
```

**Why JWT?**

- Stateless (server doesn't need to remember who's logged in)
- Secure (signed with secret, can't be tampered with)
- Portable (works across different servers)

---

## �🔒 ZERO-CREDENTIAL FRONTEND

**IMPORTANT**: This application implements **backend-only authentication**. The frontend has **ZERO Supabase credentials** exposed to the browser!

- ❌ No `NEXT_PUBLIC_SUPABASE_URL`
- ❌ No `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- ✅ Only `NEXT_PUBLIC_BACKEND_URL`
- ✅ All auth handled by backend API

See `ZERO_CREDENTIAL_FRONTEND.md` for complete details.

## Architecture Overview

```
┌─────────────────┐
│  User Browser   │  ← You're here (Chrome, Firefox, etc.)
│ (NO Supabase    │
│  credentials!)  │  🔒 No database secrets in browser!
└────────┬────────┘
         │
         │ HTTPS requests with JWT tokens
         │ (e.g., "Get my videos", "Save this note")
         ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Vercel         │─────▶│  Railway         │─────▶│  Supabase DB    │
│  (Frontend)     │      │  (Backend API)   │      │  (PostgreSQL)   │
│                 │      │                  │      │                 │
│  Next.js 15     │      │  FastAPI/Python  │      │  Videos, Notes  │
│  React + UI     │      │  Business Logic  │      │  Books, Chunks  │
│                 │      │  OpenAI calls    │      │                 │
│  One env var:   │      │  Service role    │      │  RLS enabled    │
│  BACKEND_URL ✅ │      │  credentials 🔐  │      │  (extra defense)│
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  │ API calls with keys
                                  ▼
                         ┌──────────────────┐
                         │  OpenAI API      │
                         │  GPT-4, etc.     │
                         └──────────────────┘
```

**📚 Data Flow Example - User Creates a Note:**

1. **User clicks "Save Note"** in browser (Vercel frontend)
2. **Frontend sends HTTPS request** to Railway backend with JWT token
   ```
   POST https://your-app.railway.app/api/note
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   Body: { "video_id": "abc123", "content": "My notes..." }
   ```
3. **Backend validates JWT** (checks if user is legit)
4. **Backend saves to database** using service role key
5. **Backend returns success** to frontend
6. **Frontend shows "Note saved!"** to user

**Why This Architecture?**

- ✅ Frontend is fast (static site on CDN)
- ✅ Backend is secure (secrets never exposed)
- ✅ Database is protected (only backend can access)
- ✅ Easy to scale (separate frontend/backend)

---

## Security Model

✅ **What is secured:**

- **Frontend has NO Supabase credentials at all** (NEW!)
- Frontend cannot access database directly (impossible, no credentials)
- All authentication goes through backend API (NEW!)
- Backend uses service role keys (server-only)
- RLS enabled on database (defense in depth)
- JWT tokens stored in localStorage, validated by backend

❌ **What to NEVER do:**

- Expose SERVICE_ROLE keys to frontend
- Put JWT_SECRET in frontend environment
- Put SUPABASE_URL or SUPABASE_ANON_KEY in frontend (not needed anymore!)
- Allow direct database connections from browser

---

## Part 1: Backend Deployment (Railway)

### Prerequisites

- Railway account (https://railway.app)
- GitHub repository with your code
- Supabase project(s) set up

### Step 1: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect it's a Python app

### Step 2: Configure Build Settings

Railway should auto-detect the build, but verify:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `/backend` (if deploying from monorepo)

### Step 3: Set Environment Variables

In Railway dashboard → Variables, add:

```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# Supabase Database 1 (Videos)
SUPABASE_URL=https://nkuzhhpjdahuiuysemzg.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here  # Use service role, NOT anon key
SUPABASE_JWT_SECRET=your_jwt_secret_here

# Supabase Database 2 (Books)
SUPABASE_URL_2=https://your-second-project.supabase.co
SUPABASE_SERVICE_KEY_2=your_service_role_key_2_here  # Use service role, NOT anon key

# Database password (if needed)
DB_PASSWORD=your_db_password

# OpenAI
OPENAI_API_KEY=your_openai_key

# Server Configuration (Railway handles these automatically)

# 📚 What is API_HOST?
# The network interface your server listens on
# 0.0.0.0 = Listen on ALL network interfaces (required for Railway to route traffic to your app)
# 127.0.0.1 = Only localhost (would NOT work on Railway - outside requests couldn't reach it)
# Think of it as: "Which doors should my server answer knocks on?" - we want ALL doors open
API_HOST=0.0.0.0

# 📚 What is API_PORT?
# The port number your server listens on (like an apartment number in a building)
# Railway dynamically assigns a port and provides it through the $PORT environment variable
# NEVER hardcode a port like 8000 in production - use $PORT so Railway can control it
# The $ means it's a variable that Railway will replace with the actual port (e.g., 3000, 8080, etc.)
API_PORT=$PORT

# 📚 What is API_RELOAD?
# Auto-reload watches your code files and restarts the server when they change
# Great for development (saves time), BAD for production (wastes resources, can cause issues)
# false = Disable auto-reload for better performance and stability in production
API_RELOAD=false

# 📚 What is CORS (Cross-Origin Resource Sharing)?
# Security mechanism that controls which websites can access your API
#
# WHY IT'S NEEDED:
# Your frontend (vercel.app) and backend (railway.app) are on different domains
# Browsers block this by default for security (prevents malicious sites from stealing data)
# CORS tells the browser: "It's OK, these specific websites are allowed to call this API"
#
# EXAMPLE WITHOUT CORS:
# ❌ Frontend tries to call backend → Browser blocks it → API never receives request
#
# EXAMPLE WITH CORS:
# ✅ Frontend calls backend → Browser checks CORS → Sees domain is allowed → Request goes through
#
# CRITICAL: ADD YOUR ACTUAL VERCEL FRONTEND URL HERE AFTER DEPLOYMENT
# Comma-separated list of allowed origins (no spaces, no trailing slashes!)
# Add your Vercel URL after you deploy the frontend in Part 2
CORS_ORIGINS=https://your-app.vercel.app,https://your-backend.railway.app
```

**⚠️ IMPORTANT NOTES:**

1. **Service Role Keys**: Use the `service_role` key (NOT the `anon` key) from Supabase:

   - Go to Supabase Dashboard → Settings → API
   - Scroll down to "Project API keys"
   - Copy the **`service_role`** secret key (the long one)
   - This key bypasses RLS - that's correct for backend!

2. **CORS_ORIGINS**: You'll need to update this twice:

   - **First deployment**: Use temporary values `https://your-app.vercel.app,https://your-backend.railway.app`
   - **After frontend deployed**: Replace with your actual Vercel URL (e.g., `https://yt-notes-abc123.vercel.app,https://yt-notes-production.up.railway.app`)

3. **$PORT variable**: Keep it as `$PORT` (with the dollar sign) - Railway will automatically replace this with the actual port number

4. **Two Supabase databases?** If you only have ONE Supabase project:
   - Set `SUPABASE_URL_2` to the same value as `SUPABASE_URL`
   - Set `SUPABASE_KEY_2` to the same value as `SUPABASE_KEY`
   - Set `SUPABASE_SERVICE_KEY_2` to the same value as `SUPABASE_SERVICE_KEY`

**Important**: After deploying, come back and update `CORS_ORIGINS` with your actual Vercel URL!

### Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Railway will give you a URL like: `https://your-app.railway.app`
4. Test the API: `https://your-app.railway.app/` should return `{"message": "..."}`

### Step 5: Enable Public Networking

1. Go to Settings → Networking
2. Generate Domain if not already done
3. Note your backend URL (you'll need it for frontend)

---

## Part 2: Frontend Deployment (Vercel)

### Prerequisites

- Vercel account (https://vercel.com)
- Railway backend URL from Part 1
- Supabase project credentials

### Step 1: Create Vercel Project

1. Go to https://vercel.com/new
2. Import your Git repository
3. Vercel will auto-detect Next.js

### Step 2: Configure Build Settings

Vercel should auto-detect, but verify:

- **Framework Preset**: Next.js
- **Root Directory**: `frontend` (if monorepo)
- **Build Command**: `npm run build` or `pnpm build`
- **Output Directory**: `.next`
- **Install Command**: `npm install` or `pnpm install`

### Step 3: Set Environment Variables

In Vercel dashboard → Settings → Environment Variables, add:

```bash
# Backend API URL (from Railway) - THIS IS THE ONLY ONE NEEDED!
NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
```

**🎉 That's it! No Supabase credentials needed in frontend!**

**DO NOT ADD** (these are NOT needed anymore):

- ❌ `NEXT_PUBLIC_SUPABASE_URL`
- ❌ `NEXT_PUBLIC_SUPABASE_ANON_KEY`

The frontend now uses backend-only authentication. See `ZERO_CREDENTIAL_FRONTEND.md`.
NEXT_PUBLIC_SUPABASE_URL=https://nkuzhhpjdahuiuysemzg.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

````

**Critical**:

- Use `NEXT_PUBLIC_` prefix for all frontend env vars
- Use the `anon` key, NOT the `service_role` key
- Use your Railway backend URL for `NEXT_PUBLIC_BACKEND_URL`

### Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Vercel will give you a URL like: `https://your-app.vercel.app`
4. Test the frontend by visiting the URL

### Step 5: Update CORS in Backend

**Important**: Go back to Railway and update the `CORS_ORIGINS` variable:

```bash
CORS_ORIGINS=https://your-app.vercel.app
````

Then redeploy the Railway backend.

---

## Part 3: Database Configuration (Supabase)

### Enable Row Level Security (RLS)

This is CRITICAL for security. Run in Supabase SQL Editor:

```sql
-- Enable RLS on all tables
ALTER TABLE public.youtube_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subtitle_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.video_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_queue ENABLE ROW LEVEL SECURITY;
```

**Note**: With RLS enabled and NO policies, only the `service_role` (your backend) can access data. This is perfect for your security model!

### Verify JWT Secret

1. Go to Supabase → Settings → API
2. Copy the "JWT Secret"
3. Ensure it matches the `SUPABASE_JWT_SECRET` in Railway backend

---

## Part 4: Verification Checklist

### Test Backend

```bash
# Health check
curl https://your-backend.railway.app/

# Test with auth (replace TOKEN with real JWT)
curl https://your-backend.railway.app/api/videos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Frontend

1. Open `https://your-app.vercel.app`
2. Open browser DevTools → Network tab
3. Verify:
   - ✅ Requests go to `your-backend.railway.app`
   - ❌ NO requests go directly to `supabase.co/rest/v1/`
   - ✅ Auth requests go to `supabase.co/auth/v1/` (this is OK)

### Test Security

Try to access Supabase directly (should fail):

```bash
curl "https://nkuzhhpjdahuiuysemzg.supabase.co/rest/v1/youtube_videos" \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

Expected: Empty array or 403 error (RLS blocking access)

---

## Part 5: Post-Deployment

### Add Custom Domain (Optional)

**Vercel:**

1. Settings → Domains
2. Add your domain
3. Configure DNS records

**Railway:**

1. Settings → Networking → Custom Domain
2. Add your domain
3. Configure DNS records

### Set up Monitoring

**Railway:**

- Built-in metrics and logs
- Go to Observability tab

**Vercel:**

- Built-in analytics
- Go to Analytics tab

### Configure Webhooks (Optional)

Set up automatic deployments:

- Push to `main` branch → auto-deploy both Railway and Vercel

---

## Environment Variables Reference

### Backend (Railway) - REQUIRED Variables

**Where to get these values:**

| Variable                 | Required | Where to Find                                                             | What to Set                                                  |
| ------------------------ | -------- | ------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `YOUTUBE_API_KEY`        | Yes      | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) | Your YouTube Data API v3 key                                 |
| `SUPABASE_URL`           | Yes      | Supabase Dashboard → Settings → API → Project URL                         | `https://xxxxx.supabase.co` (Videos database)                |
| `SUPABASE_KEY`           | Yes      | Supabase Dashboard → Settings → API → `service_role` key (NOT anon!)      | The secret `service_role` key for videos DB                  |
| `SUPABASE_SERVICE_KEY`   | Yes      | Same as above (duplicate for compatibility)                               | Same value as `SUPABASE_KEY`                                 |
| `SUPABASE_JWT_SECRET`    | Yes      | Supabase Dashboard → Settings → API → JWT Secret                          | Copy the JWT secret (used to verify tokens)                  |
| `SUPABASE_URL_2`         | Yes      | Same as `SUPABASE_URL` but for books database                             | `https://yyyyy.supabase.co` (Books database, if using two)   |
| `SUPABASE_KEY_2`         | Yes      | Same as `SUPABASE_KEY` but for books database                             | The secret `service_role` key for books DB                   |
| `SUPABASE_SERVICE_KEY_2` | Yes      | Same as above (duplicate for compatibility)                               | Same value as `SUPABASE_KEY_2`                               |
| `OPENAI_API_KEY`         | Yes      | [OpenAI Platform](https://platform.openai.com/api-keys)                   | Your OpenAI API key (starts with `sk-`)                      |
| `CORS_ORIGINS`           | Yes      | You create this after deploying frontend                                  | `https://your-app.vercel.app,https://your-app.railway.app`   |
| `API_HOST`               | No       | N/A - Railway handles this                                                | Leave as `0.0.0.0` (binds to all network interfaces)         |
| `API_PORT`               | No       | N/A - Railway provides this automatically                                 | Leave as `$PORT` (Railway will set the port dynamically)     |
| `API_RELOAD`             | No       | N/A - Set to `false` for production                                       | `false` (disables auto-reload for better performance)        |
| `DB_PASSWORD`            | Optional | Supabase Dashboard → Settings → Database → Connection String              | Only needed if using direct database connection (not common) |

**⚠️ CRITICAL: Service Role Keys**

- **NEVER** use the `anon` key in the backend - only `service_role`!
- The `service_role` key bypasses Row Level Security (RLS)
- This is correct behavior - backend should have full database access
- Frontend will NEVER see these keys (zero-credential architecture)

### Frontend (Vercel) - REQUIRED Variables

**Where to get these values:**

| Variable                  | Required | Where to Find                      | What to Set                                                    |
| ------------------------- | -------- | ---------------------------------- | -------------------------------------------------------------- |
| `NEXT_PUBLIC_BACKEND_URL` | Yes      | Railway deployment URL from Part 1 | `https://your-app.railway.app` (your backend URL from Railway) |

**🎉 That's it! Only ONE environment variable needed for frontend!**

**❌ DO NOT ADD (outdated - not needed with zero-credential frontend):**

- ~~`NEXT_PUBLIC_SUPABASE_URL`~~ - No longer needed!
- ~~`NEXT_PUBLIC_SUPABASE_ANON_KEY`~~ - No longer needed!

**Why so few variables?** The frontend now uses backend-only authentication. All Supabase credentials stay on the server where they're safe. See `ZERO_CREDENTIAL_FRONTEND.md` for details.

---

## Troubleshooting

### CORS Errors

**Problem**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:

1. Check `CORS_ORIGINS` in Railway backend
2. Ensure it includes your Vercel frontend URL
3. Redeploy backend after changing

### Authentication Errors

**Problem**: "Invalid token" or "JWT verification failed"

**Solution**:

1. Verify `SUPABASE_JWT_SECRET` in Railway matches Supabase project
2. Check token is being sent in `Authorization: Bearer TOKEN` format
3. Verify user's email is in verified list

### Database Access Errors

**Problem**: "No rows returned" or "403 Forbidden"

**Solution**:

1. Verify backend is using `SERVICE_ROLE` key (not anon key)
2. Check RLS policies in Supabase
3. Service role should bypass RLS

### Build Failures

**Railway backend:**

- Check `requirements.txt` is in root or specify `--root-directory`
- Verify Python version in `nixpacks.toml`

**Vercel frontend:**

- Check `package.json` scripts
- Verify all dependencies are in `package.json`
- Check build logs for TypeScript errors

---

## Rollback Procedure

### Railway

1. Go to Deployments
2. Click on a previous successful deployment
3. Click "Redeploy"

### Vercel

1. Go to Deployments
2. Click on a previous deployment
3. Click "Promote to Production"

---

## Next Steps

1. ✅ Set up SSL/TLS (Railway and Vercel handle this automatically)
2. ✅ Configure custom domains
3. ✅ Set up monitoring and alerts
4. ✅ Enable Vercel Analytics
5. ✅ Configure Supabase backups
6. ✅ Set up CI/CD pipelines
7. ✅ Add rate limiting (consider Railway's built-in rate limiting)

---

## Support

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Supabase docs: https://supabase.com/docs

For project-specific help, see:

- `backend/.docs/RAILWAY_SECURITY_SETUP.md`
- `backend/.docs/RLS_SETUP.md`
- `backend/.docs/RLS_EXAMPLES.md`
