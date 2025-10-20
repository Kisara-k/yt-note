# Refactored Architecture Reference

This document explains the refactored codebase structure and how environment-based configuration works.

## Overview

The codebase has been refactored for production deployment with the following key changes:

1. ✅ **No hardcoded URLs** - All URLs use environment variables
2. ✅ **Centralized configuration** - Single source of truth for API URLs
3. ✅ **Environment-based deployment** - Works in dev and production
4. ✅ **Security-first** - Backend-only database access
5. ✅ **Deployment-ready** - Railway and Vercel configurations included

---

## Configuration Architecture

### Backend (`backend/`)

**Environment Variables** (`.env`):

```bash
# Database access (SERVICE ROLE - server only!)
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...  # Service role key only - bypasses RLS
SUPABASE_JWT_SECRET=...

# APIs
YOUTUBE_API_KEY=...
OPENAI_API_KEY=...

# Server
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS (production: add frontend URL)
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

**Key Files:**

- `backend/api.py` - CORS configured from `CORS_ORIGINS` env var
- `backend/main.py` - Server config from env vars
- `backend/config.py` - Chunking and AI config
- `backend/auth/middleware.py` - JWT verification using `SUPABASE_JWT_SECRET`

**Entry Point:**

```bash
# Development
python main.py

# Production (Railway)
uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Frontend (`frontend/`)

**Environment Variables** (`.env.local`):

```bash
# Backend API (ONLY public-safe values!)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000  # Dev
# NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app  # Prod

# Supabase (for auth ONLY)
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...  # ANON key, NOT service role!
```

**Key Files:**

- `frontend/lib/config.ts` - **Single source of truth** for all URLs
  ```typescript
  export const API_BASE_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  export const SUPABASE_ANON_KEY =
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
  ```

**Updated Components:**
All components now import from `@/lib/config`:

- ✅ `video-filter.tsx`
- ✅ `book-filter.tsx`
- ✅ `book-add.tsx`
- ✅ `book-chunk-editor.tsx`
- ✅ `content-notes-editor.tsx`
- ✅ `auth-context.tsx`

**API Routes** (Next.js):
All API routes use `NEXT_PUBLIC_BACKEND_URL`:

- `app/api/video/route.ts`
- `app/api/videos/route.ts`
- `app/api/note/route.ts`
- `app/api/chunks/[video_id]/route.ts`
- etc.

---

## Data Flow

### Development (Local)

```
┌──────────────────────┐
│  Browser             │
│  http://localhost:3000│
└──────────┬───────────┘
           │ NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
           ▼
┌──────────────────────┐
│  Backend API         │
│  http://localhost:8000│
└──────────┬───────────┘
           │ SUPABASE_SERVICE_KEY
           ▼
┌──────────────────────┐
│  Supabase DB         │
│  (Service role access)│
└──────────────────────┘
```

### Production (Railway + Vercel)

```
┌──────────────────────────┐
│  Browser                 │
│  https://app.vercel.app  │
└────────────┬─────────────┘
             │ NEXT_PUBLIC_BACKEND_URL=https://api.railway.app
             ▼
┌──────────────────────────┐
│  Backend API (Railway)   │
│  https://api.railway.app │
└────────────┬─────────────┘
             │ SUPABASE_SERVICE_KEY (server-only!)
             ▼
┌──────────────────────────┐
│  Supabase DB             │
│  (RLS enabled)           │
│  (Service role bypasses) │
└──────────────────────────┘
```

---

## Security Model

### What Frontend Has Access To

✅ **Allowed:**

- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL (for auth)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Anon key (for auth only)

❌ **Forbidden:**

- ❌ Service role keys
- ❌ JWT secrets
- ❌ Database passwords
- ❌ Any non-`NEXT_PUBLIC_` variables

### What Backend Has Access To

✅ **Backend-only:**

- `SUPABASE_SERVICE_KEY` - Full database access (bypasses RLS)
- `SUPABASE_JWT_SECRET` - For verifying user JWTs
- `YOUTUBE_API_KEY` - YouTube Data API
- `OPENAI_API_KEY` - OpenAI API
- Database credentials

### RLS (Row Level Security)

**Purpose**: Defense in depth - even if anon key leaks, RLS blocks direct access

**Configuration**:

```sql
-- Enable RLS on all tables
ALTER TABLE youtube_videos ENABLE ROW LEVEL SECURITY;
-- No policies = only service_role can access
```

**Result**:

- ✅ Backend (service role) can access everything
- ❌ Frontend (anon key) cannot access anything
- ✅ Must go through backend API

---

## File Structure

