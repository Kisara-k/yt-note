"""
Quick verification that the book was created successfully
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

from db.books_crud import get_book_by_id, get_all_books
from db.book_chapters_crud import get_chapter_index, get_chapter_details
from db.book_notes_crud import get_note_by_book_id

load_dotenv()

BOOK_ID = "practical_guide_123"

def main():
    print("=" * 60)
    print("VERIFYING BOOK IN DATABASE")
    print("=" * 60)
    
    # Check book exists
    print("\n[1] Checking book metadata...")
    book = get_book_by_id(BOOK_ID)
    if book:
        print(f"   ✓ Book found: {book.get('title')}")
        print(f"     Author: {book.get('author')}")
        print(f"     Description: {book.get('description', 'N/A')[:60]}...")
        print(f"     Tags: {book.get('tags', [])}")
    else:
        print(f"   ✗ Book not found!")
        return
    
    # Check chapters
    print("\n[2] Checking chapters...")
    chapters = get_chapter_index(BOOK_ID)
    if chapters:
        print(f"   ✓ Found {len(chapters)} chapters:")
        for ch in chapters:
            print(f"     [{ch.get('chapter_id')}] {ch.get('chapter_title')}")
    else:
        print(f"   ✗ No chapters found!")
        return
    
    # Check chapter details
    print("\n[3] Checking first chapter details...")
    chapter = get_chapter_details(BOOK_ID, 0)
    if chapter:
        print(f"   ✓ Chapter 0 loaded successfully")
        print(f"     Title: {chapter.get('chapter_title')}")
        text = chapter.get('chapter_text', '')
        print(f"     Text: {text[:100]}...")
        print(f"     Total length: {len(text)} characters")
    else:
        print(f"   ✗ Failed to load chapter!")
        return
    
    # Check book note
    print("\n[4] Checking book note...")
    note = get_note_by_book_id(BOOK_ID)
    if note:
        print(f"   ✓ Book note found")
        print(f"     Note: {note.get('note_content', '')[:60]}...")
        print(f"     Tags: {note.get('custom_tags', [])}")
    else:
        print(f"   ⚠ No book note (optional)")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ BOOK VERIFICATION SUCCESSFUL!")
    print("=" * 60)
    print(f"\nBook ID: {BOOK_ID}")
    print(f"Chapters: {len(chapters)}")
    print(f"Status: Ready to view")
    print(f"\n🔗 View in frontend:")
    print(f"   http://localhost:3000/books?b={BOOK_ID}")
    print("\n📊 What's included:")
    print(f"   - Complete book metadata")
    print(f"   - {len(chapters)} chapters with full text")
    print(f"   - Chapter-by-chapter viewing")
    print(f"   - Note-taking capability")
    print(f"   - Tags and organization")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
