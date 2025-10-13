"""
Test script for books functionality
Tests all book-related CRUD operations and API endpoints
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.books_crud import (
    create_book,
    get_book_by_id,
    get_all_books,
    delete_book
)
from db.book_chapters_crud import (
    create_chapter,
    get_chapters_by_book,
    get_chapter_index,
    get_chapter_details,
    update_chapter_note
)
from db.book_notes_crud import (
    create_or_update_note,
    get_note_by_book_id
)


def test_books():
    """Test books functionality"""
    print("=" * 60)
    print("TESTING BOOKS FUNCTIONALITY")
    print("=" * 60)
    
    # Test data
    test_book_id = "test_book_123"
    test_title = "Test Book: The Art of Testing"
    test_author = "Test Author"
    
    # Clean up any existing test data
    print("\n1. Cleaning up existing test data...")
    delete_book(test_book_id)
    print("   ✓ Cleanup complete")
    
    # Test 1: Create book
    print("\n2. Creating book...")
    book = create_book(
        book_id=test_book_id,
        title=test_title,
        author=test_author,
        description="A test book for testing",
        tags=["testing", "example"]
    )
    
    if book:
        print(f"   ✓ Book created: {book['id']}")
        print(f"     Title: {book['title']}")
        print(f"     Author: {book['author']}")
    else:
        print("   ✗ Failed to create book")
        return False
    
    # Test 2: Create chapters
    print("\n3. Creating chapters...")
    chapters_data = [
        {
            "chapter_title": "Chapter 1: Introduction",
            "chapter_text": "This is the introduction chapter. It contains important introductory material that sets the stage for the rest of the book."
        },
        {
            "chapter_title": "Chapter 2: The Main Concept",
            "chapter_text": "This chapter explores the main concept in detail. It provides examples and explanations of the core ideas."
        },
        {
            "chapter_title": "Chapter 3: Advanced Topics",
            "chapter_text": "Here we dive into advanced topics that build upon the foundation laid in previous chapters."
        }
    ]
    
    for idx, chapter_data in enumerate(chapters_data):
        chapter = create_chapter(
            book_id=test_book_id,
            chapter_id=idx,
            chapter_title=chapter_data["chapter_title"],
            chapter_text=chapter_data["chapter_text"]
        )
        if chapter:
            print(f"   ✓ Chapter {idx} created: {chapter['chapter_title']}")
        else:
            print(f"   ✗ Failed to create chapter {idx}")
            return False
    
    # Test 3: Get book by ID
    print("\n4. Retrieving book by ID...")
    retrieved_book = get_book_by_id(test_book_id)
    if retrieved_book and retrieved_book['id'] == test_book_id:
        print(f"   ✓ Book retrieved: {retrieved_book['title']}")
    else:
        print("   ✗ Failed to retrieve book")
        return False
    
    # Test 4: Get all books
    print("\n5. Getting all books...")
    all_books = get_all_books()
    if all_books and any(b['id'] == test_book_id for b in all_books):
        print(f"   ✓ Found {len(all_books)} books (including test book)")
    else:
        print("   ✗ Failed to get all books")
        return False
    
    # Test 5: Get chapter index
    print("\n6. Getting chapter index...")
    index = get_chapter_index(test_book_id)
    if index and len(index) == 3:
        print(f"   ✓ Chapter index retrieved: {len(index)} chapters")
        for chapter in index:
            print(f"     - Chapter {chapter['chapter_id']}: {chapter['chapter_title']}")
    else:
        print("   ✗ Failed to get chapter index")
        return False
    
    # Test 6: Get chapter details
    print("\n7. Getting chapter details...")
    chapter_details = get_chapter_details(test_book_id, 0)
    if chapter_details:
        print(f"   ✓ Chapter details retrieved:")
        print(f"     Title: {chapter_details['chapter_title']}")
        print(f"     Text length: {len(chapter_details.get('chapter_text', ''))} characters")
    else:
        print("   ✗ Failed to get chapter details")
        return False
    
    # Test 7: Update chapter note
    print("\n8. Updating chapter note...")
    note_result = update_chapter_note(
        test_book_id,
        0,
        "This is my note for chapter 1. It contains important observations."
    )
    if note_result:
        print("   ✓ Chapter note updated")
    else:
        print("   ✗ Failed to update chapter note")
        return False
    
    # Test 8: Verify chapter note
    print("\n9. Verifying chapter note...")
    chapter_with_note = get_chapter_details(test_book_id, 0)
    if chapter_with_note and chapter_with_note.get('note_content'):
        print(f"   ✓ Chapter note verified: {chapter_with_note['note_content'][:50]}...")
    else:
        print("   ✗ Failed to verify chapter note")
        return False
    
    # Test 9: Create book note
    print("\n10. Creating book note...")
    book_note = create_or_update_note(
        test_book_id,
        "This is my overall note for the book. It summarizes my thoughts.",
        custom_tags=["important", "reference"]
    )
    if book_note:
        print("   ✓ Book note created")
    else:
        print("   ✗ Failed to create book note")
        return False
    
    # Test 10: Get book note
    print("\n11. Retrieving book note...")
    retrieved_note = get_note_by_book_id(test_book_id)
    if retrieved_note and retrieved_note.get('note_content'):
        print(f"   ✓ Book note retrieved: {retrieved_note['note_content'][:50]}...")
        print(f"     Tags: {retrieved_note.get('custom_tags', [])}")
    else:
        print("   ✗ Failed to retrieve book note")
        return False
    
    # Test 11: Get all chapters
    print("\n12. Getting all chapters...")
    all_chapters = get_chapters_by_book(test_book_id)
    if all_chapters and len(all_chapters) == 3:
        print(f"   ✓ All chapters retrieved: {len(all_chapters)} chapters")
    else:
        print("   ✗ Failed to get all chapters")
        return False
    
    # Cleanup
    print("\n13. Cleaning up test data...")
    if delete_book(test_book_id):
        print("   ✓ Test book deleted")
    else:
        print("   ✗ Failed to delete test book")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Check if environment variables are set
    if not os.getenv("SUPABASE_URL_2") or not os.getenv("SUPABASE_KEY_2"):
        print("ERROR: SUPABASE_URL_2 and SUPABASE_KEY_2 must be set in .env")
        sys.exit(1)
    
    try:
        success = test_books()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
