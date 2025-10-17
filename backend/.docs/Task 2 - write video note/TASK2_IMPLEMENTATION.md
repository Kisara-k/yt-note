# Task 2 - Single User Web App Implementation

## Overview

Task 2 has been successfully implemented! This creates a single-user web application where you can:

1. Enter a YouTube video URL or ID
2. View video title and channel name
3. Create and save markdown notes for each video using TipTap editor
4. Automatically load existing notes when loading a video

## What Was Implemented

### 1. Database Schema (`database/create_table.sql`)

- ✅ Created `video_notes` table with:
  - `video_id` as primary key (foreign key to `youtube_videos`)
  - `note_content` for markdown notes
  - `user_email` for future multi-user support
  - Automatic timestamp tracking (`created_at`, `updated_at`)
  - Auto-update trigger for `updated_at`

### 2. Backend CRUD Operations (`database/video_notes_crud.py`)

- ✅ Create/update notes (upsert)
- ✅ Get note by video ID
- ✅ Get all notes with pagination
- ✅ Get notes with video information (JOIN)
- ✅ Delete notes
- ✅ User email support for future multi-user functionality

### 3. FastAPI Backend (`backend/api.py`)

- ✅ RESTful API endpoints:
  - `POST /api/video` - Fetch video info (from DB or YouTube API)
  - `GET /api/note/{video_id}` - Get note for a video
  - `POST /api/note` - Save/update note
  - `GET /api/notes` - Get all notes with video info
- ✅ CORS configuration for Next.js frontend
- ✅ Error handling and validation
- ✅ Automatic video fetching and storage

### 4. Next.js API Routes

- ✅ `/api/video` - Proxy to backend video endpoint
- ✅ `/api/note` - Proxy to backend note endpoints
- ✅ `/api/note/[video_id]` - Get specific note
- ✅ Error handling and response formatting

### 5. Frontend Components (`frontend/components/video-notes-editor.tsx`)

- ✅ Video URL input with validation
- ✅ Load video button with loading state
- ✅ Video information display (title, channel, stats)
- ✅ TipTap markdown editor integration
- ✅ Save note button with unsaved changes indicator
- ✅ Auto-load existing notes when fetching video
- ✅ Toast notifications for user feedback
- ✅ Responsive design

### 6. Dependencies

- ✅ Added FastAPI, Uvicorn, and Pydantic to `requirements.txt`
- ✅ Frontend already has all required dependencies

## Setup Instructions

### Step 1: Update Database Tables

Run the updated SQL to create the `video_notes` table:

```bash
cd database
python create_table.py
```

Or manually run the SQL in Supabase SQL Editor.

### Step 2: Install Python Dependencies

```bash
cd database
pip install -r requirements.txt
```

This will install FastAPI, Uvicorn, and other required packages.

### Step 3: Configure Environment Variables

Make sure your `.env` file in the root directory has:

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Database
DB_PASSWORD=your_db_password
```

Create a `.env.local` file in the `frontend` directory:

```env
BACKEND_URL=http://localhost:8000
```

### Step 4: Start the Backend API

```bash
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

You can view the API documentation at http://localhost:8000/docs

### Step 5: Start the Frontend

```bash
cd frontend
pnpm dev
```

The frontend will be available at http://localhost:3000

## Usage

1. **Open the app**: Navigate to http://localhost:3000
2. **Enter a video**: Paste a YouTube URL or video ID in the input field
   - Examples:
     - `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
     - `https://youtu.be/dQw4w9WgXcQ`
     - `dQw4w9WgXcQ`
3. **Click "Load Video"**: The app will:
   - Check if video exists in database
   - If not, fetch from YouTube API and store it
   - Display video title, channel name, and stats
   - Load any existing note for this video
4. **Write your note**: Use the TipTap editor to create markdown notes
   - Full markdown support
   - Rich text formatting
   - Code blocks, lists, tables, etc.
5. **Save your note**: Click "Save Note" button
   - Note is stored in the database
   - Unsaved changes indicator disappears
6. **Load another video**: Enter a new URL to switch videos
   - Your previous note is automatically saved in the database

## API Endpoints

### Backend API (Port 8000)

#### POST /api/video

Fetch video information by URL or ID

```json
Request:
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

Response:
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel_title": "Rick Astley",
  "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
  "view_count": 1234567890,
  "like_count": 12345678
}
```

#### GET /api/note/{video_id}

Get note for a specific video

```json
Response:
{
  "video_id": "dQw4w9WgXcQ",
  "note_content": "# My Notes\n\nThis is my note...",
  "created_at": "2025-10-10T12:00:00Z",
  "updated_at": "2025-10-10T13:00:00Z"
}
```

#### POST /api/note

Create or update a note

