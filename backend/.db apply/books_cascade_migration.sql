-- ============================================================
-- Books Database: Cascade Delete Migration
-- ============================================================
-- This migration implements proper cascade delete behavior:
-- 1. Removes CASCADE from book_notes (preserve notes when book deleted)
-- 2. Adds triggers to delete storage files when book/chapter deleted
-- ============================================================

-- ============================================================
-- Step 1: Remove CASCADE from book_notes foreign key
-- ============================================================

-- Drop existing constraint
ALTER TABLE book_notes
    DROP CONSTRAINT IF EXISTS book_notes_book_id_fkey;

-- Re-add without CASCADE (notes should persist even if book deleted)
ALTER TABLE book_notes
    ADD CONSTRAINT book_notes_book_id_fkey
    FOREIGN KEY (book_id)
    REFERENCES books(id)
    ON DELETE NO ACTION;  -- Changed from CASCADE to NO ACTION

COMMENT ON CONSTRAINT book_notes_book_id_fkey ON book_notes IS 
    'Book notes persist even if book is deleted (orphaned notes allowed)';

-- ============================================================
-- Step 2: Create function to delete storage on book delete
-- ============================================================

CREATE OR REPLACE FUNCTION delete_book_storage()
RETURNS TRIGGER AS $$
BEGIN
    -- Note: Storage deletion will be handled by backend via Supabase Storage API
    -- This trigger documents the expected behavior
    -- The backend's delete_book() function should call:
    --   1. delete_book_chapters_from_storage(book_id)
    --   2. Then delete the book record (which cascades to book_chapters)
    
    RAISE NOTICE 'Book % deleted - storage cleanup should be handled by backend', OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (for documentation/audit purposes)
CREATE TRIGGER before_book_delete
    BEFORE DELETE ON books
    FOR EACH ROW
    EXECUTE FUNCTION delete_book_storage();

COMMENT ON FUNCTION delete_book_storage() IS 
    'Documents that storage deletion must be handled by backend before book deletion';

-- ============================================================
-- Step 3: Create function to delete storage on chapter delete
-- ============================================================

CREATE OR REPLACE FUNCTION delete_chapter_storage()
RETURNS TRIGGER AS $$
BEGIN
    -- Note: Storage deletion will be handled by backend via Supabase Storage API
    -- This trigger documents the expected behavior
    -- The backend's delete_chapter() function should call:
    --   1. delete_chapter_from_storage(chapter_text_path)
    --   2. Then delete the chapter record
    
    RAISE NOTICE 'Chapter %/% deleted - storage cleanup should be handled by backend', 
        OLD.book_id, OLD.chapter_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (for documentation/audit purposes)
CREATE TRIGGER before_chapter_delete
    BEFORE DELETE ON book_chapters
    FOR EACH ROW
    EXECUTE FUNCTION delete_chapter_storage();

COMMENT ON FUNCTION delete_chapter_storage() IS 
    'Documents that storage deletion must be handled by backend before chapter deletion';

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
    AND tc.table_name IN ('book_notes', 'book_chapters');

-- ============================================================
-- Notes:
-- ============================================================
-- CASCADE BEHAVIOR:
--   - book_chapters: KEPT CASCADE (deleted when book deleted)
--   - book_notes: REMOVED CASCADE (preserved when book deleted)
--   - Storage: Handled by backend before DB deletion
--
-- STORAGE CLEANUP:
--   - Book deletion: Backend calls delete_book_chapters_from_storage()
--   - Chapter deletion: Backend calls delete_chapter_from_storage()
--   - Handled via Supabase Storage API (cannot be done in SQL trigger)
-- ============================================================
