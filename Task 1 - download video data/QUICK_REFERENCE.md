# Quick Reference Guide

## Environment Setup

1. Copy `.env.example` to `.env`
2. Fill in your credentials:
   - `YOUTUBE_API_KEY` from Google Cloud Console
   - `SUPABASE_URL` and `SUPABASE_KEY` from Supabase Dashboard
   - `DB_PASSWORD` from Supabase Database settings

## Database Setup

```bash
cd database
pip install -r requirements.txt
python create_table.py
```

## Usage

### Fetch Videos

```python
from backend.fetch_youtube_videos import fetch_and_store_videos

# Fetch multiple videos
urls = ["https://www.youtube.com/watch?v=VIDEO_ID1", "https://youtu.be/VIDEO_ID2"]
results = fetch_and_store_videos(urls)
```

### Query Videos

```python
from database.youtube_crud import *

# Get by ID
video = get_video_by_id("dQw4w9WgXcQ")

# Get all (with limit)
videos = get_all_videos(limit=50)

# By channel
channel_videos = get_videos_by_channel("CHANNEL_ID")

# By tags
tagged = search_videos_by_tags(["music", "tutorial"])

# Recently updated
recent = get_recently_updated_videos(hours=24)
```

### Command Line

```bash
# Demo
python backend/main.py --demo

# Interactive
python backend/main.py --interactive

# Fetch specific videos
python backend/main.py URL1 URL2 URL3
```

## Common SQL Queries

```sql
-- Get all videos
SELECT id, title, view_count, like_count FROM youtube_videos
ORDER BY view_count DESC LIMIT 10;

-- Search by tag
SELECT * FROM youtube_videos WHERE 'music' = ANY(tags);

-- Recently updated
SELECT * FROM youtube_videos
WHERE updated_at > NOW() - INTERVAL '24 hours';

-- By channel
SELECT * FROM youtube_videos WHERE channel_id = 'CHANNEL_ID';
```

## Troubleshooting

| Problem                     | Solution                                |
| --------------------------- | --------------------------------------- |
| `YOUTUBE_API_KEY not found` | Create `.env` file with your API key    |
| `Table does not exist`      | Run `python database/create_table.py`   |
| `Connection refused`        | Check Supabase credentials in `.env`    |
| `Quota exceeded`            | Wait 24 hours or request quota increase |
| Import errors               | Normal - paths resolve at runtime       |

## API Limits

- YouTube API: 10,000 units/day (default quota)
- Batch fetch: Up to 50 videos per API call
- Each video fetch: ~1 unit

## Key Files

| File                              | Purpose                                    |
| --------------------------------- | ------------------------------------------ |
| `backend/fetch_youtube_videos.py` | YouTube API fetching                       |
| `database/youtube_crud.py`        | Database CRUD operations                   |
| `backend/main.py`                 | Main integration script                    |
| `database/create_table.sql`       | Database schema                            |
| `.env`                            | Configuration (create from `.env.example`) |

## Data Fields

All YouTube API fields are stored:

- Metadata: title, description, channel, published date
- Statistics: views, likes, comments
- Tags: stored as PostgreSQL array
- Thumbnails: stored as JSONB
- Timestamps: created_at, updated_at (auto-updated)

## Next Steps

1. ✅ Set up environment
2. ✅ Create database tables
3. ✅ Test with sample videos
4. ⏳ Integrate with frontend
5. ⏳ Add scheduled updates
6. ⏳ Build UI for searching/filtering