```
yt-note/
├── backend/
│   ├── .env                    # ❌ Never commit
│   ├── .env.example            # ✅ Template for setup
│   ├── api.py                  # ✅ CORS from env
│   ├── main.py                 # ✅ Server config from env
│   ├── config.py               # AI/chunking config
│   ├── railway.toml            # Railway config
│   ├── nixpacks.toml           # Nixpacks config
│   ├── Procfile                # Railway start command
│   └── auth/
│       └── middleware.py       # ✅ JWT verification
│
├── frontend/
│   ├── .env.local              # ❌ Never commit
│   ├── .env.local.example      # ✅ Template for setup
│   ├── vercel.json             # Vercel config
│   ├── lib/
│   │   └── config.ts           # ✅ Centralized URL config
│   ├── components/
│   │   ├── video-filter.tsx    # ✅ Uses API_BASE_URL
│   │   ├── book-filter.tsx     # ✅ Uses API_BASE_URL
│   │   └── ...                 # ✅ All updated
│   └── app/
│       └── api/
│           └── **/*.ts         # ✅ Uses NEXT_PUBLIC_BACKEND_URL
│
├── DEPLOYMENT.md               # ✅ Full deployment guide
├── MIGRATION_CHECKLIST.md      # ✅ Step-by-step checklist
└── .gitignore                  # ✅ Protects secrets
```

---

## Environment Variables Quick Reference

### Backend (Railway)

| Variable               | Type   | Purpose                        |
| ---------------------- | ------ | ------------------------------ |
| `SUPABASE_URL`         | Secret | Database URL                   |
| `SUPABASE_SERVICE_KEY` | Secret | Full DB access                 |
| `SUPABASE_JWT_SECRET`  | Secret | Verify user tokens             |
| `YOUTUBE_API_KEY`      | Secret | YouTube API                    |
| `OPENAI_API_KEY`       | Secret | OpenAI API                     |
| `CORS_ORIGINS`         | Config | Allowed frontend URLs          |
| `API_HOST`             | Config | Server host (0.0.0.0)          |
| `API_PORT`             | Config | Server port ($PORT in Railway) |

### Frontend (Vercel)

| Variable                        | Type   | Purpose              |
| ------------------------------- | ------ | -------------------- |
| `NEXT_PUBLIC_BACKEND_URL`       | Public | Backend API URL      |
| `NEXT_PUBLIC_SUPABASE_URL`      | Public | Supabase (auth only) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public | Anon key (auth only) |

---

## Development Workflow

### 1. Local Development

**Backend:**

```bash
cd backend
cp .env.example .env
# Fill in your values
python main.py
```

**Frontend:**

```bash
cd frontend
cp .env.local.example .env.local
# Set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm install
npm run dev
```

### 2. Testing Locally

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Production Deployment

Follow `DEPLOYMENT.md` step by step.

---

## Migration from Old Code

### What Changed

**Before:**

```typescript
// ❌ Hardcoded URL
fetch('http://localhost:8000/api/videos');
```

**After:**

```typescript
// ✅ Environment-based
import { API_BASE_URL } from '@/lib/config';
fetch(`${API_BASE_URL}/api/videos`);
```

**Before:**

```python
# ❌ Hardcoded CORS
allow_origins=["http://localhost:3000"]
```

**After:**

```python
# ✅ Environment-based
allowed_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
allow_origins=allowed_origins
```

---

## Troubleshooting

### "API_BASE_URL is not defined"

**Cause**: Component not importing from config

**Fix**:

```typescript
import { API_BASE_URL } from '@/lib/config';
```

### "CORS error"

**Cause**: Frontend URL not in `CORS_ORIGINS`

**Fix**: Update `CORS_ORIGINS` in Railway backend and redeploy

### "Invalid token"

**Cause**: `SUPABASE_JWT_SECRET` mismatch

**Fix**: Copy exact JWT secret from Supabase → Settings → API

### "Cannot access database"

**Cause**: Using anon key instead of service role

**Fix**: Backend should use `SUPABASE_SERVICE_KEY`, not `SUPABASE_ANON_KEY`

---

## Best Practices

1. ✅ **Always use config imports** - Never hardcode URLs
2. ✅ **Prefix frontend env vars** - Use `NEXT_PUBLIC_` for all frontend vars
3. ✅ **Never commit `.env`** - Use `.env.example` as template
4. ✅ **Test locally first** - Verify with localhost before deploying
5. ✅ **Update CORS after deployment** - Add production URLs to `CORS_ORIGINS`
6. ✅ **Use service role in backend only** - Never in frontend
7. ✅ **Enable RLS** - Defense in depth
8. ✅ **Monitor logs** - Railway and Vercel dashboards

---

## Additional Resources

- **Deployment Guide**: `DEPLOYMENT.md`
- **Migration Checklist**: `MIGRATION_CHECKLIST.md`
- **Security Setup**: `backend/.docs/RAILWAY_SECURITY_SETUP.md`
- **RLS Configuration**: `backend/.docs/RLS_SETUP.md`
- **RLS Examples**: `backend/.docs/RLS_EXAMPLES.md`

---

## Quick Commands

### Local Development

```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Production Deploy

```bash
# Push to GitHub (triggers auto-deploy)
git push origin main

# Or use Railway/Vercel CLIs
railway up  # Backend
vercel --prod  # Frontend
```

### Check Environment

```bash
# Backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SUPABASE_URL'))"

# Frontend
npm run env | grep NEXT_PUBLIC
```
