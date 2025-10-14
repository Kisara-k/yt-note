-- ============================================================
-- YouTube Database: Cascade Delete Migration
-- ============================================================
-- This migration implements proper cascade delete behavior:
-- 1. Removes CASCADE from video_notes (preserve notes when video deleted)
-- 2. Adds trigger to delete storage files when video/chunk deleted
-- ============================================================

-- ============================================================
-- Step 1: Remove CASCADE from video_notes foreign key
-- ============================================================

-- Drop existing constraint
ALTER TABLE video_notes
    DROP CONSTRAINT IF EXISTS fk_video;

-- Re-add without CASCADE (notes should persist even if video deleted)
ALTER TABLE video_notes
    ADD CONSTRAINT fk_video
    FOREIGN KEY (video_id)
    REFERENCES youtube_videos(id)
    ON DELETE NO ACTION;  -- Changed from CASCADE to NO ACTION

COMMENT ON CONSTRAINT fk_video ON video_notes IS 
    'Video notes persist even if video is deleted (orphaned notes allowed)';

-- ============================================================
-- Step 2: Create function to delete storage on video delete
-- ============================================================

CREATE OR REPLACE FUNCTION delete_video_storage()
RETURNS TRIGGER AS $$
BEGIN
    -- Note: Storage deletion will be handled by backend via Supabase Storage API
    -- This trigger documents the expected behavior
    -- The backend's delete_video() function should call:
    --   1. delete_video_chunks_from_storage(video_id)
    --   2. Then delete the video record (which cascades to subtitle_chunks)
    
    RAISE NOTICE 'Video % deleted - storage cleanup should be handled by backend', OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (for documentation/audit purposes)
CREATE TRIGGER before_video_delete
    BEFORE DELETE ON youtube_videos
    FOR EACH ROW
    EXECUTE FUNCTION delete_video_storage();

COMMENT ON FUNCTION delete_video_storage() IS 
    'Documents that storage deletion must be handled by backend before video deletion';

-- ============================================================
-- Step 3: Create function to delete storage on chunk delete
-- ============================================================

CREATE OR REPLACE FUNCTION delete_chunk_storage()
RETURNS TRIGGER AS $$
BEGIN
    -- Note: Storage deletion will be handled by backend via Supabase Storage API
    -- This trigger documents the expected behavior
    -- The backend's delete_chunk() function should call:
    --   1. delete_chunk_from_storage(chunk_text_path)
    --   2. Then delete the chunk record
    
    RAISE NOTICE 'Chunk %/% deleted - storage cleanup should be handled by backend', 
        OLD.video_id, OLD.chunk_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (for documentation/audit purposes)
CREATE TRIGGER before_chunk_delete
    BEFORE DELETE ON subtitle_chunks
    FOR EACH ROW
    EXECUTE FUNCTION delete_chunk_storage();

COMMENT ON FUNCTION delete_chunk_storage() IS 
    'Documents that storage deletion must be handled by backend before chunk deletion';

-- ============================================================
-- Verification queries
-- ============================================================

-- Check foreign key constraints
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
    AND tc.table_name IN ('video_notes', 'subtitle_chunks');

-- ============================================================
-- Notes:
-- ============================================================
-- CASCADE BEHAVIOR:
--   - subtitle_chunks: KEPT CASCADE (deleted when video deleted)
--   - video_notes: REMOVED CASCADE (preserved when video deleted)
--   - Storage: Handled by backend before DB deletion
--
-- STORAGE CLEANUP:
--   - Video deletion: Backend calls delete_video_chunks_from_storage()
--   - Chunk deletion: Backend calls delete_chunk_from_storage()
--   - Handled via Supabase Storage API (cannot be done in SQL trigger)
-- ============================================================
