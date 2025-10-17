"""
Test to verify chapter reordering reindexes properly
"""

from db.book_chapters_crud import (
    create_chapter,
    get_chapters_by_book,
    reorder_chapters,
    delete_all_chapters_for_book
)
from db.books_crud import create_book, delete_book
import uuid

def test_reorder_reindexing():
    """Test that reordering reindexes chapters sequentially starting from 0"""
    
    # Create a test book
    test_book_id = f"test_reorder_{str(uuid.uuid4())[:8]}"
    print(f"\n[1] Creating test book: {test_book_id}")
    
    book = create_book(
        book_id=test_book_id,
        title="Reorder Test Book",
        author="Test Author"
    )
    
    if not book:
        print("   ✗ Failed to create book")
        return False
    print("   ✓ Book created")
    
    # Create 5 chapters (1, 2, 3, 4, 5) - 1-indexed
    print("\n[2] Creating 5 chapters...")
    for i in range(5):
        chapter = create_chapter(
            book_id=test_book_id,
            chapter_id=i + 1,  # 1-indexed
            chapter_title=f"Chapter {i + 1}",
            chapter_text=f"Content for chapter {i + 1}"
        )
        if not chapter:
            print(f"   ✗ Failed to create chapter {i + 1}")
            cleanup(test_book_id)
            return False
        print(f"   ✓ Chapter {i + 1} created")
    
    # Get current chapters
    print("\n[3] Current chapter order:")
    chapters = get_chapters_by_book(test_book_id)
    for ch in chapters:
        print(f"   Chapter {ch['chapter_id']}: {ch['chapter_title']}")
    
    # Reorder: Move chapter 4 to the front [4, 1, 2, 3, 5] - using 1-indexed IDs
    print("\n[4] Reordering: [4, 1, 2, 3, 5] (move chapter 4 to front)")
    new_order = [4, 1, 2, 3, 5]  # These are current chapter_ids (1-indexed)
    
    if not reorder_chapters(test_book_id, new_order):
        print("   ✗ Failed to reorder chapters")
        cleanup(test_book_id)
        return False
    print("   ✓ Chapters reordered")
    
    # Get chapters after reorder
    print("\n[5] Chapter order after reordering:")
    reordered_chapters = get_chapters_by_book(test_book_id)
    
    expected_titles = [
        "Chapter 4",  # Was chapter 4, now at position 1
        "Chapter 1",  # Was chapter 1, now at position 2
        "Chapter 2",  # Was chapter 2, now at position 3
        "Chapter 3",  # Was chapter 3, now at position 4
        "Chapter 5",  # Was chapter 5, now at position 5
    ]
    
    all_correct = True
    for idx, ch in enumerate(reordered_chapters):
        print(f"   Chapter {ch['chapter_id']}: {ch['chapter_title']}")
        
        # Check if chapter_id is sequential starting from 1 (1-indexed)
        if ch['chapter_id'] != idx + 1:
            print(f"      ✗ ERROR: Expected chapter_id={idx + 1}, got {ch['chapter_id']}")
            all_correct = False
        
        # Check if title matches expected
        if ch['chapter_title'] != expected_titles[idx]:
            print(f"      ✗ ERROR: Expected '{expected_titles[idx]}', got '{ch['chapter_title']}'")
            all_correct = False
    
    if not all_correct:
        cleanup(test_book_id)
        return False
    
    print("\n[6] Verifying sequential IDs:")
    chapter_ids = [ch['chapter_id'] for ch in reordered_chapters]
    expected_ids = list(range(1, len(reordered_chapters) + 1))  # 1-indexed: [1, 2, 3, 4, 5]
    
    if chapter_ids != expected_ids:
        print(f"   ✗ ERROR: IDs not sequential!")
        print(f"      Expected: {expected_ids}")
        print(f"      Got: {chapter_ids}")
        cleanup(test_book_id)
        return False
    
    print(f"   ✓ All chapter_ids are sequential: {chapter_ids}")
    
    # Cleanup
    print("\n[7] Cleaning up...")
    cleanup(test_book_id)
    print("   ✓ Test book deleted")
    
    print("\n" + "="*60)
    print("✓ REORDER REINDEXING TEST PASSED!")
    print("  - Chapters are reindexed sequentially starting from 1")
    print("  - Chapter order matches expected order")
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
    test_reorder_reindexing()
