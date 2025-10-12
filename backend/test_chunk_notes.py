"""
Test script to verify chunk notes functionality
Run this after applying the schema update
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import after adding to path
from db.subtitle_chunks_crud import get_chunks_by_video, update_chunk_note, get_chunk_details

load_dotenv()

def test_chunk_notes():
    """Test chunk note functionality"""
    print("\n=== Testing Chunk Notes Functionality ===\n")
    
    # Test 1: Check if we can query chunks
    print("Test 1: Querying existing chunks...")
    chunks = get_chunks_by_video("test_video_id")
    
    if chunks:
        print(f"✓ Found {len(chunks)} chunks")
        
        # Test 2: Try updating a note
        test_video_id = chunks[0]['video_id']
        test_chunk_id = chunks[0]['chunk_id']
        test_note = "# Test Note\n\nThis is a test markdown note."
        
        print(f"\nTest 2: Updating note for chunk {test_chunk_id}...")
        result = update_chunk_note(test_video_id, test_chunk_id, test_note)
        
        if result:
            print(f"✓ Successfully updated note")
            
            # Test 3: Verify note was saved
            print(f"\nTest 3: Retrieving chunk with note...")
            chunk = get_chunk_details(test_video_id, test_chunk_id, include_text=False)
            
            if chunk and 'note_content' in chunk:
                print(f"✓ Note content retrieved: {chunk['note_content'][:50]}...")
                print("\n✅ All tests passed! Chunk notes functionality is working.")
            else:
                print("✗ Failed to retrieve note content")
                print("❌ Tests failed - note_content column may not exist yet")
        else:
            print("✗ Failed to update note")
            print("❌ Tests failed - check if schema was applied")
    else:
        print("ℹ No existing chunks found. This is OK if database is empty.")
        print("✅ Setup is ready - create some chunks to test notes functionality")

if __name__ == "__main__":
    try:
        test_chunk_notes()
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print("\nMake sure to:")
        print("1. Run the SQL in Supabase SQL Editor:")
        print("   ALTER TABLE subtitle_chunks ADD COLUMN IF NOT EXISTS note_content TEXT;")
        print("2. Ensure there are chunks in the database to test with")
