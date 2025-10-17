"""Quick check of chunk IDs for a specific video"""
from db.subtitle_chunks_crud import get_chunks_by_video

video_id = "Esu8BXLBmZ4"
chunks = get_chunks_by_video(video_id)

print(f"\nChunks for video {video_id}:")
for chunk in chunks:
    print(f"  chunk_id: {chunk['chunk_id']}, path: {chunk.get('chunk_text_path', 'N/A')}")