```json
Request:
{
  "video_id": "dQw4w9WgXcQ",
  "note_content": "# My Notes\n\nThis is my note...",
  "user_email": "user@example.com"
}

Response:
{
  "video_id": "dQw4w9WgXcQ",
  "note_content": "# My Notes\n\nThis is my note...",
  "user_email": "user@example.com",
  "created_at": "2025-10-10T12:00:00Z",
  "updated_at": "2025-10-10T13:00:00Z"
}
```

#### GET /api/notes

Get all notes with video information

```json
Response:
{
  "notes": [
    {
      "video_id": "dQw4w9WgXcQ",
      "note_content": "...",
      "youtube_videos": {
        "title": "...",
        "channel_title": "..."
      }
    }
  ],
  "count": 1
}
```

## Database Schema

### video_notes Table

```sql
CREATE TABLE video_notes (
    video_id VARCHAR(20) PRIMARY KEY,
    note_content TEXT,
    user_email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY(video_id) REFERENCES youtube_videos(id) ON DELETE CASCADE
);
```

## Features

### ✅ Implemented

- Video URL/ID input and validation
- Fetch video from database or YouTube API
- Display video information (title, channel, stats)
- TipTap markdown editor integration
- Create and update notes
- Auto-load existing notes
- Save button with unsaved changes indicator
- Toast notifications
- Responsive design
- RESTful API
- Database schema with foreign keys
- Automatic timestamp tracking

### 🔄 Deferred (Authentication)

For this single-user implementation, authentication has been simplified:

- User email is hardcoded as `default@user.com`
- No login/logout functionality yet
- RLS policies are set to allow all operations for testing

To add authentication in the future:

1. Implement Google OAuth or email/password authentication
2. Update RLS policies to restrict by user email
3. Pass authenticated user email to API endpoints
4. Add login/logout UI components

## Testing

### Test the Backend API

```bash
# Test video endpoint
curl -X POST http://localhost:8000/api/video \
  -H "Content-Type: application/json" \
  -d '{"video_url": "dQw4w9WgXcQ"}'

# Test note endpoint
curl -X POST http://localhost:8000/api/note \
  -H "Content-Type: application/json" \
  -d '{"video_id": "dQw4w9WgXcQ", "note_content": "# Test Note"}'

# Get note
curl http://localhost:8000/api/note/dQw4w9WgXcQ
```

### Test CRUD Operations

```bash
cd database
python video_notes_crud.py
```

## Troubleshooting

### Backend API Not Starting

- Check if port 8000 is already in use
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file has correct Supabase credentials

### Frontend Can't Connect to Backend

- Verify backend is running on port 8000
- Check `.env.local` has `BACKEND_URL=http://localhost:8000`
- Check browser console for CORS errors

### Video Not Found

- Verify YouTube API key is valid
- Check if video ID is correct
- Make sure video is public on YouTube

### Notes Not Saving

- Check backend logs for errors
- Verify `video_notes` table exists in database
- Make sure video exists in `youtube_videos` table first

## Next Steps

1. **Add Authentication**: Implement Google OAuth or email/password login
2. **Add User Dashboard**: Show list of all user's notes
3. **Add Search**: Search notes by content or video title
4. **Add Export**: Export notes as markdown files
5. **Add Sharing**: Share notes with other users
6. **Add Categories**: Organize notes by categories/tags
7. **Add Auto-save**: Auto-save notes while typing
8. **Add Rich Media**: Embed video player in the note editor

## File Structure

```
yt-note/
├── backend/
│   ├── api.py                    # FastAPI backend (NEW)
│   ├── fetch_youtube_videos.py   # YouTube API integration
│   └── main.py                   # CLI tool
├── database/
│   ├── create_table.sql          # Updated with video_notes table
│   ├── video_notes_crud.py       # Note CRUD operations (NEW)
│   ├── youtube_crud.py           # Video CRUD operations
│   └── requirements.txt          # Updated with FastAPI
└── frontend/
    ├── app/
    │   ├── api/                  # Next.js API routes (NEW)
    │   │   ├── video/route.ts
    │   │   └── note/
    │   │       ├── route.ts
    │   │       └── [video_id]/route.ts
    │   ├── layout.tsx            # Updated metadata
    │   └── page.tsx              # Updated to use VideoNotesEditor
    ├── components/
    │   ├── video-notes-editor.tsx  # Main component (NEW)
    │   └── ui/                     # UI components
    └── .env.local.example         # Environment template (NEW)
```

## Success Criteria ✅

All Task 2 requirements have been met:

1. ✅ User can enter video URL or ID
2. ✅ Shows video title and channel name
3. ✅ Fetches from database if exists, otherwise calls API
4. ✅ TipTap markdown editor implemented
5. ✅ Notes stored in separate table with video_id as PK
6. ✅ Existing notes loaded when entering video
7. ✅ Save button updates table entry
8. ✅ Notes stored in markdown format
9. ✅ Accessible from Next.js frontend

**Authentication note**: For single-user mode, authentication is simplified with a hardcoded user email. Full Google OAuth can be added as a future enhancement.
