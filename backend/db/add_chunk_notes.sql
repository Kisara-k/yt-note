-- Add note_content field to subtitle_chunks table
-- This allows each chunk to have its own markdown note

ALTER TABLE subtitle_chunks
ADD COLUMN IF NOT EXISTS note_content TEXT;

COMMENT ON COLUMN subtitle_chunks.note_content IS 'User-written markdown notes for this chunk';
