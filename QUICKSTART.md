# Quick Start Guide - Production Ready

This guide gets you up and running with the refactored, production-ready yt-note application.

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or pnpm
- Supabase account (2 projects)
- YouTube Data API key
- OpenAI API key

---

## Local Development Setup

### 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/Kisara-k/yt-note.git
cd yt-note

# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
# or
pnpm install
```

### 2. Backend Environment Setup

```bash
cd backend
cp .env.example .env
```

Edit `.env` and fill in your values:

```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# Supabase Database 1 (Videos)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key  # Use service role, NOT anon key
SUPABASE_JWT_SECRET=your_jwt_secret

# Supabase Database 2 (Books)
SUPABASE_URL_2=https://your-second-project.supabase.co
SUPABASE_KEY_2=your_service_role_key_2
SUPABASE_SERVICE_KEY_2=your_service_role_key_2

# OpenAI
OPENAI_API_KEY=your_openai_key

# Server (leave defaults for local dev)
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Frontend Environment Setup

```bash
cd frontend
cp .env.local.example .env.local
```

Edit `.env.local`:

```bash
# Backend API (local development)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Supabase (for authentication)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### 4. Database Setup

Run the SQL schema in Supabase SQL Editor:

```bash
# For Database 1 (Videos)
# Copy contents of database_schema.sql and run in Supabase

# For Database 2 (Books)
# Copy contents of books_schema.sql and run in Supabase
```

### 5. Configure Verified Emails

```bash
cd backend/auth
python manage_verified_emails.py
```

Add your email to the verified list.

### 6. Start Development Servers

**Terminal 1 - Backend:**

```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

### 7. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Production Deployment

### Quick Deploy (Railway + Vercel)

1. **Deploy Backend to Railway**

   ```bash
   # Push to GitHub
   git push origin main

   # Railway will auto-detect and deploy
   # Or use Railway CLI:
   railway login
   railway init
   railway up
   ```

2. **Configure Backend Environment**

   - Go to Railway dashboard
   - Add all variables from `.env.example`
   - Don't forget to set `CORS_ORIGINS` (update after frontend deploys)

3. **Deploy Frontend to Vercel**

   ```bash
   # Use Vercel CLI:
   vercel login
   vercel --prod

   # Or connect via GitHub in Vercel dashboard
   ```

4. **Configure Frontend Environment**

   - Go to Vercel dashboard → Settings → Environment Variables
   - Add:
     - `NEXT_PUBLIC_BACKEND_URL` = your Railway URL
     - `NEXT_PUBLIC_SUPABASE_URL`
     - `NEXT_PUBLIC_SUPABASE_ANON_KEY`

5. **Update Backend CORS**

   - Go back to Railway
   - Update `CORS_ORIGINS` with your Vercel URL
   - Redeploy

6. **Enable Database RLS**
   ```sql
   -- Run in Supabase SQL Editor
   ALTER TABLE youtube_videos ENABLE ROW LEVEL SECURITY;
   ALTER TABLE subtitle_chunks ENABLE ROW LEVEL SECURITY;
   ALTER TABLE video_notes ENABLE ROW LEVEL SECURITY;
   ALTER TABLE books ENABLE ROW LEVEL SECURITY;
   ALTER TABLE book_chapters ENABLE ROW LEVEL SECURITY;
   ALTER TABLE book_notes ENABLE ROW LEVEL SECURITY;
   ```

For detailed steps, see `DEPLOYMENT.md`.

---

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/
# Should return: {"message": "YouTube Notes API is running"}
```

### Frontend Connection

1. Open http://localhost:3000
2. Open DevTools → Network tab
3. Try to use a feature
4. Verify requests go to `localhost:8000` (not Supabase directly)

### Database Access

```bash
# Should work (backend uses service role)
curl http://localhost:8000/api/videos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Should fail (RLS blocks direct access)
curl "https://your-project.supabase.co/rest/v1/youtube_videos" \
  -H "apikey: YOUR_ANON_KEY"
