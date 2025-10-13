"""
Debug test to see exactly what's happening during reorder
"""

from db.book_chapters_crud import create_chapter, get_chapters_by_book, delete_all_chapters_for_book
from db.books_crud import create_book, delete_book
from db.book_chapters_crud import supabase
import uuid

def debug_reorder():
    """Debug test to see exactly what reorder does"""
    
    test_book_id = f"debug_{str(uuid.uuid4())[:8]}"
    print(f"\n[TEST] Creating book: {test_book_id}\n")
    
    book = create_book(book_id=test_book_id, title="Debug Book", author="Test")
    
    # Create 3 chapters (1-indexed: 1, 2, 3)
    print("[TEST] Creating 3 chapters (1, 2, 3):\n")
    for i in range(3):
        create_chapter(test_book_id, i + 1, f"Chapter {i + 1}", f"Content {i + 1}")
    
    chapters = get_chapters_by_book(test_book_id)
    print("BEFORE REORDER:")
    for ch in chapters:
        print(f"  ID={ch['chapter_id']}, Title='{ch['chapter_title']}', Path={ch['chapter_text_path'].split('/')[-1][:8]}...")
    
    # Manual reorder to see what happens (1-indexed IDs)
    print("\n[TEST] Reordering to [3, 1, 2] (move chapter 3 to front):\n")
    chapter_order = [3, 1, 2]  # Current chapter_ids in desired order
    
    # Step 1: Set to negative temps
    print("Step 1: Setting temporary negative IDs")
    for idx, old_id in enumerate(chapter_order):
        temp_id = -(idx + 1)
        print(f"  Chapter {old_id} -> temp {temp_id}")
        supabase.table("book_chapters").update({"chapter_id": temp_id}).eq("book_id", test_book_id).eq("chapter_id", old_id).execute()
    
    chapters_temp = get_chapters_by_book(test_book_id)
    print("\nAFTER TEMP IDS:")
    for ch in sorted(chapters_temp, key=lambda x: x['chapter_id']):
        print(f"  ID={ch['chapter_id']}, Title='{ch['chapter_title']}'")
    
    # Step 2: Set to final positions
    print("\nStep 2: Setting final positions (1-indexed)")
    for idx, old_id in enumerate(chapter_order):
        temp_id = -(idx + 1)
        new_id = idx + 1  # This should be 1, 2, 3
        print(f"  temp {temp_id} -> final {new_id} (was originally chapter {old_id})")
        supabase.table("book_chapters").update({"chapter_id": new_id}).eq("book_id", test_book_id).eq("chapter_id", temp_id).execute()
    
    chapters_final = get_chapters_by_book(test_book_id)
    print("\nAFTER FINAL IDS:")
    for ch in chapters_final:
        print(f"  ID={ch['chapter_id']}, Title='{ch['chapter_title']}'")
    
    print("\n[EXPECTATION]:")
    print("  ID=1 should have Title='Chapter 3' (was chapter 3)")
    print("  ID=2 should have Title='Chapter 1' (was chapter 1)")
    print("  ID=3 should have Title='Chapter 2' (was chapter 2)")
    
    print("\n[ACTUAL RESULT]:")
    correct = True
    expected = ["Chapter 3", "Chapter 1", "Chapter 2"]
    for ch in chapters_final:
        expected_title = expected[ch['chapter_id'] - 1]  # Adjust for 1-indexed
        match = "✓" if ch['chapter_title'] == expected_title else "✗"
        print(f"  {match} ID={ch['chapter_id']}, Title='{ch['chapter_title']}' (expected '{expected_title}')")
        if ch['chapter_title'] != expected_title:
            correct = False
    
    # Cleanup
    delete_all_chapters_for_book(test_book_id)
    delete_book(test_book_id)
    
    if correct:
        print("\n✓ REORDERING WORKS CORRECTLY (1-indexed)")
    else:
        print("\n✗ REORDERING IS BROKEN")
    
    return correct

if __name__ == "__main__":
    debug_reorder()
