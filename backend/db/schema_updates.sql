-- ===================================================
-- Schema Updates for YouTube Notes Application
-- ===================================================

-- Drop unused tables
DROP TABLE IF EXISTS job_queue CASCADE;
DROP TABLE IF EXISTS tag_keys CASCADE;

-- Remove custom_tag_keys from youtube_videos (moved to video_notes)
ALTER TABLE youtube_videos DROP COLUMN IF EXISTS custom_tag_keys;
DROP INDEX IF EXISTS idx_custom_tag_keys;

-- ===================================================
-- 1. Update video_notes table - Add custom_tags
-- ===================================================

ALTER TABLE video_notes 
ADD COLUMN IF NOT EXISTS custom_tags TEXT[] DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_video_notes_custom_tags ON video_notes USING GIN(custom_tags);

COMMENT ON COLUMN video_notes.custom_tags IS 'Array of custom tag strings for filtering';

-- ===================================================
-- Summary
-- ===================================================

SELECT 
    'youtube_videos' as table_name, COUNT(*) as row_count FROM youtube_videos
UNION ALL
SELECT 'video_notes', COUNT(*) FROM video_notes
UNION ALL
SELECT 'subtitle_chunks', COUNT(*) FROM subtitle_chunks
ORDER BY table_name;

