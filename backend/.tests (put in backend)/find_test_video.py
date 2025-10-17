"""Quick script to find videos with chunks for testing"""
from db.youtube_crud import get_all_videos
from db.subtitle_chunks_crud import get_chunks_by_video

videos = get_all_videos(limit=10)
print('\n=== Videos with chunks ===\n')

videos_with_chunks = []
for v in videos:
    chunks = get_chunks_by_video(v['id'])
    if len(chunks) > 0:
        print(f"✓ {v['id']}: {v['title'][:60]}...")
        print(f"  Chunks: {len(chunks)}")
        videos_with_chunks.append((v['id'], len(chunks)))

if not videos_with_chunks:
    print("No videos with chunks found.")
    print("\nTo test the feature:")
    print("1. Process a video through the frontend")
    print("2. Or run: python main.py (in backend) and use the API to process a video")
else:
    print(f"\n✅ Found {len(videos_with_chunks)} videos with chunks")
    print(f"\nTest with video ID: {videos_with_chunks[0][0]}")
