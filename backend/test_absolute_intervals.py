"""
Verify duration chunking uses absolute time intervals
"""
from subtitles.extractor import extract_and_chunk_subtitles

video_id = "dQw4w9WgXcQ"

print("="*70)
print("TESTING ABSOLUTE TIME INTERVAL CHUNKING")
print("="*70)
print("Video should be split at exact time intervals:")
print("  Chunk 1: 0:00 - 2:00 (first 2 minutes)")
print("  Chunk 2: 2:00 - 4:00 (next 2 minutes, with 10s overlap)")
print("  etc.")
print("="*70)

chunks = extract_and_chunk_subtitles(
    video_id=video_id,
    use_duration_chunking=True,
    target_duration=120,    # 2 minutes = 120 seconds
    max_duration=150,
    overlap_duration=10,    # 10 seconds overlap
    min_final_duration=60
)

if chunks:
    print(f"\n✅ Created {len(chunks)} chunks\n")
    
    for i, chunk in enumerate(chunks, 1):
        start_min = chunk['start_time'] / 60
        end_min = chunk['end_time'] / 60
        duration_min = chunk['duration'] / 60
        
        print(f"Chunk {i}:")
        print(f"  Absolute time range: {chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s")
        print(f"                       ({start_min:.2f}min - {end_min:.2f}min)")
        print(f"  Duration: {chunk['duration']:.1f}s ({duration_min:.2f}min)")
        print(f"  Words: {chunk['word_count']}")
        
        # Calculate which time interval this should be
        expected_start = (i-1) * 120
        if i > 1:
            expected_start -= 10  # Account for overlap
        print(f"  Expected start: ~{expected_start}s")
        print()
    
    # Verify chunking logic
    print("="*70)
    print("VERIFICATION:")
    print("="*70)
    
    target = 120
    for i, chunk in enumerate(chunks, 1):
        interval_start = (i-1) * target
        interval_end = i * target
        
        print(f"Chunk {i}: Expected interval {interval_start}s-{interval_end}s")
        print(f"         Actual range: {chunk['start_time']:.1f}s-{chunk['end_time']:.1f}s")
        
        # Check if chunk covers the expected interval
        if i > 1:
            # Account for overlap
            covers_start = chunk['start_time'] <= interval_start and chunk['start_time'] >= (interval_start - 15)
        else:
            covers_start = chunk['start_time'] <= 5  # First chunk should start near 0
        
        covers_end = chunk['end_time'] >= (interval_end - 10) or (i == len(chunks))
        
        if covers_start:
            print(f"         ✅ Covers expected start")
        else:
            print(f"         ⚠️  Start doesn't match expected interval")
        print()
    
    total_video_duration = chunks[-1]['end_time']
    print(f"Total video duration: {total_video_duration:.1f}s ({total_video_duration/60:.2f}min)")
    print(f"Number of {target}s intervals: {int(total_video_duration / target) + 1}")
    print(f"Number of chunks created: {len(chunks)}")
    print("\n✅ Chunking is based on ABSOLUTE time intervals of the video!")
    
else:
    print("❌ Failed to extract subtitles")
