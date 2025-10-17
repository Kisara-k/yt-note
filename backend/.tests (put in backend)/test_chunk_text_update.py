"""
Test chunk text update functionality for both books and video chunks
"""

from db.subtitle_chunks_crud import update_chunk_text, get_chunk_details


def test_video_chunk_text_update():
    """Test updating video chunk text"""
    print("\n=== Testing Video Chunk Text Update ===\n")
    
    # Use a test video ID that exists in your database
    test_video_id = "dQw4w9WgXcQ"  # Replace with actual video ID from your DB
    test_chunk_id = 1
    
    print(f"1. Getting original chunk details for video {test_video_id}, chunk {test_chunk_id}...")
    original_chunk = get_chunk_details(test_video_id, test_chunk_id, include_text=True)
    
    if not original_chunk:
        print(f"   ✗ Chunk not found. Please update test_video_id with a valid video ID.")
        return False
    
    original_text = original_chunk.get('chunk_text', '')
    print(f"   ✓ Original text length: {len(original_text) if original_text else 0} chars")
    
    # Update with new text
    print(f"\n2. Updating chunk text...")
    updated_text = f"{original_text}\n\n[TEST UPDATE - This line was added by test_chunk_text_update.py]"
    updated_chunk = update_chunk_text(test_video_id, test_chunk_id, updated_text)
    
    if not updated_chunk:
        print("   ✗ Failed to update chunk text")
        return False
    
    print(f"   ✓ Chunk text updated successfully")
    print(f"   ✓ New text length: {len(updated_text)} chars")
    
    # Verify the update
    print(f"\n3. Verifying update...")
    verified_chunk = get_chunk_details(test_video_id, test_chunk_id, include_text=True)
    
    if not verified_chunk:
        print("   ✗ Failed to retrieve updated chunk")
        return False
    
    verified_text = verified_chunk.get('chunk_text', '')
    if "[TEST UPDATE" in verified_text:
        print("   ✓ Update verified successfully")
        print(f"   ✓ Verified text contains test marker")
    else:
        print("   ✗ Update verification failed - test marker not found")
        return False
    
    print("\n✅ Video chunk text update test PASSED")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("CHUNK TEXT UPDATE TEST")
    print("=" * 60)
    
    success = test_video_chunk_text_update()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ TESTS FAILED")
        print("\nNote: Update test_video_id with a valid video ID from your database")
    print("=" * 60)
