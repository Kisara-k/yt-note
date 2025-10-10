-- ===================================================
-- Create the 'youtube_videos' table for storing YouTube video data
-- ===================================================

-- Drop existing table if it exists (for clean setup)
DROP TABLE IF EXISTS youtube_videos CASCADE;

-- Create the youtube_videos table
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
    
    -- Content details (flattened)
    duration VARCHAR(20),
    dimension VARCHAR(10),
    definition VARCHAR(10),
    caption BOOLEAN,
    licensed_content BOOLEAN,
    projection VARCHAR(20),
    
    -- Status fields (flattened)
    upload_status VARCHAR(20),
    privacy_status VARCHAR(20),
    license VARCHAR(20),
    embeddable BOOLEAN,
    public_stats_viewable BOOLEAN,
    made_for_kids BOOLEAN,
    
    -- Statistics (these can be updated when re-fetching)
    view_count BIGINT,
    like_count BIGINT,
    favorite_count INTEGER,
    comment_count BIGINT,
    
    -- Automatic timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_channel_id ON youtube_videos(channel_id);
CREATE INDEX idx_published_at ON youtube_videos(published_at);
CREATE INDEX idx_tags ON youtube_videos USING GIN(tags);
CREATE INDEX idx_updated_at ON youtube_videos(updated_at);
CREATE INDEX idx_created_at ON youtube_videos(created_at);

-- Create trigger function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at on row updates
CREATE TRIGGER update_youtube_videos_updated_at
    BEFORE UPDATE ON youtube_videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE youtube_videos ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Allow all operations for testing" ON youtube_videos;

-- Create a policy to allow all operations (for testing)
-- WARNING: In production, you should have more restrictive policies!
CREATE POLICY "Allow all operations for testing" ON youtube_videos
FOR ALL 
USING (true)
WITH CHECK (true);

-- ===================================================
-- Keep the 'notes' table for CRUD testing
-- ===================================================

-- Create the table
CREATE TABLE IF NOT EXISTS notes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Allow all operations for testing" ON notes;

-- Create a policy to allow all operations (for testing)
-- WARNING: In production, you should have more restrictive policies!
CREATE POLICY "Allow all operations for testing" ON notes
FOR ALL 
USING (true)
WITH CHECK (true);

-- ===================================================
-- Create the 'video_notes' table for storing markdown notes for videos
-- ===================================================

-- Drop existing table if it exists
DROP TABLE IF EXISTS video_notes CASCADE;

-- Create the video_notes table
CREATE TABLE video_notes (
    -- Primary identifier (YouTube video ID)
    video_id VARCHAR(20) PRIMARY KEY,
    
    -- Note content in markdown
    note_content TEXT,
    
    -- User email (for future multi-user support)
    user_email VARCHAR(255),
    
    -- Automatic timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Foreign key to youtube_videos table
    CONSTRAINT fk_video
        FOREIGN KEY(video_id) 
        REFERENCES youtube_videos(id)
        ON DELETE CASCADE
);

-- Create indexes for common queries
CREATE INDEX idx_video_notes_user_email ON video_notes(user_email);
CREATE INDEX idx_video_notes_updated_at ON video_notes(updated_at);

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_video_notes_updated_at
    BEFORE UPDATE ON video_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE video_notes ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Allow all operations for testing" ON video_notes;

-- Create a policy to allow all operations (for testing)
-- WARNING: In production, you should have more restrictive policies!
CREATE POLICY "Allow all operations for testing" ON video_notes
FOR ALL 
USING (true)
WITH CHECK (true);
