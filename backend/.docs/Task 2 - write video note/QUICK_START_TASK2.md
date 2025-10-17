# Quick Start Guide - Task 2

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- pnpm installed
- YouTube API key
- Supabase account with credentials

## 5-Minute Setup

### 1. Update Database (1 minute)

```bash
cd database
python create_table.py
```

### 2. Install Backend Dependencies (2 minutes)

```bash
cd database
pip install -r requirements.txt
```

### 3. Configure Environment (1 minute)

Make sure `.env` exists in root with:

```env
YOUTUBE_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

Create `frontend/.env.local`:

```env
BACKEND_URL=http://localhost:8000
```

### 4. Start Backend (30 seconds)

```bash
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Frontend (30 seconds)

```bash
cd frontend
pnpm dev
```

## Test It Out

1. Open http://localhost:3000
2. Enter a YouTube URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. Click "Load Video"
4. Write some notes
5. Click "Save Note"

Done! 🎉

## Common Issues

**Backend won't start?**

- Run `pip install fastapi uvicorn pydantic`

**Frontend can't connect?**

- Check backend is running on port 8000
- Verify `.env.local` exists in frontend folder

**Video not found?**

- Check YouTube API key is valid
- Verify video is public

## What's Working

- ✅ Enter YouTube video URL or ID
- ✅ Fetch video info (title, channel, stats)
- ✅ TipTap markdown editor
- ✅ Save notes to database
- ✅ Auto-load existing notes
- ✅ Unsaved changes indicator

## Next Video?

Just enter a new URL and click "Load Video"!
Your previous notes are automatically saved in the database.
