# YouTube Notes Application

A full-stack application for creating and managing markdown notes for YouTube videos with **AI-powered subtitle analysis**. Enter a video URL, process it with AI to get intelligent chunks, summaries, and key points, then write notes using a powerful TipTap markdown editor.

## 🎯 NEW: AI-Powered Features

- ✅ **Subtitle Extraction**: Automatic subtitle download via yt-dlp
- ✅ **Intelligent Chunking**: Break videos into 5-minute segments
- ✅ **OpenAI Analysis**: AI-generated titles, summaries, key points, and topics for each chunk
- ✅ **Chunk Viewer**: Browse and explore video segments with AI insights
- ✅ **Background Processing**: Async job queue for video processing
- 🎉 **Process any YouTube video and get instant AI-powered insights!**

**For complete implementation details**: See [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

## 🔐 Authentication Required

**The app now requires secure login via Supabase!** 🔒

- ✅ Secure authentication with JWT tokens
- ✅ Only verified emails can access (hardcoded whitelist)
- ✅ No user emails stored in database
- ✅ Session management with automatic token refresh

**Authentication Setup**: See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for complete setup guide!

## ✨ Features

**Web Application** 🎉

- ✅ Secure login/signup with Supabase Auth
- ✅ Enter YouTube video URL or ID
- ✅ Auto-fetch video info (title, channel, stats)
- ✅ Create markdown notes with TipTap editor
- ✅ Auto-save notes to database
- ✅ Load existing notes automatically

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- pnpm
- Supabase account with Email Auth enabled
- YouTube Data API v3 key

### Setup (10 minutes)

> **⚠️ Important**: Authentication is now required. See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for detailed setup.

1. **Install dependencies**

```bash
# Python dependencies (includes pyjwt for auth)
cd backend/db
pip install -r requirements.txt

# Frontend dependencies (includes @supabase/supabase-js)
cd ../../frontend
pnpm install
```

2. **Configure environment**

Create `backend/db/.env`:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

3. **Configure verified emails**

Edit `backend/auth/config.py` to add authorized email addresses:

```python
VERIFIED_EMAIL_HASHES = [
    "your-email-hash-here",
    # Add more email hashes as needed
]
```

4. **Create database tables**

```bash
cd backend/db
python create_table.py
```

5. **Enable Supabase Email Auth**

- Go to your Supabase dashboard
- Navigate to Authentication > Providers
- Enable Email provider
- Create user accounts for verified emails

6. **Run the application**

**Terminal 1 - Backend API:**

```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
pnpm dev
```

7. **Sign in and start taking notes!**

- Open http://localhost:3000
- Sign in with a verified email account
- Start creating notes for your favorite videos! 🎉

## 📁 Project Structure

```
yt-note/
├── backend/
│   ├── auth/                      # Authentication module (NEW - Auth)
│   │   ├── __init__.py            # Module exports
│   │   ├── config.py              # Verified email hashes
│   │   ├── middleware.py          # JWT verification & email whitelist
│   │   ├── manage_verified_emails.py  # Helper script for managing hashes
│   │   └── .verified_emails       # Reference file (gitignored)
│   ├── api.py                     # FastAPI REST API with auth
│   ├── fetch_youtube_videos.py   # YouTube API integration
│   ├── main.py                    # Server entry point
│   └── db/
│       ├── create_table.sql       # Database schemas
│       ├── update_schema.sql      # Auth migration (NEW - Auth)
│       ├── youtube_crud.py        # Video CRUD operations
│       ├── video_notes_crud.py    # Note CRUD (no user_email)
│       └── requirements.txt       # Python dependencies (includes pyjwt)
└── frontend/
    ├── lib/
    │   └── auth-context.tsx       # Auth context provider (NEW - Auth)
    ├── app/
    │   ├── layout.tsx             # With AuthProvider (NEW - Auth)
    │   └── page.tsx               # Auth-protected main page (NEW - Auth)
    ├── components/
    │   ├── login-form.tsx         # Login/signup UI (NEW - Auth)
    │   ├── video-notes-editor.tsx # Main UI with auth tokens
    │   └── ui/                    # TipTap editor & UI components
    ├── package.json               # Includes @supabase/supabase-js
    └── .env.local                 # Frontend config (Supabase)
```

## 🎯 Features

### Authentication & Security ✅

- ✅ **Secure Login**: JWT-based authentication via Supabase
- ✅ **Email Verification**: Only whitelisted emails can access
- ✅ **Session Management**: Automatic token refresh
- ✅ **Protected API**: All endpoints require valid authentication
- ✅ **No Email Storage**: User emails not stored in database
- ✅ **Sign Out**: Secure session termination

### Web Application ✅

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
- ✅ JWT authentication middleware
- ✅ Email whitelist verification
- ✅ CORS configured for frontend
- ✅ Request/response validation
- ✅ Error handling with proper status codes
- ✅ Protected endpoints requiring authentication

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
- Supabase authentication integration
- React Context for auth state management
- TipTap markdown editor
- Responsive UI with Tailwind CSS
- shadcn/ui components
- Protected routes with auth checks

#### Application Routes

- `/` - Login page (root)
- `/video` - Main video notes editor
- `/video/filter` - Filter and browse all videos
- `/video/creator-notes` - View notes by creator/channel

**Note**: All video routes are under `/video/` to allow for future expansion (e.g., `/book/` for book notes).

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

### Authentication

All protected endpoints require an `Authorization: Bearer <token>` header.

**New Endpoints:**

- `POST /api/auth/verify-email` - Check if email is in verified list (public)

**Protected Endpoints:**

- `POST /api/video` - Fetch video information (requires auth)
- `GET /api/note/{video_id}` - Get note for video (requires auth)
- `POST /api/note` - Save note (requires auth)
- `GET /api/notes` - Get all notes (requires auth)

**Example Request:**

```javascript
const token = await getAccessToken(); // From auth context
const response = await fetch('/api/video', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({ video_url: 'https://...' }),
});
```

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
4. Copy the following to your `.env` files:

   - **URL**: Project URL (both backend and frontend)
   - **Anon Key**: For frontend (`NEXT_PUBLIC_SUPABASE_ANON_KEY`)
   - **Service Role Key**: For backend (`SUPABASE_KEY`)
   - **JWT Secret**: For backend token validation (`SUPABASE_JWT_SECRET`)

5. Enable Email Authentication:
   - Go to Authentication > Providers
   - Enable Email provider
   - Configure email templates (optional)

See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for detailed instructions.

## 🐛 Troubleshooting

### "Email is not authorized"

Your email is not in the verified list. Add it to `backend/config.py`:

```python
VERIFIED_EMAILS = [
    "your-email@example.com",
]
```

### "Invalid or expired token"

- Sign out and sign back in
- Check that `SUPABASE_JWT_SECRET` is correctly set in backend `.env`
- Verify Supabase project is active

### Frontend login page not working

- Ensure `@supabase/supabase-js` is installed: `pnpm install`
- Check `frontend/.env.local` has correct Supabase URL and anon key
- Verify Email Auth is enabled in Supabase dashboard

### Backend authentication errors

- Ensure `pyjwt` is installed: `pip install pyjwt`
- Check `backend/db/.env` has all required Supabase credentials
- Verify service role key (not anon key) is used in backend

### Frontend can't connect to backend

- Check backend is running on port 8000
- Verify CORS settings in `backend/api.py`
- Check browser console for CORS or auth errors

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
- Verify you're signed in (check for auth token)
- Check that `video_notes` table exists (run `create_table.py`)
- Ensure the video exists in `youtube_videos` table first
- Check browser console for authentication errors

## 📚 Documentation

### Authentication

- **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)** - Complete authentication setup guide
- [backend/auth/config.py](backend/auth/config.py) - Verified email hashes configuration
- [backend/auth/middleware.py](backend/auth/middleware.py) - Authentication middleware

### Web App Implementation

- [TASK2_SUMMARY.md](TASK2_SUMMARY.md) - Implementation overview
- [TASK2_IMPLEMENTATION.md](TASK2_IMPLEMENTATION.md) - Detailed guide

### YouTube API Integration

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
- [x] **Authentication: Supabase Auth integration** ⭐ NEW
- [x] **Authentication: Email whitelist verification** ⭐ NEW
- [x] **Authentication: JWT token validation** ⭐ NEW
- [x] **Authentication: Protected API endpoints** ⭐ NEW
- [x] **Security: No email storage in database** ⭐ NEW

### Future Enhancements 🚀

- [ ] Google OAuth integration
- [ ] Password reset flow
- [ ] Email verification flow
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
