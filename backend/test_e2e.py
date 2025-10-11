"""
End-to-end test: Verify full pipeline with database
Tests: YouTube metadata → Subtitles → AI enrichment → Database storage
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("END-TO-END DATABASE TEST")
print("="*70)

# Test video (short for quick testing)
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
TEST_VIDEO_ID = "dQw4w9WgXcQ"

print(f"\nTest video: {TEST_VIDEO_URL}")
print("="*70)

def test_1_metadata():
    """Test 1: Fetch and store video metadata"""
    print("\n[TEST 1] Video Metadata → Database")
    print("-"*70)
    
    try:
        from orchestrator import process_video_metadata
        from db.youtube_crud import get_video_by_id
        
        # Process metadata
        metadata = process_video_metadata(TEST_VIDEO_URL)
        
        if not metadata:
            print("✗ Failed to fetch metadata")
            return False
        
        print(f"✓ Fetched metadata")
        print(f"  Title: {metadata['title'][:50]}...")
        print(f"  Channel: {metadata['channel_title']}")
        
        # Verify database
        db_video = get_video_by_id(TEST_VIDEO_ID)
        
        if not db_video:
            print("✗ Video not found in database")
            return False
        
        print(f"✓ Video stored in database")
        print(f"  DB Title: {db_video['title'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_subtitles():
    """Test 2: Extract and chunk subtitles"""
    print("\n[TEST 2] Subtitles → Chunks")
    print("-"*70)
    
    try:
        from orchestrator import process_video_subtitles
        
        chunks = process_video_subtitles(TEST_VIDEO_ID)
        
        if not chunks:
            print("✗ No chunks created")
            return False
        
        print(f"✓ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3]):
            print(f"  Chunk {i}: {chunk['word_count']} words, {chunk['sentence_count']} sentences")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_ai_enrichment():
    """Test 3: AI enrichment (uses API credits)"""
    print("\n[TEST 3] AI Enrichment")
    print("-"*70)
    print("Note: This test will use OpenAI API credits if API key is configured.")
    
    try:
        from orchestrator import process_video_subtitles, process_chunks_enrichment_parallel
        
        chunks = process_video_subtitles(TEST_VIDEO_ID)
        
        if not chunks:
            print("✗ No chunks to enrich")
            return False
        
        print(f"Enriching {len(chunks)} chunks in parallel...")
        enriched = process_chunks_enrichment_parallel(chunks)
        
        print(f"✓ Enriched {len(enriched)} chunks")
        for i, chunk in enumerate(enriched[:2]):
            print(f"\n  Chunk {i}:")
            print(f"    Title: {chunk.get('title', 'N/A')[:60]}")
            print(f"    Field 1: {chunk.get('field_1', 'N/A')[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_full_pipeline():
    """Test 4: Full pipeline with database storage"""
    print("\n[TEST 4] Full Pipeline → Database")
    print("-"*70)
    print("Running: extract → chunk → enrich → save to database")
    
    try:
        from orchestrator import process_full_video
        from db.subtitle_chunks_crud import get_chunks_by_video
        
        print(f"\nProcessing video: {TEST_VIDEO_ID}")
        success = process_full_video(TEST_VIDEO_ID)
        
        if not success:
            print("✗ Pipeline failed")
            return False
        
        print("\n✓ Pipeline completed")
        
        # Verify chunks in database
        db_chunks = get_chunks_by_video(TEST_VIDEO_ID)
        
        if not db_chunks:
            print("✗ No chunks found in database")
            return False
        
        print(f"✓ Found {len(db_chunks)} chunks in database")
        
        # Show sample chunk
        if db_chunks:
            sample = db_chunks[0]
            print(f"\nSample chunk from database:")
            print(f"  Chunk ID: {sample['chunk_id']}")
            print(f"  Word count: {sample.get('word_count', 'N/A')}")
            print(f"  Sentence count: {sample.get('sentence_count', 'N/A')}")
            short_title = sample.get('short_title')
            if short_title:
                print(f"  Title: {short_title[:50]}")
            chunk_text = sample.get('chunk_text', '')
            if chunk_text:
                print(f"  Text preview: {chunk_text[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_notes():
    """Test 5: Create and retrieve notes"""
    print("\n[TEST 5] Notes → Database")
    print("-"*70)
    
    try:
        from db.video_notes_crud import create_or_update_note, get_note_by_video_id
        
        # Create note
        test_note = "This is a test note for end-to-end testing."
        note = create_or_update_note(
            video_id=TEST_VIDEO_ID,
            note_content=test_note,
            custom_tags=["test", "e2e"]
        )
        
        if not note:
            print("✗ Failed to create note")
            return False
        
        print(f"✓ Created note")
        print(f"  Content: {note['note_content'][:50]}...")
        
        # Retrieve note
        retrieved = get_note_by_video_id(TEST_VIDEO_ID)
        
        if not retrieved:
            print("✗ Failed to retrieve note")
            return False
        
        print(f"✓ Retrieved note from database")
        print(f"  Content: {retrieved['note_content'][:50]}...")
        print(f"  Tags: {retrieved.get('custom_tags', [])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    results = []
    
    results.append(("Metadata → DB", test_1_metadata()))
    results.append(("Subtitles → Chunks", test_2_subtitles()))
    results.append(("AI Enrichment", test_3_ai_enrichment()))
    results.append(("Full Pipeline → DB", test_4_full_pipeline()))
    results.append(("Notes → DB", test_5_notes()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Database integration verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(1)
