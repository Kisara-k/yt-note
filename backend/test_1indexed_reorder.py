"""
Test 1-indexed chapter reordering
"""

from db.book_chapters_crud import create_chapter, get_chapters_by_book, reorder_chapters, delete_all_chapters_for_book
from db.books_crud import create_book, delete_book
import uuid

def test_1indexed_reorder():
    """Test that reordering creates 1-indexed chapters (1, 2, 3...)"""
    
    test_book_id = f"test_1idx_{str(uuid.uuid4())[:8]}"
    print(f"\n[1] Creating test book: {test_book_id}")
    
    book = create_book(book_id=test_book_id, title="1-Indexed Test", author="Test")
    if not book:
        return False
    print("   ✓ Book created")
    
    # Create 4 chapters (1-indexed: 1, 2, 3, 4)
    print("\n[2] Creating 4 chapters (1, 2, 3, 4)...")
    for i in range(4):
        chapter = create_chapter(test_book_id, i + 1, f"Chapter {i + 1}", f"Content {i + 1}")
        if not chapter:
            print(f"   ✗ Failed to create chapter {i + 1}")
            cleanup(test_book_id)
            return False
    print("   ✓ All chapters created")
    
    # Show current state
    print("\n[3] Current chapters:")
    chapters = get_chapters_by_book(test_book_id)
    for ch in chapters:
        print(f"   ID={ch['chapter_id']}, Title='{ch['chapter_title']}'")
    
    # Reorder: [2, 4, 1, 3] (mix them up) - using 1-indexed IDs
    print("\n[4] Reordering to [2, 4, 1, 3]...")
    new_order = [2, 4, 1, 3]  # Current chapter_ids in desired order
    
    if not reorder_chapters(test_book_id, new_order):
        print("   ✗ Failed to reorder")
        cleanup(test_book_id)
        return False
    print("   ✓ Reordered")
    
    # Check result - should be 1-indexed (1, 2, 3, 4)
    print("\n[5] After reordering (should be 1-indexed):")
    reordered = get_chapters_by_book(test_book_id)
    
    expected_titles = ["Chapter 2", "Chapter 4", "Chapter 1", "Chapter 3"]
    expected_ids = [1, 2, 3, 4]
    
    success = True
    for idx, ch in enumerate(reordered):
        print(f"   ID={ch['chapter_id']}, Title='{ch['chapter_title']}'")
        
        if ch['chapter_id'] != expected_ids[idx]:
            print(f"      ✗ Expected ID={expected_ids[idx]}, got {ch['chapter_id']}")
            success = False
        
        if ch['chapter_title'] != expected_titles[idx]:
            print(f"      ✗ Expected Title='{expected_titles[idx]}', got '{ch['chapter_title']}'")
            success = False
    
    if success:
        print("\n✓ SUCCESS: Chapters are 1-indexed (1, 2, 3, 4)")
        print("   - Chapter IDs start from 1")
        print("   - Chapter order is correct")
    else:
        print("\n✗ FAILED: Reordering did not produce expected result")
    
    cleanup(test_book_id)
    return success

def cleanup(book_id):
    try:
        delete_all_chapters_for_book(book_id)
        delete_book(book_id)
    except:
        pass

if __name__ == "__main__":
    test_1indexed_reorder()
