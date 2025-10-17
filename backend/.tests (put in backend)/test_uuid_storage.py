"""
Test script to verify UUID-based chapter storage
Tests that chapters maintain their storage paths across reorders
"""

from db.book_chapters_crud import (
    create_chapter,
    get_chapters_by_book,
    get_chapter_details,
    reorder_chapters,
    delete_all_chapters_for_book
)
from db.books_crud import create_book, delete_book
import uuid

def test_uuid_storage():
    """Test that chapter storage uses UUIDs and persists across reorders"""
    
    # Create a test book
    test_book_id = f"test_uuid_{str(uuid.uuid4())[:8]}"
    print(f"\n[1] Creating test book: {test_book_id}")
    
    book = create_book(
        book_id=test_book_id,
        title="UUID Storage Test Book",
        author="Test Author",
        description="Test book for UUID storage",
        tags=["test"]
    )
    
    if not book:
        print("   ✗ Failed to create book")
        return False
    print("   ✓ Book created")
    
    # Create 3 chapters (1-indexed: 1, 2, 3)
    print("\n[2] Creating 3 chapters...")
    chapters_data = [
        {"title": "First Chapter", "text": "This is the first chapter content."},
        {"title": "Second Chapter", "text": "This is the second chapter content."},
        {"title": "Third Chapter", "text": "This is the third chapter content."}
    ]
    
    for idx, ch in enumerate(chapters_data):
        chapter = create_chapter(
            book_id=test_book_id,
            chapter_id=idx + 1,  # 1-indexed
            chapter_title=ch["title"],
            chapter_text=ch["text"]
        )
        if not chapter:
            print(f"   ✗ Failed to create chapter {idx + 1}")
            return False
        print(f"   ✓ Chapter {idx + 1}: {ch['title']}")
    
    # Get chapters and store their storage paths
    print("\n[3] Checking initial storage paths...")
    chapters = get_chapters_by_book(test_book_id)
    original_paths = {}
    
    for ch in chapters:
        path = ch['chapter_text_path']
        original_paths[ch['chapter_id']] = path
        print(f"   Chapter {ch['chapter_id']}: {path}")
        
        # Verify path format (should be book_id/uuid.txt, not chapter_X.txt)
        if f"chapter_{ch['chapter_id']}" in path:
            print(f"   ✗ ERROR: Path still uses old format: {path}")
            cleanup(test_book_id)
            return False
    
    print("   ✓ All chapters use UUID-based storage paths")
    
    # Reorder chapters: [1, 2, 3] -> [3, 1, 2] (1-indexed)
    print("\n[4] Reordering chapters: [1, 2, 3] -> [3, 1, 2]")
    new_order = [3, 1, 2]  # These are the current chapter_ids in desired order
    if not reorder_chapters(test_book_id, new_order):
        print("   ✗ Failed to reorder chapters")
        cleanup(test_book_id)
        return False
    print("   ✓ Chapters reordered")
    
    # Verify storage paths remained the same
    print("\n[5] Verifying storage paths after reorder...")
    reordered_chapters = get_chapters_by_book(test_book_id)
    
    # After reorder, chapters should be 1-indexed: [1, 2, 3]
    # Chapter 1 should have the content/path of old chapter 3
    # Chapter 2 should have the content/path of old chapter 1
    # Chapter 3 should have the content/path of old chapter 2
    
    for idx, ch in enumerate(reordered_chapters):
        new_id = ch['chapter_id']  # Should be 1, 2, 3
        old_id = new_order[idx]  # Which old chapter is now at this position
        current_path = ch['chapter_text_path']
        expected_path = original_paths[old_id]
        
        print(f"   Chapter {new_id} (was {old_id}): {current_path}")
        
        if current_path != expected_path:
            print(f"   ✗ ERROR: Storage path changed!")
            print(f"      Expected: {expected_path}")
            print(f"      Got: {current_path}")
            cleanup(test_book_id)
            return False
    
    print("   ✓ All storage paths remained unchanged after reorder")
    
    # Verify content is correct
    print("\n[6] Verifying chapter content after reorder...")
    for idx, ch in enumerate(reordered_chapters):
        new_id = ch['chapter_id']
        old_id = new_order[idx]  # Original chapter that's now at this position
        
        # Get full chapter details with text
        full_chapter = get_chapter_details(test_book_id, new_id)
        if not full_chapter:
            print(f"   ✗ Failed to get chapter {new_id}")
            cleanup(test_book_id)
            return False
        
        # Get the expected text based on which old chapter this was
        # old_id is 1-indexed (1, 2, 3), chapters_data is 0-indexed array
        expected_text = chapters_data[old_id - 1]["text"]
        actual_text = full_chapter.get('chapter_text', '')
        
        if actual_text != expected_text:
            print(f"   ✗ ERROR: Content mismatch for chapter {new_id}")
            print(f"      Expected: {expected_text}")
            print(f"      Got: {actual_text}")
            cleanup(test_book_id)
            return False
        
        print(f"   ✓ Chapter {new_id} content correct")
    
    # Cleanup
    print("\n[7] Cleaning up...")
    cleanup(test_book_id)
    print("   ✓ Test book deleted")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("  - Chapters use UUID-based storage paths")
    print("  - Storage paths persist across reorders")
    print("  - Content remains correct after reordering")
    print("="*60)
    return True


def cleanup(book_id: str):
    """Clean up test data"""
    try:
        delete_all_chapters_for_book(book_id)
        delete_book(book_id)
    except Exception as e:
        print(f"   ! Cleanup error: {e}")


if __name__ == "__main__":
    test_uuid_storage()
