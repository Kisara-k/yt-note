"""
Test chapter text update to ensure UUID paths persist
"""

from db.book_chapters_crud import (
    create_chapter,
    get_chapter_details,
    update_chapter_text,
    delete_all_chapters_for_book
)
from db.books_crud import create_book, delete_book
import uuid

def test_chapter_update():
    """Test that updating chapter text maintains the same storage path"""
    
    # Create a test book
    test_book_id = f"test_update_{str(uuid.uuid4())[:8]}"
    print(f"\n[1] Creating test book: {test_book_id}")
    
    book = create_book(
        book_id=test_book_id,
        title="Chapter Update Test",
        author="Test Author"
    )
    
    if not book:
        print("   ✗ Failed to create book")
        return False
    print("   ✓ Book created")
    
    # Create a chapter (1-indexed)
    print("\n[2] Creating initial chapter...")
    original_text = "This is the original chapter text."
    chapter = create_chapter(
        book_id=test_book_id,
        chapter_id=1,  # 1-indexed
        chapter_title="Test Chapter",
        chapter_text=original_text
    )
    
    if not chapter:
        print("   ✗ Failed to create chapter")
        return False
    
    original_path = chapter['chapter_text_path']
    print(f"   ✓ Chapter created with storage path: {original_path}")
    
    # Update chapter text
    print("\n[3] Updating chapter text...")
    updated_text = "This is the UPDATED chapter text with new content."
    updated_chapter = update_chapter_text(test_book_id, 1, updated_text)  # chapter_id=1
    
    if not updated_chapter:
        print("   ✗ Failed to update chapter")
        cleanup(test_book_id)
        return False
    
    updated_path = updated_chapter['chapter_text_path']
    print(f"   ✓ Chapter updated")
    print(f"      Original path: {original_path}")
    print(f"      Updated path:  {updated_path}")
    
    # Verify path didn't change
    if original_path != updated_path:
        print("   ✗ ERROR: Storage path changed during update!")
        cleanup(test_book_id)
        return False
    
    print("   ✓ Storage path remained the same")
    
    # Verify content was actually updated
    print("\n[4] Verifying updated content...")
    full_chapter = get_chapter_details(test_book_id, 1)  # chapter_id=1
    
    if not full_chapter:
        print("   ✗ Failed to retrieve chapter")
        cleanup(test_book_id)
        return False
    
    retrieved_text = full_chapter.get('chapter_text', '')
    
    if retrieved_text != updated_text:
        print(f"   ✗ ERROR: Content not updated correctly!")
        print(f"      Expected: {updated_text}")
        print(f"      Got: {retrieved_text}")
        cleanup(test_book_id)
        return False
    
    print("   ✓ Content updated correctly")
    
    # Update again to test multiple updates
    print("\n[5] Updating chapter text again...")
    second_update_text = "This is the SECOND UPDATE to test persistence."
    second_updated_chapter = update_chapter_text(test_book_id, 1, second_update_text)  # chapter_id=1
    
    if not second_updated_chapter:
        print("   ✗ Failed to update chapter second time")
        cleanup(test_book_id)
        return False
    
    second_path = second_updated_chapter['chapter_text_path']
    
    if original_path != second_path:
        print("   ✗ ERROR: Storage path changed on second update!")
        cleanup(test_book_id)
        return False
    
    print("   ✓ Storage path still the same after multiple updates")
    
    # Cleanup
    print("\n[6] Cleaning up...")
    cleanup(test_book_id)
    print("   ✓ Test book deleted")
    
    print("\n" + "="*60)
    print("✓ CHAPTER UPDATE TEST PASSED!")
    print("  - Storage paths persist across updates")
    print("  - Content is updated correctly")
    print("  - Multiple updates maintain the same path")
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
    test_chapter_update()
