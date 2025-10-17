# Book Prompts Implementation

## Overview

Books now use specialized AI prompts that are different from video prompts for enriching chapter sections with AI-generated content.

## What Changed

### Prompts File (`backend/prompts.py`)

**Added:**

- `BOOK_PROMPTS` dictionary with book-specific prompt templates
- `VIDEO_PROMPTS` renamed from `PROMPTS` for clarity
- All functions now accept `content_type` parameter ('video' or 'book')

**Book Prompts vs Video Prompts:**

| Field        | Video Label        | Book Label         |
| ------------ | ------------------ | ------------------ |
| `ai_field_1` | High-Level Summary | Chapter Summary    |
| `ai_field_2` | Key Points         | Important Concepts |
| `ai_field_3` | Topics/Themes      | Key Insights       |

**Prompt Language Differences:**

- Videos: "video segment" → Books: "book chapter section"
- Videos: "main ideas and key takeaways" → Books: "main concepts, arguments, or narrative developments"
- Videos: "bullet points" → Books: "concepts with brief explanations"
- Videos: "topics or themes" → Books: "actionable insights or important lessons"

### Orchestrator (`backend/orchestrator.py`)

**Updated:**

- `process_chunks_enrichment_parallel()` now accepts `content_type` parameter
- Passes `content_type='video'` by default for backward compatibility
- Book enrichment will use `content_type='book'` when implemented

### API (`backend/api.py`)

**Updated:**

- `/api/prompts` endpoint now accepts `?content_type=video` or `?content_type=book` query parameter
- Returns appropriate prompt set based on content type
- Defaults to 'video' for backward compatibility

## How to Use

### Get Book Prompts in API

```bash
GET /api/prompts?content_type=book
```

Returns:

```json
{
  "prompts": [
    {
      "field_name": "title",
      "label": "Short Title",
      "template": "Create a concise title (max 10 words) that captures the main topic of this book chapter section..."
    },
    ...
  ],
  "count": 4,
  "content_type": "book"
}
```

### Enrich Book Chapters in Code

```python
from orchestrator import process_chunks_enrichment_parallel

# For book chapters
enriched_chapters = process_chunks_enrichment_parallel(
    chunks=chapter_chunks,
    content_type='book'  # Use book prompts
)

# For video subtitles (default)
enriched_subtitles = process_chunks_enrichment_parallel(
    chunks=subtitle_chunks,
    content_type='video'  # Or omit - defaults to 'video'
)
```

## Testing

Run the test script to verify prompts are different:

```bash
cd backend
python test_book_prompts.py
```

Expected output:

```
✓ title: Video and book prompts are DIFFERENT
✓ field_1: Video and book prompts are DIFFERENT
✓ field_2: Video and book prompts are DIFFERENT
✓ field_3: Video and book prompts are DIFFERENT

✓ SUCCESS: All book prompts are different from video prompts
```

## Backward Compatibility

✅ All existing code continues to work without changes
✅ Default behavior unchanged (uses video prompts)
✅ Only new book enrichment code needs to specify `content_type='book'`

## Next Steps

To implement book chapter enrichment:

1. Create book chunking logic (similar to subtitle chunking)
2. Call `process_chunks_enrichment_parallel(chunks, content_type='book')`
3. Store enriched fields in book_chapters table/storage
4. Display in frontend ChunkViewer

## Files Modified

- ✅ `backend/prompts.py` - Added book prompts and content_type parameter
- ✅ `backend/orchestrator.py` - Added content_type parameter to enrichment function
- ✅ `backend/api.py` - Updated /api/prompts endpoint to accept content_type
- ✅ `backend/test_book_prompts.py` - New test file
- ✅ `CHANGELOG.md` - Documented changes
