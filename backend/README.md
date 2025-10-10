# Backend - YouTube Video Fetcher

This backend module fetches YouTube video details using the YouTube Data API v3 and stores them in a Supabase (PostgreSQL) database.

## Features

- ✅ Fetch video details from YouTube Data API v3
- ✅ Batch processing (up to 50 videos per API call)
- ✅ Extract video IDs from various YouTube URL formats
- ✅ Store video data in PostgreSQL with proper schema
- ✅ Automatic timestamp tracking (created_at, updated_at)
- ✅ Upsert support (update existing videos or create new ones)
- ✅ PostgreSQL array support for tags
- ✅ JSONB support for complex nested objects (thumbnails, localized content)

## Setup

### 1. Install Dependencies

```bash
cd backend/db
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with:

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Database (for direct psycopg2 connection)
DB_PASSWORD=your_db_password
```

### 3. Create Database Tables

Run the table creation script:

```bash
cd backend/db
python create_table.py
```

This will create:

- `youtube_videos` table with all required fields
- Automatic triggers for `updated_at` timestamp
- Indexes for common queries
- Row Level Security policies

## Database Schema

### YouTube Videos Table

```sql
CREATE TABLE youtube_videos (
    -- Primary identifier
    id VARCHAR(20) PRIMARY KEY,

    -- Top-level fields
    kind VARCHAR(50),
    etag VARCHAR(100),

    -- Snippet fields (flattened)
    published_at TIMESTAMPTZ,
    channel_id VARCHAR(50),
    title TEXT,
    description TEXT,
    channel_title VARCHAR(255),
    category_id VARCHAR(10),
    live_broadcast_content VARCHAR(20),
    default_language VARCHAR(10),
    default_audio_language VARCHAR(10),

    -- Tags stored as PostgreSQL array
    tags TEXT[],

    -- Complex nested objects stored as JSONB
    thumbnails JSONB,
    localized JSONB,  -- Only stored if default_language is not 'en'

    -- Content details
    duration VARCHAR(20),
    dimension VARCHAR(10),
    definition VARCHAR(10),
    caption BOOLEAN,
    licensed_content BOOLEAN,
    content_rating JSONB,
    projection VARCHAR(20),

    -- Status fields
    upload_status VARCHAR(20),
    privacy_status VARCHAR(20),
    license VARCHAR(20),
    embeddable BOOLEAN,
    public_stats_viewable BOOLEAN,
    made_for_kids BOOLEAN,

    -- Statistics
    view_count BIGINT,
    like_count BIGINT,
    favorite_count INTEGER,
    comment_count BIGINT,

    -- Automatic timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()  -- Auto-updated via trigger
);
```

### Indexes

- `idx_channel_id` - For filtering by channel
- `idx_published_at` - For sorting by publish date
- `idx_tags` - GIN index for array tag searches
- `idx_updated_at` - For finding recently updated videos
- `idx_created_at` - For finding recently added videos

## Usage

### Start the Backend API Server

The simplest way to start the backend:

```bash
cd backend
python main.py
```

This will start the FastAPI server at http://localhost:8000 with:

- **API endpoints**: http://localhost:8000/api/\*
- **Interactive documentation**: http://localhost:8000/docs
- **Auto-reload enabled** for development

#### Alternative: Direct uvicorn command

```bash
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### Environment Variables (Optional)

You can customize the server by setting environment variables in `backend/db/.env`:

```env
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

### Run Demo/Test Script

To test the YouTube video fetching functionality:

```bash
cd backend
python demo.py
```

This runs a demonstration that:

1. Fetches example videos from YouTube
2. Stores them in the database
3. Queries and displays the results

#### Demo Options

```bash
# Run with demo videos
python demo.py --demo

# Interactive mode (enter your own URLs)
python demo.py --interactive

# Fetch specific URLs
python demo.py URL1 URL2 URL3
```

### Fetch Videos from Python Script

```python
from backend.fetch_youtube_videos import fetch_and_store_videos, fetch_single_video

# Fetch multiple videos
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/9bZkp7q19f0",
    "dQw4w9WgXcQ",  # Plain video ID also works
]

results = fetch_and_store_videos(urls)
print(f"Successfully stored: {results['success']} videos")

# Fetch a single video
video = fetch_single_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

### CRUD Operations

```python
from backend.db.youtube_crud import (
    get_video_by_id,
    get_all_videos,
    get_videos_by_channel,
    search_videos_by_tags,
    get_recently_updated_videos
)

# Get a specific video
video = get_video_by_id("dQw4w9WgXcQ")

# Get all videos (with limit)
videos = get_all_videos(limit=50)

# Get videos from a channel
channel_videos = get_videos_by_channel("UCuAXFkgsw1L7xaCfnd5JJOw")

# Search by tags
tagged_videos = search_videos_by_tags(["rickroll", "music"])

# Get recently updated videos (last 24 hours)
recent = get_recently_updated_videos(hours=24)
```

### Run Tests

```bash
# Test database connection and table creation
cd backend/db
python create_table.py

# Test YouTube video CRUD operations
python youtube_crud.py

# Test YouTube API fetching and database storage (demo)
cd ..
python demo.py --demo

# Test the backend API
python quick_test.py
```

## Supported URL Formats

The system can extract video IDs from:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`
- `VIDEO_ID` (plain 11-character video ID)

## Features Explained

### Automatic Timestamp Tracking

- `created_at`: Set automatically when a video is first inserted
- `updated_at`: Automatically updated whenever the row is modified (via database trigger)

This allows you to:

- Track when videos were first added to your database
- Track when video statistics (views, likes) were last refreshed
- Query recently updated videos

### Upsert (Insert or Update)

The system uses PostgreSQL's `upsert` functionality:

- If a video doesn't exist, it's created
- If a video already exists (same ID), it's updated
- The `updated_at` timestamp is automatically refreshed on updates

### Tag Storage

Tags are stored as PostgreSQL arrays (`TEXT[]`), allowing:

- Efficient storage
- Fast searching with GIN indexes
- Array overlap queries (`&&` operator)
- Individual element searches (`= ANY(tags)`)

### JSONB Storage

Complex nested objects like thumbnails and localized content are stored as JSONB:

- Preserves original structure
- Allows JSON queries if needed
- More flexible than flattening all fields

### Conditional Localized Storage

The `localized` field is only stored if `default_language` is NOT 'en', following the task requirement to save space for English-language videos.

## API Rate Limits

YouTube Data API v3 has quota limits:

- Default quota: 10,000 units per day
- Each `videos.list` request costs 1 unit per video (approximately)
- Batch requests (up to 50 videos) are more efficient

## Error Handling

The system handles:

- Invalid YouTube URLs
- API errors (network issues, invalid API key)
- Database connection errors
- Missing environment variables

## Next Steps

1. ✅ Database schema created
2. ✅ CRUD operations implemented
3. ✅ YouTube API integration
4. ✅ Batch processing
5. ⏳ Frontend integration
6. ⏳ Scheduled updates for video statistics
7. ⏳ Search and filtering UI

## Troubleshooting

### "YOUTUBE_API_KEY not found"

Make sure you have created a `.env` file with your YouTube API key.

### "Table does not exist"

Run `python backend/db/create_table.py` to create the required tables.

### "Connection refused"

Check your Supabase credentials in the `.env` file.

### "Quota exceeded"

You've hit YouTube API's daily quota limit. Wait until the next day or request a quota increase.
