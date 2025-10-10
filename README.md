# YouTube Notes Application

A full-stack application for creating and managing markdown notes for YouTube videos. Enter a video URL, and the app will fetch video information and let you write notes using a powerful TipTap markdown editor.

## ✨ New: Task 2 Complete!

**Single-user web app is now live!** 🎉

- ✅ Enter YouTube video URL or ID
- ✅ Auto-fetch video info (title, channel, stats)
- ✅ Create markdown notes with TipTap editor
- ✅ Auto-save notes to database
- ✅ Load existing notes automatically

**Quick Start**: See [QUICK_START_TASK2.md](QUICK_START_TASK2.md) for 5-minute setup!

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- pnpm
- Supabase account
- YouTube Data API v3 key

### Setup (5 minutes)

1. **Install dependencies**

```bash
# Python dependencies
cd backend/db
pip install -r requirements.txt

# Frontend dependencies
cd ../../frontend
pnpm install
```

2. **Configure environment**

Create `.env` in root:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
DB_PASSWORD=your_db_password
```

Create `frontend/.env.local`:

```env
BACKEND_URL=http://localhost:8000
```

3. **Create database tables**

```bash
cd backend/db
python create_table.py
```

4. **Run the application**

**Terminal 1 - Backend API:**

```bash
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**

```bash
cd frontend
pnpm dev
```

Open http://localhost:3000 and start taking notes! 🎉

## 📁 Project Structure

```
yt-note/
├── backend/
│   ├── api.py                    # FastAPI REST API (NEW - Task 2)
│   ├── fetch_youtube_videos.py   # YouTube API integration
│   ├── main.py                   # CLI tool
│   ├── test_task2.py            # Test suite (NEW - Task 2)
│   └── db/
│       ├── create_table.sql          # Database schemas (youtube_videos + video_notes)
│       ├── youtube_crud.py           # Video CRUD operations
│       ├── video_notes_crud.py       # Note CRUD operations (NEW - Task 2)
│       └── requirements.txt          # Python dependencies (includes FastAPI)
└── frontend/
    ├── app/
    │   ├── api/                  # Next.js API routes (NEW - Task 2)
    │   │   ├── video/
    │   │   └── note/
    │   ├── layout.tsx
    │   └── page.tsx              # Main app page
    ├── components/
    │   ├── video-notes-editor.tsx  # Main UI component (NEW - Task 2)
    │   └── ui/                     # TipTap editor & UI components
    └── .env.local                  # Frontend config
```

## 🎯 Features

### Task 2: Single-User Web App ✅

- ✅ **Video Input**: Enter YouTube URL or video ID
- ✅ **Smart Fetching**: Checks database first, fetches from YouTube API if needed
- ✅ **Video Display**: Shows title, channel name, views, likes
- ✅ **TipTap Editor**: Full-featured markdown editor
- ✅ **Note Management**: Create, edit, and save notes for each video
- ✅ **Auto-load**: Existing notes load automatically
- ✅ **Unsaved Indicator**: Know when you have unsaved changes
- ✅ **Toast Notifications**: User-friendly feedback

### Task 1: YouTube API Integration ✅

- ✅ Fetch YouTube video details using batch API (up to 50 videos per request)
- ✅ Store video data in PostgreSQL/Supabase
- ✅ Automatic timestamp tracking (created_at, updated_at)
- ✅ Support for various YouTube URL formats
- ✅ PostgreSQL array support for tags
- ✅ JSONB support for complex nested objects
- ✅ Upsert functionality (update existing or create new)
- ✅ Comprehensive query functions (by ID, channel, tags, date range)

### Backend API

- ✅ FastAPI REST API with OpenAPI docs
- ✅ CORS configured for frontend
- ✅ Request/response validation
- ✅ Error handling
- ✅ 4 main endpoints (video fetch, note CRUD)

### Database Schema

The `youtube_videos` table stores:

- Video metadata (title, description, channel info)
- Statistics (views, likes, comments)
- Tags (PostgreSQL array)
- Thumbnails (JSONB)
- Content details (duration, quality, captions)
- Status information (privacy, embeddable, etc.)
- Automatic timestamps with trigger-based updates

### Frontend

- Modern Next.js 15 app
- TipTap markdown editor
- Responsive UI with Tailwind CSS
- shadcn/ui components

## 📚 Usage Examples

### Fetch Videos from URLs

```python
from backend.fetch_youtube_videos import fetch_and_store_videos

urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/9bZkp7q19f0",
    "VIDEO_ID",  # Plain video IDs also work
]

results = fetch_and_store_videos(urls)
print(f"Successfully stored: {results['success']} videos")
```

### Query Videos

```python
from backend.db.youtube_crud import (
    get_all_videos,
    get_video_by_id,
    search_videos_by_tags,
    get_recently_updated_videos
)

# Get all videos
videos = get_all_videos(limit=50)

# Get specific video
video = get_video_by_id("dQw4w9WgXcQ")

# Search by tags
tagged_videos = search_videos_by_tags(["music", "tutorial"])

# Get recently updated (last 24 hours)
recent = get_recently_updated_videos(hours=24)
```

