"""
Integration test - Test full video processing pipeline
Tests orchestrator with real video
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("INTEGRATION TEST - FULL VIDEO PROCESSING")
print("="*70)

# Test full pipeline
test_video_id = "dQw4w9WgXcQ"  # Short video for testing

print(f"\nTest video: {test_video_id}")
print("="*70)

try:
    from orchestrator import (
        process_video_metadata,
        process_video_subtitles,
        process_chunks_enrichment_parallel,
        process_full_video
    )
    
    # Step 1: Metadata
    print("\n[1/4] Fetching metadata...")
    metadata = process_video_metadata(f"https://www.youtube.com/watch?v={test_video_id}")
    
    if metadata:
        print(f"✓ Title: {metadata['title']}")
        print(f"✓ Channel: {metadata['channel_title']}")
    else:
        print("✗ Failed to fetch metadata")
        sys.exit(1)
    
    # Step 2: Subtitles
    print("\n[2/4] Extracting and chunking subtitles...")
    chunks = process_video_subtitles(test_video_id)
    
    if chunks:
        print(f"✓ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3
            print(f"  Chunk {i}: {chunk['word_count']} words, {chunk['sentence_count']} sentences")
    else:
        print("✗ No chunks created")
        sys.exit(1)
    
    # Step 3: AI Enrichment (parallel)
    print("\n[3/4] Enriching chunks with AI (parallel)...")
    print("Note: This will use OpenAI API credits")
    
    response = input("Proceed with AI enrichment? (y/n): ")
    
    if response.lower() == 'y':
        enriched = process_chunks_enrichment_parallel(chunks)
        
        print(f"✓ Enriched {len(enriched)} chunks")
        for i, chunk in enumerate(enriched[:2]):
            print(f"\n  Chunk {i}:")
            print(f"    Title: {chunk.get('title', 'N/A')[:60]}")
            print(f"    Field 1: {chunk.get('field_1', 'N/A')[:60]}")
    else:
        print("⊘ Skipped AI enrichment")
    
    # Step 4: Full pipeline test (optional)
    print("\n[4/4] Test full pipeline?")
    print("This will: extract → chunk → enrich → save to DB")
    
    response = input("Run full pipeline test? (y/n): ")
    
    if response.lower() == 'y':
        print(f"\nProcessing full video: {test_video_id}")
        success = process_full_video(test_video_id)
        
        if success:
            print("✓ Full pipeline completed successfully!")
        else:
            print("✗ Pipeline failed")
    else:
        print("⊘ Skipped full pipeline test")
    
    print("\n" + "="*70)
    print("INTEGRATION TEST COMPLETE")
    print("="*70)
    
except KeyboardInterrupt:
    print("\n\nTest cancelled by user")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