```

---

## Common Issues

### Backend won't start

**Issue**: `ModuleNotFoundError`

**Solution**:

```bash
cd backend
pip install -r requirements.txt
```

### Frontend build error

**Issue**: TypeScript errors or missing modules

**Solution**:

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

### CORS error

**Issue**: `Access-Control-Allow-Origin` header missing

**Solution**: Check `CORS_ORIGINS` in backend `.env` includes your frontend URL

### Auth error

**Issue**: "Invalid token"

**Solution**:

1. Verify `SUPABASE_JWT_SECRET` matches your Supabase project
2. Check your email is in verified list
3. Try logging out and back in

### Database error

**Issue**: "Cannot read from table"

**Solution**:

1. Check backend is using `SUPABASE_SERVICE_KEY` (not anon key)
2. Verify Supabase URL is correct
3. Run database schema SQL if tables don't exist

---

## File Structure

```
yt-note/
├── backend/                  # Python FastAPI backend
│   ├── api.py               # Main API endpoints
│   ├── main.py              # Server entry point
│   ├── orchestrator.py      # Job orchestration
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Backend environment (create from .env.example)
│   ├── auth/                # Authentication
│   ├── db/                  # Database operations
│   ├── openai_api/          # OpenAI integration
│   └── .docs/               # Documentation
│
├── frontend/                # Next.js frontend
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   ├── lib/                 # Utilities & config
│   ├── public/              # Static assets
│   ├── .env.local           # Frontend environment (create from .env.local.example)
│   └── package.json         # Node dependencies
│
├── DEPLOYMENT.md            # Detailed deployment guide
├── MIGRATION_CHECKLIST.md   # Step-by-step deployment checklist
├── ARCHITECTURE.md          # Architecture documentation
└── README.md                # Project overview
```

---

## Key Configuration Files

### Backend

- `.env` - Environment variables (secrets)
- `api.py` - CORS configuration
- `main.py` - Server settings
- `railway.toml` - Railway deployment config
- `Procfile` - Railway start command

### Frontend

- `.env.local` - Environment variables
- `lib/config.ts` - Centralized URL configuration
- `vercel.json` - Vercel deployment config

---

## Development Workflow

### Making Changes

1. **Create feature branch**

   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes** (backend or frontend)

3. **Test locally**

   ```bash
   # Backend
   cd backend && python main.py

   # Frontend
   cd frontend && npm run dev
   ```

4. **Commit and push**

   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature
   ```

5. **Create pull request** on GitHub

6. **Merge to main** → Auto-deploys to Railway/Vercel

### Testing

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test

# Type checking
cd frontend
npm run type-check
```

---

## Environment Variables Reference

### Backend (`.env`)

Required:

- `YOUTUBE_API_KEY` - YouTube Data API key
- `SUPABASE_URL` - Supabase project URL (DB 1)
- `SUPABASE_SERVICE_KEY` - Service role key (DB 1)
- `SUPABASE_JWT_SECRET` - JWT secret for verification
- `SUPABASE_URL_2` - Supabase project URL (DB 2)
- `SUPABASE_SERVICE_KEY_2` - Service role key (DB 2)
- `OPENAI_API_KEY` - OpenAI API key

Optional (have defaults):

- `API_HOST` - Default: 0.0.0.0
- `API_PORT` - Default: 8000
- `API_RELOAD` - Default: true
- `CORS_ORIGINS` - Default: http://localhost:3000

### Frontend (`.env.local`)

Required:

- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase URL (for auth)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Anon key (for auth)

---

## Next Steps

- [ ] Read `DEPLOYMENT.md` for production deployment
- [ ] Review `ARCHITECTURE.md` to understand the refactored code
- [ ] Use `MIGRATION_CHECKLIST.md` when deploying
- [ ] Configure RLS following `backend/.docs/RLS_SETUP.md`
- [ ] Set up monitoring and alerts
- [ ] Configure custom domains
- [ ] Set up CI/CD pipeline

---

## Getting Help

- **Deployment Issues**: See `DEPLOYMENT.md` Troubleshooting section
- **Architecture Questions**: See `ARCHITECTURE.md`
- **Security Setup**: See `backend/.docs/RAILWAY_SECURITY_SETUP.md`
- **RLS Configuration**: See `backend/.docs/RLS_SETUP.md`

## Additional Resources

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Supabase docs: https://supabase.com/docs
- Next.js docs: https://nextjs.org/docs
- FastAPI docs: https://fastapi.tiangolo.com

---

**You're ready to go! 🚀**

Start with local development, then follow `DEPLOYMENT.md` when ready for production.
