# Quick Setup Instructions

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure .env file

Create a `.env` file in the root directory with your credentials:

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Database (for direct psycopg2 connection)
DB_PASSWORD=your_db_password
```

- Get your Supabase project URL and anon key from: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/settings/api
- Get your YouTube API key from: https://console.cloud.google.com/apis/credentials

See `docs/1 GET_API_KEY.md` for detailed YouTube API setup instructions.
See `docs/1 SUPABASE_CONNECTION_GUIDE.md` for Supabase setup.

## 3. Create database tables

Run the table creation script:

```bash
python create_table.py
```

This will create:

- `youtube_videos` table - For storing YouTube video data
- `notes` table - For testing CRUD operations
- Automatic triggers for timestamp tracking
- Indexes for performance
- Row Level Security policies

Alternatively, you can run the SQL directly in Supabase SQL Editor:

```bash
# Copy contents of create_table.sql and run in Supabase SQL Editor
```

See `docs/1 CREATE_TABLE_INSTRUCTIONS.md` for more details.

## 4. Test the connection

### Test basic CRUD operations

```bash
python db_crud.py
```

### Test YouTube video operations

```bash
python youtube_crud.py
```

### Test YouTube API fetching

```bash
cd ../backend
python fetch_youtube_videos.py
```

## Tables Overview

### youtube_videos

Stores all YouTube video data including:

- Video metadata (title, description, channel, etc.)
- Statistics (views, likes, comments)
- Tags (PostgreSQL array)
- Thumbnails (JSONB)
- Timestamps (created_at, updated_at with auto-update trigger)

### notes

Simple test table for CRUD operations

## Connection Method Used

✅ **Supabase Python Client Library** - Best for your use case because:

- Simple and clean API
- Handles authentication automatically
- Perfect for persistent applications
- No need to manage connection strings or pooling
- Works with both IPv4 and IPv6

## Troubleshooting

### "YOUTUBE_API_KEY not found"

Make sure you have created a `.env` file with your YouTube API key.

### "Table does not exist"

Run `python create_table.py` to create the required tables.

### "Connection refused"

Check your Supabase credentials in the `.env` file.

### "Quota exceeded"

You've hit YouTube API's daily quota limit. Wait until the next day or request a quota increase.
