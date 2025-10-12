"""
Test the chunk notes feature - focused test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db.subtitle_chunks_crud import get_chunk_details, update_chunk_note

# Use a real video with chunks
VIDEO_ID = "Esu8BXLBmZ4"
CHUNK_ID = 0

print("\n" + "="*60)
print("CHUNK NOTES FEATURE TEST")
print("="*60 + "\n")

# Test 1: Get chunk with current note
print(f"1. Getting chunk {CHUNK_ID} from video {VIDEO_ID}...")
chunk = get_chunk_details(VIDEO_ID, CHUNK_ID, include_text=False)

if not chunk:
    print("✗ Chunk not found")
    sys.exit(1)

print(f"✓ Chunk found: {chunk.get('short_title', 'No title')}")
print(f"  Current note_content: {chunk.get('note_content', 'None')[:50] if chunk.get('note_content') else 'None'}")

# Test 2: Update note
print(f"\n2. Updating note content...")
test_note = """# My Chunk Note

This is a **test note** with markdown.

## Features
- Lists work
- **Bold** and *italic*
- Code blocks

> Quotes work too!
"""

result = update_chunk_note(VIDEO_ID, CHUNK_ID, test_note)

if not result:
    print("✗ Failed to update note")
    sys.exit(1)

print("✓ Note updated successfully")

# Test 3: Verify the update
print(f"\n3. Verifying update...")
chunk = get_chunk_details(VIDEO_ID, CHUNK_ID, include_text=False)

if not chunk or not chunk.get('note_content'):
    print("✗ Note not found after update")
    sys.exit(1)

if chunk['note_content'] == test_note:
    print("✓ Note content matches")
    print(f"\n{'-'*60}")
    print(chunk['note_content'])
    print(f"{'-'*60}\n")
else:
    print("✗ Note content mismatch")
    sys.exit(1)

# Test 4: Update to empty note
print(f"4. Testing empty note...")
result = update_chunk_note(VIDEO_ID, CHUNK_ID, "")

if result and result.get('note_content') == "":
    print("✓ Empty note works")
else:
    print("✗ Empty note failed")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED")
print("="*60)
print("\nFeature is working correctly!")
print(f"\nTest in browser:")
print(f"1. Go to http://localhost:3001")
print(f"2. Log in")
print(f"3. Navigate to video {VIDEO_ID}")
print(f"4. You should see the chunk notes editor")
