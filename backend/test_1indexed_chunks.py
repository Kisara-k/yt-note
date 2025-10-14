"""
Test script to verify 1-indexed video chunks implementation

Tests:
1. Chunk creation starts from 1
2. Bulk chunk creation uses 1-indexed IDs
3. Chunk retrieval by ID works correctly
4. Chunk index displays correct IDs
"""

from db.subtitle_chunks_crud import (
    create_chunk,
    bulk_create_chunks,
    get_chunk_details,
    get_chunk_index,
    delete_chunks_by_video
)
from db.subtitle_chunks_storage import upload_chunk_text
from db.youtube_crud import create_or_update_video

def test_1indexed_chunks():
    """Test that video chunks use 1-indexed IDs"""
    test_video_id = "test_1indexed_video"
    
    print("\n" + "="*60)
    print("Testing 1-Indexed Video Chunks")
    print("="*60)
    
    # Clean up any existing test data
    print("\n[Setup] Cleaning up existing test data...")
    delete_chunks_by_video(test_video_id)
    
    # Create test video in database
    print("[Setup] Creating test video...")
    test_video_data = {
        'id': test_video_id,
        'snippet': {
            'title': 'Test Video for 1-indexed chunks',
            'channelTitle': 'Test Channel',
            'channelId': 'test_channel'
        }
    }
    create_or_update_video(test_video_data)
    
    # Test 1: Create individual chunks starting from 1
    print("\n[Test 1] Creating chunks with IDs 1, 2, 3...")
    chunk1 = create_chunk(
        video_id=test_video_id,
        chunk_id=1,
        chunk_text="This is chunk 1",
        short_title="Chunk One"
    )
    chunk2 = create_chunk(
        video_id=test_video_id,
        chunk_id=2,
        chunk_text="This is chunk 2",
        short_title="Chunk Two"
    )
    chunk3 = create_chunk(
        video_id=test_video_id,
        chunk_id=3,
        chunk_text="This is chunk 3",
        short_title="Chunk Three"
    )
    
    if chunk1 and chunk2 and chunk3:
        print(f"✅ Created chunk 1: {chunk1['short_title']}")
        print(f"✅ Created chunk 2: {chunk2['short_title']}")
        print(f"✅ Created chunk 3: {chunk3['short_title']}")
    else:
        print("❌ Failed to create chunks")
        return False
    
    # Test 2: Retrieve chunk by ID
    print("\n[Test 2] Retrieving chunk with ID=1...")
    retrieved_chunk = get_chunk_details(test_video_id, 1)
    
    if retrieved_chunk and retrieved_chunk['chunk_id'] == 1:
        print(f"✅ Retrieved chunk 1: {retrieved_chunk['short_title']}")
    else:
        print(f"❌ Failed to retrieve chunk 1")
        return False
    
    # Test 3: Get chunk index
    print("\n[Test 3] Getting chunk index...")
    chunk_index = get_chunk_index(test_video_id)
    
    if len(chunk_index) == 3:
        print(f"✅ Chunk index has 3 chunks")
        print(f"   Chunk IDs: {[c['chunk_id'] for c in chunk_index]}")
        
        # Verify IDs are 1, 2, 3
        expected_ids = [1, 2, 3]
        actual_ids = [c['chunk_id'] for c in chunk_index]
        
        if actual_ids == expected_ids:
            print(f"✅ Chunk IDs are correct: {actual_ids}")
        else:
            print(f"❌ Chunk IDs incorrect. Expected {expected_ids}, got {actual_ids}")
            return False
    else:
        print(f"❌ Expected 3 chunks, got {len(chunk_index)}")
        return False
    
    # Test 4: Bulk create chunks (simulating orchestrator behavior)
    print("\n[Test 4] Testing bulk create with 1-indexed IDs...")
    test_video_id2 = "test_bulk_1indexed"
    delete_chunks_by_video(test_video_id2)
    
    # Create second test video
    test_video_data2 = {
        'id': test_video_id2,
        'snippet': {
            'title': 'Test Video 2 for bulk',
            'channelTitle': 'Test Channel',
            'channelId': 'test_channel'
        }
    }
    create_or_update_video(test_video_data2)
    
    bulk_chunks = [
        {
            'video_id': test_video_id2,
            'chunk_id': i + 1,  # 1-indexed
            'chunk_text': f"Bulk chunk {i + 1} content",
            'short_title': f"Bulk Chunk {i + 1}",
            'ai_field_1': None,
            'ai_field_2': None,
            'ai_field_3': None
        }
        for i in range(5)  # Create 5 chunks
    ]
    
    result = bulk_create_chunks(bulk_chunks)
    
    if result and len(result) == 5:
        created_ids = [c['chunk_id'] for c in result]
        expected_ids = [1, 2, 3, 4, 5]
        
        print(f"✅ Bulk created 5 chunks")
        print(f"   Chunk IDs: {created_ids}")
        
        if created_ids == expected_ids:
            print(f"✅ Bulk chunk IDs are correct: {created_ids}")
        else:
            print(f"❌ Bulk chunk IDs incorrect. Expected {expected_ids}, got {created_ids}")
            return False
    else:
        print(f"❌ Bulk create failed")
        return False
    
    # Cleanup
    print("\n[Cleanup] Removing test data...")
    delete_chunks_by_video(test_video_id)
    delete_chunks_by_video(test_video_id2)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - Chunks are 1-indexed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_1indexed_chunks()
    exit(0 if success else 1)
