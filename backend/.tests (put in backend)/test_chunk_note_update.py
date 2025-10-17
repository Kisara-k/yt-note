"""Test chunk notes with a real video"""
from db.subtitle_chunks_crud import get_chunk_details, update_chunk_note

test_video_id = "Esu8BXLBmZ4"
test_chunk_id = 0

print(f"\n=== Testing Chunk Notes with {test_video_id} ===\n")

# Get current chunk details
print(f"1. Getting chunk {test_chunk_id}...")
chunk = get_chunk_details(test_video_id, test_chunk_id, include_text=False)

if chunk:
    print(f"✓ Found chunk")
    print(f"  Short title: {chunk.get('short_title', 'N/A')}")
    print(f"  Current note: {chunk.get('note_content', 'None')}")
    
    # Update the note
    print(f"\n2. Updating note content...")
    test_note = """# Test Chunk Note

This is a **markdown** note for this chunk.

## Key Points
- Point 1
- Point 2
- Point 3

> This is a quote

```python
# Code example
print("Hello from chunk note!")
```
"""
    
    result = update_chunk_note(test_video_id, test_chunk_id, test_note)
    
    if result:
        print("✓ Note updated successfully")
        
        # Verify it was saved
        print(f"\n3. Verifying note was saved...")
        chunk = get_chunk_details(test_video_id, test_chunk_id, include_text=False)
        
        if chunk and chunk.get('note_content'):
            print(f"✓ Note retrieved successfully")
            print(f"\nSaved note preview:")
            print("-" * 60)
            print(chunk['note_content'][:200] + "...")
            print("-" * 60)
            print("\n✅ ALL TESTS PASSED!")
            print("\n🎉 Chunk notes feature is working correctly!")
        else:
            print("✗ Note not found after save")
    else:
        print("✗ Failed to update note")
else:
    print("✗ Chunk not found")
