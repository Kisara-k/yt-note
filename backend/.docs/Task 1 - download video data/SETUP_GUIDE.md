# Step-by-Step Setup Guide

Follow these steps to get the YouTube video fetcher up and running.

## Prerequisites Check

Before starting, make sure you have:

- [ ] Python 3.8 or higher installed
- [ ] pip (Python package manager) installed
- [ ] A Supabase account (free tier is fine)
- [ ] A Google Cloud account (for YouTube API)

## Step 1: Get YouTube API Key

### 1.1 Go to Google Cloud Console

Visit: https://console.cloud.google.com/

### 1.2 Create a New Project (or select existing)

1. Click "Select a project" in the top bar
2. Click "New Project"
3. Name it (e.g., "yt-note-app")
4. Click "Create"

### 1.3 Enable YouTube Data API v3

1. In the sidebar, go to "APIs & Services" > "Library"
2. Search for "YouTube Data API v3"
3. Click on it
4. Click "Enable"

### 1.4 Create API Key

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the API key
4. (Optional) Click "Restrict Key" to limit usage to YouTube Data API only

**Save this key** - you'll need it for the `.env` file.

## Step 2: Get Supabase Credentials

### 2.1 Create Supabase Project

Visit: https://supabase.com/dashboard

1. Click "New Project"
2. Choose organization or create new
3. Fill in project details:
   - Name: "yt-note"
   - Database Password: (create a strong password)
   - Region: (choose closest to you)
4. Click "Create new project"
5. Wait for project to finish setting up (~2 minutes)

### 2.2 Get API Credentials

1. In your project dashboard, click "Settings" (gear icon)
2. Go to "API" section
3. Copy these values:
   - **Project URL** (e.g., https://xxx.supabase.co)
   - **anon public** key (under "Project API keys")

### 2.3 Get Database Password

1. Go to "Settings" > "Database"
2. Scroll to "Connection string"
3. Note the password you created (or reset if needed)

**Save these credentials** - you'll need them for the `.env` file.

## Step 3: Install Dependencies

### 3.1 Clone/Download the Repository

If you haven't already, get the project files.

### 3.2 Install Python Dependencies

```bash
cd database
pip install -r requirements.txt
```

Expected packages:

- supabase==2.7.4
- python-dotenv==1.0.0
- psycopg2-binary==2.9.9
- google-api-python-client==2.108.0

**Verify installation:**

```bash
pip list | grep -E "(supabase|google-api-python-client)"
```

## Step 4: Configure Environment Variables

### 4.1 Create .env File

In the project root directory, create a file named `.env`:

```bash
# On Windows
copy .env.example .env

# On Mac/Linux
cp .env.example .env
```

### 4.2 Edit .env File

Open `.env` in a text editor and fill in your credentials:

```env
# YouTube API (from Step 1)
YOUTUBE_API_KEY=AIzaSy...YOUR_KEY_HERE

# Supabase (from Step 2)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...YOUR_KEY_HERE

# Database Password (from Step 2.3)
DB_PASSWORD=your_database_password
```

**Important:**

- Replace ALL placeholder values
- Don't add quotes around values
- Don't commit this file to Git (it's in .gitignore)

## Step 5: Create Database Tables

### 5.1 Run Table Creation Script

```bash
cd database
python create_table.py
```

**Expected output:**

```
🔌 Connecting to Supabase database...
📄 SQL file loaded successfully
✅ Connected successfully
🔧 Executing SQL commands...
✅ Table created successfully!
```

### 5.2 Verify Tables Created

Go to Supabase Dashboard:

1. Click "Table Editor" in sidebar
2. You should see:
   - `youtube_videos` table
   - `notes` table

Click on `youtube_videos` to see all columns.

## Step 6: Test the Setup

### 6.1 Test Basic CRUD Operations

```bash
python db_crud.py
```

**Expected output:**

- Creates a test note
- Reads all notes
- Updates the note
- Deletes the note

### 6.2 Test YouTube CRUD Operations

```bash
python youtube_crud.py
```

**Expected output:**

- Upserts a sample video (Rick Astley)
- Reads the video back
- Shows search results

### 6.3 Test YouTube API Fetching

```bash
cd ../backend
python fetch_youtube_videos.py
```

**Expected output:**

- Fetches 3 sample videos from YouTube
- Stores them in database
- Shows summary statistics

## Step 7: Run Demo

### 7.1 Run Full Demo

```bash
python main.py --demo
```

**Expected output:**

- Fetches example videos
- Stores in database
- Queries and displays results

### 7.2 Try Interactive Mode

```bash
python main.py --interactive
```

Enter some YouTube URLs when prompted.

### 7.3 Fetch Specific Videos

```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Verification Checklist

Check that everything works:

- [ ] Environment variables are set in `.env`
- [ ] Python dependencies are installed
- [ ] Database tables are created
- [ ] `db_crud.py` runs without errors
- [ ] `youtube_crud.py` runs without errors
- [ ] `fetch_youtube_videos.py` fetches real videos
- [ ] `main.py --demo` completes successfully
- [ ] Videos appear in Supabase Table Editor

## Troubleshooting

### Error: "No module named 'supabase'"

**Solution:** Install dependencies

```bash
cd database
pip install -r requirements.txt
```

### Error: "YOUTUBE_API_KEY not found"

**Solution:** Check your `.env` file

- Make sure file is named exactly `.env` (not `.env.txt`)
- Make sure it's in the project root directory
- Make sure the API key is correct

### Error: "Could not connect to Supabase"

**Solution:** Check Supabase credentials

- Verify SUPABASE_URL and SUPABASE_KEY in `.env`
- Make sure project is running in Supabase dashboard
- Check internet connection

### Error: "Table does not exist"

**Solution:** Create tables

```bash
cd database
python create_table.py
```

### Error: "Quota exceeded"

**Solution:** Wait or increase quota

- Free YouTube API quota: 10,000 units/day
- Resets at midnight Pacific Time
- Request increase in Google Cloud Console if needed

### Error: "Invalid video ID"

**Solution:** Check URL format

- Must be a valid YouTube URL
- Supported formats:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `VIDEO_ID` (11 characters)

## Next Steps

Now that everything is set up:

1. **Explore the code:**

   - `database/youtube_crud.py` - Database operations
   - `backend/fetch_youtube_videos.py` - API fetching
   - `backend/main.py` - Main script

2. **Try fetching your own videos:**

   ```bash
   python backend/main.py "YOUR_VIDEO_URL"
   ```

3. **Query the database:**

   ```python
   from database.youtube_crud import get_all_videos
   videos = get_all_videos()
   for video in videos:
       print(f"{video['title']} - {video['view_count']:,} views")
   ```

4. **Check Supabase Dashboard:**

   - View stored videos in Table Editor
   - Run custom SQL queries
   - Monitor API usage

5. **Frontend Integration (optional):**
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

## Success! 🎉

You now have a fully functional YouTube video fetcher that:

- Fetches video data from YouTube API
- Stores it in PostgreSQL/Supabase
- Tracks timestamps automatically
- Supports batch processing
- Provides comprehensive querying

Start fetching and analyzing YouTube videos!

## Getting Help

If you encounter issues:

1. Check the error message carefully
2. Review this setup guide
3. Check `README.md` for additional documentation
4. Check `QUICK_REFERENCE.md` for common tasks
5. Review individual file documentation:
   - `backend/README.md`
   - `database/SETUP.md`

## Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Array Types](https://www.postgresql.org/docs/current/arrays.html)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
