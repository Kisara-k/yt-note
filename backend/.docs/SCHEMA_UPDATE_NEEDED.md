# Database Schema Update Required

## Issue

The `subtitle_chunks` table schema in Supabase needs to be updated to support the new word-based chunking system.

## Required Changes

Run this SQL in your Supabase SQL editor:

```sql
-- Remove old time-based columns
ALTER TABLE subtitle_chunks DROP COLUMN IF EXISTS start_time;
ALTER TABLE subtitle_chunks DROP COLUMN IF EXISTS end_time;

-- Add new word-based columns
ALTER TABLE subtitle_chunks ADD COLUMN IF NOT EXISTS word_count INTEGER;
ALTER TABLE subtitle_chunks ADD COLUMN IF NOT EXISTS sentence_count INTEGER;

-- Add comments
COMMENT ON COLUMN subtitle_chunks.word_count IS 'Number of words in this chunk';
COMMENT ON COLUMN subtitle_chunks.sentence_count IS 'Number of sentences in this chunk';
```

## Verify Schema

After running the SQL, verify in Supabase:

1. Go to Table Editor → subtitle_chunks
2. Check that columns exist:
   - ✅ video_id
   - ✅ chunk_id
   - ✅ chunk_text
   - ✅ word_count (new)
   - ✅ sentence_count (new)
   - ✅ short_title
   - ✅ ai_field_1, ai_field_2, ai_field_3
   - ❌ start_time (removed)
   - ❌ end_time (removed)

## Refresh Schema Cache

If you still get "column not found" errors:

1. Go to Settings → API
2. Click "Reload schema cache" or restart PostgREST

## Test

After updating, run:

```bash
python test_e2e.py
```

All tests should pass.
