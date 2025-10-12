-- ============================================================
-- YouTube Notes Database Schema
-- ============================================================
-- This schema defines the core tables for storing YouTube video
-- metadata, subtitle chunks, and user notes with AI enrichment
-- ============================================================

-- ============================================================
-- HELPER FUNCTION: Auto-update updated_at timestamp
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TABLE: youtube_videos
-- Stores YouTube video metadata fetched from YouTube API
-- ============================================================

CREATE TABLE youtube_videos (
    -- Primary identifier
    id VARCHAR(20) PRIMARY KEY,
    
    -- YouTube API response fields
    kind VARCHAR(50),
    etag VARCHAR(100),
    
    -- Video metadata
    published_at TIMESTAMPTZ,
    channel_id VARCHAR(50),
    title TEXT,
    description TEXT,
    channel_title VARCHAR(255),
    category_id VARCHAR(10),
    live_broadcast_content VARCHAR(20),
    default_language VARCHAR(10),
    default_audio_language VARCHAR(10),
    tags TEXT[],
    
    -- Video technical details
    duration VARCHAR(20),
    dimension VARCHAR(10),
    definition VARCHAR(10),
    caption BOOLEAN,
    licensed_content BOOLEAN,
    projection VARCHAR(20),
    
    -- Publishing status
    upload_status VARCHAR(20),
    privacy_status VARCHAR(20),
    license VARCHAR(20),
    embeddable BOOLEAN,
    public_stats_viewable BOOLEAN,
    made_for_kids BOOLEAN,
    
    -- Video statistics
    view_count BIGINT,
    like_count BIGINT,
    favorite_count INTEGER,
    comment_count BIGINT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments for youtube_videos
COMMENT ON TABLE youtube_videos IS 'Stores YouTube video metadata and statistics';

-- ============================================================
-- TABLE: subtitle_chunks
-- Stores subtitle text chunks with AI-generated enrichment
-- ============================================================

CREATE TABLE subtitle_chunks (
    -- Composite primary key
    video_id VARCHAR(20) NOT NULL,
    chunk_id INTEGER NOT NULL,
    
    -- Chunk content
    chunk_text TEXT NOT NULL,
    
    -- AI-generated fields (NULL until processed)
    short_title TEXT,
    ai_field_1 TEXT,  -- High-level summary
    ai_field_2 TEXT,  -- Key points
    ai_field_3 TEXT,  -- Topics/themes
    
    -- Timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    PRIMARY KEY (video_id, chunk_id)
);

-- Comments for subtitle_chunks
COMMENT ON TABLE subtitle_chunks IS 'Stores subtitle chunks with AI enrichment';
COMMENT ON COLUMN subtitle_chunks.chunk_text IS 'Full text of this chunk';
COMMENT ON COLUMN subtitle_chunks.short_title IS 'AI-generated short title (NULL if not processed)';
COMMENT ON COLUMN subtitle_chunks.ai_field_1 IS 'AI-generated high-level summary (NULL if not processed)';
COMMENT ON COLUMN subtitle_chunks.ai_field_2 IS 'AI-generated key points (NULL if not processed)';
COMMENT ON COLUMN subtitle_chunks.ai_field_3 IS 'AI-generated topics/themes (NULL if not processed)';

-- ============================================================
-- TABLE: video_notes
-- Stores user-created notes for videos
-- ============================================================

CREATE TABLE video_notes (
    -- Primary key (one note per video)
    video_id VARCHAR(20) PRIMARY KEY,
    
    -- Note content
    note_content TEXT,
    
    -- Custom tags for filtering
    custom_tags TEXT[] DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments for video_notes
COMMENT ON TABLE video_notes IS 'Stores user notes for videos';
COMMENT ON COLUMN video_notes.custom_tags IS 'Array of custom tag strings for filtering';

-- ============================================================
-- INDEXES: Performance optimization
-- ============================================================

-- youtube_videos indexes
CREATE INDEX idx_channel_id ON youtube_videos(channel_id);
CREATE INDEX idx_published_at ON youtube_videos(published_at);
CREATE INDEX idx_created_at ON youtube_videos(created_at);
CREATE INDEX idx_updated_at ON youtube_videos(updated_at);
CREATE INDEX idx_tags ON youtube_videos USING GIN(tags);

-- subtitle_chunks indexes
CREATE INDEX idx_subtitle_chunks_video ON subtitle_chunks(video_id);

-- video_notes indexes
CREATE INDEX idx_video_notes_updated_at ON video_notes(updated_at);
CREATE INDEX idx_video_notes_custom_tags ON video_notes USING GIN(custom_tags);

-- ============================================================
-- FOREIGN KEY CONSTRAINTS: Referential integrity
-- ============================================================

-- subtitle_chunks references youtube_videos
ALTER TABLE subtitle_chunks
    ADD CONSTRAINT fk_subtitle_chunk_video
    FOREIGN KEY (video_id)
    REFERENCES youtube_videos(id)
    ON DELETE CASCADE;

-- video_notes references youtube_videos
ALTER TABLE video_notes
    ADD CONSTRAINT fk_video
    FOREIGN KEY (video_id)
    REFERENCES youtube_videos(id)
    ON DELETE CASCADE;

-- ============================================================
-- TRIGGERS: Auto-update timestamps
-- ============================================================

-- Auto-update youtube_videos.updated_at
CREATE TRIGGER update_youtube_videos_updated_at
    BEFORE UPDATE ON youtube_videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update subtitle_chunks.updated_at
CREATE TRIGGER update_subtitle_chunks_updated_at
    BEFORE UPDATE ON subtitle_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update video_notes.updated_at
CREATE TRIGGER update_video_notes_updated_at
    BEFORE UPDATE ON video_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- ROW LEVEL SECURITY (RLS) - For Supabase compatibility
-- ============================================================
-- Note: These policies allow all operations for testing.
-- In production, implement proper user-based policies.

-- Enable RLS on all tables
ALTER TABLE youtube_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE subtitle_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_notes ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for testing
CREATE POLICY "Allow all operations for testing" 
    ON youtube_videos
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all operations for testing"
    ON subtitle_chunks
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all operations for testing"
    ON video_notes
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- GRANTS: Supabase role permissions
-- ============================================================

-- Grant permissions to Supabase roles
GRANT ALL ON FUNCTION update_updated_at_column() TO anon, authenticated, service_role;
GRANT ALL ON TABLE youtube_videos TO anon, authenticated, service_role;
GRANT ALL ON TABLE subtitle_chunks TO anon, authenticated, service_role;
GRANT ALL ON TABLE video_notes TO anon, authenticated, service_role;

-- ============================================================
-- End of Schema
-- ============================================================
