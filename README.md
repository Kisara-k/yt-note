# YouTube Notes Application

A full-stack application for fetching YouTube video details and storing them in a database, with a modern frontend for viewing and managing video information.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account
- YouTube Data API v3 key

### Setup

1. **Clone and install dependencies**

```bash
# Install Python dependencies
cd database
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
pnpm install
```

2. **Configure environment variables**

Create a `.env` file in the root directory:

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Database (for direct psycopg2 connection)
DB_PASSWORD=your_db_password
```

3. **Create database tables**

```bash
cd database
python create_table.py
```

4. **Run the application**

```bash
# Run backend demo
cd backend
python main.py --demo

# Or fetch specific videos
python main.py https://www.youtube.com/watch?v=VIDEO_ID

# Run frontend
cd frontend
pnpm dev
```

## 📁 Project Structure

```
yt-note/
├── backend/           # YouTube API integration
│   ├── main.py       # Main integration script
│   ├── fetch_youtube_videos.py  # YouTube API fetching
│   ├── youtube_api_demo.ipynb   # API exploration notebook
│   └── README.md
├── database/         # Database layer
│   ├── create_table.sql       # Table schemas
│   ├── create_table.py        # Table creation script
│   ├── youtube_crud.py        # YouTube video CRUD operations
│   ├── db_crud.py            # General CRUD operations
│   ├── requirements.txt
│   ├── SETUP.md
│   └── docs/         # Documentation
└── frontend/         # Next.js frontend
    ├── app/         # Next.js app directory
    ├── components/  # React components
    └── README.md
```

## 🎯 Features

### Backend

- ✅ Fetch YouTube video details using batch API (up to 50 videos per request)
- ✅ Store video data in PostgreSQL/Supabase
- ✅ Automatic timestamp tracking (created_at, updated_at)
- ✅ Support for various YouTube URL formats
- ✅ PostgreSQL array support for tags
- ✅ JSONB support for complex nested objects
- ✅ Upsert functionality (update existing or create new)
- ✅ Comprehensive query functions (by ID, channel, tags, date range)

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
from database.youtube_crud import (
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

See `database/docs/1 GET_API_KEY.md` for detailed instructions.

### Get Supabase Credentials

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project or select existing
3. Go to Settings > API
4. Copy URL and anon key to `.env`

See `database/docs/1 SUPABASE_CONNECTION_GUIDE.md` for detailed instructions.

## 🐛 Troubleshooting

### "YOUTUBE_API_KEY not found"

Make sure you have created a `.env` file with your YouTube API key.

### "Table does not exist"

Run `python database/create_table.py` to create the required tables.

### "Connection refused"

Check your Supabase credentials in the `.env` file.

### "Quota exceeded"

You've hit YouTube API's daily quota limit (10,000 units). Wait until the next day or request a quota increase from Google Cloud Console.

### Import errors in main.py

This is normal - the import paths are resolved at runtime using `sys.path.append()`.

## 📝 TODO / Roadmap

- [x] YouTube API integration
- [x] Database schema and CRUD operations
- [x] Batch processing
- [x] Automatic timestamp tracking
- [ ] Frontend video display
- [ ] Search and filter UI
- [ ] Scheduled updates for video statistics
- [ ] User authentication
- [ ] Note-taking functionality
- [ ] Video bookmarking
- [ ] Export functionality

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.
