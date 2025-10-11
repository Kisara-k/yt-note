-- ===================================================
-- Update video_notes table to remove user_email column
-- ===================================================

-- Remove the user_email column from video_notes table
ALTER TABLE video_notes DROP COLUMN IF EXISTS user_email;

-- Drop the index on user_email if it exists
DROP INDEX IF EXISTS idx_video_notes_user_email;

-- The table now only has:
-- - video_id (PRIMARY KEY)
-- - note_content (TEXT)
-- - created_at (TIMESTAMPTZ)
-- - updated_at (TIMESTAMPTZ)

-- Note: Authentication is now handled via Supabase Auth
-- Only verified emails (hardcoded in backend/config.py) can access the application
