from db.subtitle_chunks_crud import get_chunks_by_video
chunks = get_chunks_by_video('dQw4w9WgXcQ')
if chunks:
    print(f"Chunks found: {len(chunks)}")
    print(f"Has short_title: {bool(chunks[0].get('short_title'))}")
    print(f"Has ai_field_1: {bool(chunks[0].get('ai_field_1'))}")
    if chunks[0].get('short_title'):
        print(f"Title: {chunks[0]['short_title'][:60]}")
