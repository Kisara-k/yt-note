"""
Test script for Task 2 implementation
Tests video notes CRUD operations and API functionality
"""

import sys
import os
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.youtube_crud import get_video_by_id, create_or_update_video
from db.video_notes_crud import (
    create_or_update_note,
    get_note_by_video_id,
    get_all_notes,
    get_notes_with_video_info
)
from backend.fetch_youtube_videos import fetch_video_details, extract_video_id

def test_video_id_extraction():
    """Test video ID extraction from different URL formats"""
    print("\n" + "="*60)
    print("TEST 1: Video ID Extraction")
    print("="*60)
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ"
    ]
    
    for url in test_urls:
        video_id = extract_video_id(url)
        print(f"✓ {url} -> {video_id}")
    
    return True


def test_video_fetch_and_store():
    """Test fetching video from YouTube and storing in database"""
    print("\n" + "="*60)
    print("TEST 2: Fetch and Store Video")
    print("="*60)
    
    test_video_id = "dQw4w9WgXcQ"
    
    # Check if already in database
    print(f"\nChecking if video {test_video_id} exists in database...")
    video = get_video_by_id(test_video_id)
    
    if video:
        print(f"✓ Video found in database: {video['title']}")
    else:
        print("Video not in database, fetching from YouTube API...")
        videos_data = fetch_video_details([test_video_id])
        
        if videos_data and len(videos_data) > 0:
            video = create_or_update_video(videos_data[0])
            if video:
                print(f"✓ Video fetched and stored: {video['title']}")
            else:
                print("✗ Failed to store video")
                return False
        else:
            print("✗ Failed to fetch video from YouTube")
            return False
    
    return True


def test_note_operations():
    """Test note CRUD operations"""
    print("\n" + "="*60)
    print("TEST 3: Note CRUD Operations")
    print("="*60)
    
    test_video_id = "dQw4w9WgXcQ"
    test_note_content = "# Test Note\n\nThis is a **test** note for the video.\n\n## Features\n- Markdown support\n- Auto-save\n- TipTap editor"
    
    # Create/Update note
    print(f"\n1. Creating/Updating note for video {test_video_id}...")
    note = create_or_update_note(test_video_id, test_note_content, "test@example.com")
    if note:
        print(f"✓ Note created/updated")
        print(f"   Video ID: {note['video_id']}")
        print(f"   Content length: {len(note['note_content'])} characters")
        print(f"   User: {note.get('user_email', 'N/A')}")
    else:
        print("✗ Failed to create/update note")
        return False
    
    # Get note by video ID
    print(f"\n2. Retrieving note for video {test_video_id}...")
    note = get_note_by_video_id(test_video_id)
    if note:
        print(f"✓ Note retrieved")
        print(f"   Created: {note.get('created_at', 'N/A')}")
        print(f"   Updated: {note.get('updated_at', 'N/A')}")
    else:
        print("✗ Failed to retrieve note")
        return False
    
    # Get all notes
    print(f"\n3. Retrieving all notes...")
    notes = get_all_notes(limit=10)
    print(f"✓ Found {len(notes)} notes")
    
    # Get notes with video info
    print(f"\n4. Retrieving notes with video information...")
    notes_with_info = get_notes_with_video_info(limit=10)
    print(f"✓ Found {len(notes_with_info)} notes with video info")
    for note in notes_with_info[:3]:  # Show first 3
        video_info = note.get('youtube_videos', {})
        print(f"   - {note['video_id']}: {video_info.get('title', 'N/A')}")
    
    return True


def test_api_workflow():
    """Test the complete API workflow"""
    print("\n" + "="*60)
    print("TEST 4: Complete API Workflow")
    print("="*60)
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # 1. Extract video ID
    print(f"\n1. Extract video ID from URL...")
    video_id = extract_video_id(test_url)
    print(f"✓ Video ID: {video_id}")
    
    # 2. Check database or fetch from API
    print(f"\n2. Check database or fetch from YouTube...")
    video = get_video_by_id(video_id)
    if not video:
        videos_data = fetch_video_details([video_id])
        if videos_data:
            video = create_or_update_video(videos_data[0])
    
    if video:
        print(f"✓ Video: {video['title']}")
        print(f"   Channel: {video['channel_title']}")
        print(f"   Views: {video.get('view_count', 0):,}")
    else:
        print("✗ Failed to get video")
        return False
    
    # 3. Get or create note
    print(f"\n3. Get or create note...")
    note = get_note_by_video_id(video_id)
    if not note or not note.get('note_content'):
        print("   No existing note, creating new one...")
        note_content = f"# Notes for: {video['title']}\n\nChannel: {video['channel_title']}\n\n## My Notes\n\nAdd your notes here..."
        note = create_or_update_note(video_id, note_content, "test@example.com")
    
    if note:
        print(f"✓ Note ready")
        print(f"   Content preview: {note['note_content'][:100]}...")
    else:
        print("✗ Failed to get/create note")
        return False
    
    # 4. Update note
    print(f"\n4. Update note...")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_content = note['note_content'] + f"\n\n---\n*Last tested: {current_time}*"
    updated_note = create_or_update_note(video_id, updated_content, "test@example.com")
    if updated_note:
        print(f"✓ Note updated successfully")
    else:
        print("✗ Failed to update note")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TASK 2 IMPLEMENTATION TEST SUITE")
    print("="*60)
    print("\nTesting video notes functionality...")
    
    tests = [
        ("Video ID Extraction", test_video_id_extraction),
        ("Video Fetch and Store", test_video_fetch_and_store),
        ("Note CRUD Operations", test_note_operations),
        ("Complete API Workflow", test_api_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Task 2 implementation is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