### Command Line Usage

```bash
# Run demo with example videos
python backend/main.py --demo

# Interactive mode (prompts for URLs)
python backend/main.py --interactive

# Fetch specific videos
python backend/main.py URL1 URL2 URL3
```

## 🔧 API Reference

### YouTube Data Fetching

- `fetch_single_video(url)` - Fetch and store a single video
- `fetch_video_details(video_ids)` - Fetch details for up to 50 videos
- `fetch_and_store_videos(urls, batch_size)` - Batch fetch and store
- `extract_video_id(url)` - Extract video ID from various URL formats

### Database CRUD Operations

- `create_or_update_video(video_data)` - Upsert a single video
- `bulk_create_or_update_videos(videos_data)` - Bulk upsert
- `get_video_by_id(video_id)` - Get by ID
- `get_all_videos(limit)` - Get all videos
- `get_videos_by_channel(channel_id, limit)` - Filter by channel
- `search_videos_by_tags(tags)` - Search by tags
- `get_recently_updated_videos(hours, limit)` - Get recent updates
- `delete_video(video_id)` - Delete by ID

## 📊 Database Schema Details

### Key Features

1. **Automatic Timestamps**

   - `created_at`: Set when video is first inserted
   - `updated_at`: Auto-updated via database trigger on any modification

2. **Tag Storage**

   - Stored as PostgreSQL `TEXT[]` array
   - Supports efficient searching with GIN indexes
   - Array overlap queries (`tags && ARRAY['tag1', 'tag2']`)

3. **JSONB Storage**

   - `thumbnails`: All thumbnail URLs and dimensions
   - `localized`: Only stored if default_language ≠ 'en'
   - `content_rating`: Rating information

4. **Indexes**
   - `channel_id`, `published_at`, `updated_at`: B-tree indexes
   - `tags`: GIN index for array searches

## 🔐 Environment Setup

### Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Copy the API key to `.env`

See `backend/db/docs/1 GET_API_KEY.md` for detailed instructions.

### Get Supabase Credentials

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project or select existing
3. Go to Settings > API
4. Copy URL and anon key to `.env`

See `backend/db/docs/1 SUPABASE_CONNECTION_GUIDE.md` for detailed instructions.

## 🐛 Troubleshooting

### Backend won't start (Task 2)

Make sure you have installed FastAPI: `pip install fastapi uvicorn pydantic`

### Frontend can't connect to backend

- Check backend is running on port 8000
- Verify `frontend/.env.local` has `BACKEND_URL=http://localhost:8000`
- Check browser console for CORS errors

### "YOUTUBE_API_KEY not found"

Make sure you have created a `.env` file with your YouTube API key.

### "Table does not exist"

Run `python backend/db/create_table.py` to create the required tables.

### "Connection refused"

Check your Supabase credentials in the `.env` file.

### "Quota exceeded"

You've hit YouTube API's daily quota limit (10,000 units). Wait until the next day or request a quota increase from Google Cloud Console.

### Video notes not saving

- Make sure backend API is running
- Check that `video_notes` table exists (run `create_table.py`)
- Ensure the video exists in `youtube_videos` table first

## 📚 Documentation

### Task 2 (Web App)

- [TASK2_SUMMARY.md](TASK2_SUMMARY.md) - Implementation overview
- [TASK2_IMPLEMENTATION.md](TASK2_IMPLEMENTATION.md) - Detailed guide
- [QUICK_START_TASK2.md](QUICK_START_TASK2.md) - 5-minute quick start

### Task 1 (YouTube API)

- [Task 1 - download video data/TASK1_COMPLETE.md](Task%201%20-%20download%20video%20data/TASK1_COMPLETE.md) - Task 1 summary
- [Task 1 - download video data/SETUP_GUIDE.md](Task%201%20-%20download%20video%20data/SETUP_GUIDE.md) - Setup guide
- [backend/db/docs/](backend/db/docs/) - Database documentation

## 📝 Roadmap

### Completed ✅

- [x] Task 1: YouTube API integration
- [x] Task 1: Database schema and CRUD operations
- [x] Task 1: Batch processing
- [x] Task 1: Automatic timestamp tracking
- [x] Task 2: Video input and display
- [x] Task 2: Note-taking with TipTap editor
- [x] Task 2: Save and load notes
- [x] Task 2: FastAPI backend
- [x] Task 2: Next.js frontend

### Future Enhancements 🚀

- [ ] User authentication (Google OAuth)
- [ ] Multi-user support
- [ ] Dashboard with all notes
- [ ] Search and filter notes
- [ ] Categories/tags for notes
- [ ] Export notes as markdown
- [ ] Video player integration
- [ ] Auto-save while typing
- [ ] Scheduled updates for video statistics
- [ ] Mobile app version

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.
