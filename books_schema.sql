-- ============================================================
-- Books Database Schema (for 2nd Supabase instance)
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
-- TABLE: books
-- Stores book metadata (manually entered by users)
-- ============================================================

CREATE TABLE books (
    -- Primary identifier (user-provided short string)
    id VARCHAR(100) PRIMARY KEY,
    
    -- Book metadata
    title TEXT NOT NULL,
    author VARCHAR(255),
    publisher VARCHAR(255),
    publication_year INTEGER,
    isbn VARCHAR(20),
    description TEXT,
    tags TEXT[],
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_books_updated_at
    BEFORE UPDATE ON books
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE books IS 'Stores book metadata entered by users';

-- ============================================================
-- TABLE: book_chapters
-- Stores book chapter text chunks (similar to subtitle_chunks)
-- ============================================================

CREATE TABLE book_chapters (
    -- Composite primary key
    book_id VARCHAR(100) NOT NULL,
    chapter_id INTEGER NOT NULL,
    
    -- Chapter content (stored in storage bucket)
    chapter_text_path TEXT NOT NULL,  -- Path to text in storage bucket
    
    -- Chapter metadata
    chapter_title TEXT NOT NULL,
    
    -- AI-generated fields (NULL until processed, if ever)
    ai_field_1 TEXT,  -- High-level summary
    ai_field_2 TEXT,  -- Key points
    ai_field_3 TEXT,  -- Topics/themes
    
    -- User notes
    note_content TEXT,  -- User-written markdown notes for this chapter
    
    -- Timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    PRIMARY KEY (book_id, chapter_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_book_chapters_updated_at
    BEFORE UPDATE ON book_chapters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Index for efficient queries
CREATE INDEX idx_book_chapters_book_id ON book_chapters(book_id);

COMMENT ON TABLE book_chapters IS 'Stores book chapter text and AI enrichment';

-- ============================================================
-- TABLE: book_notes
-- Stores overall notes for books (similar to video_notes)
-- ============================================================

CREATE TABLE book_notes (
    book_id VARCHAR(100) PRIMARY KEY,
    note_content TEXT,
    custom_tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Note: ON DELETE NO ACTION - notes persist even if book is deleted
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE NO ACTION
);

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_book_notes_updated_at
    BEFORE UPDATE ON book_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE book_notes IS 'Stores user notes for books';

-- ============================================================
-- STORAGE CLEANUP TRIGGERS
-- ============================================================
-- Note: Actual storage deletion is handled by backend via Supabase Storage API
-- These triggers are for documentation and audit purposes

CREATE OR REPLACE FUNCTION delete_book_storage()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Book % deleted - storage cleanup handled by backend', OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_book_delete
    BEFORE DELETE ON books
    FOR EACH ROW
    EXECUTE FUNCTION delete_book_storage();

CREATE OR REPLACE FUNCTION delete_chapter_storage()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Chapter %/% deleted - storage cleanup handled by backend', 
        OLD.book_id, OLD.chapter_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_chapter_delete
    BEFORE DELETE ON book_chapters
    FOR EACH ROW
    EXECUTE FUNCTION delete_chapter_storage();
