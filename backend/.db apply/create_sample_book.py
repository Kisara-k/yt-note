"""
Create a sample book directly in the database (no API)
This will create a book that can be viewed in the frontend
"""
import json
import sys
import os
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from db.books_crud import create_book
from db.book_chapters_crud import create_chapter
from db.book_notes_crud import create_or_update_note

load_dotenv()

BOOK_ID = "practical_guide_123"
USER_ID = "00000000-0000-0000-0000-000000000000"  # Placeholder user ID

def main():
    print("=" * 60)
    print("CREATING SAMPLE BOOK")
    print("=" * 60)
    
    # Load sample chapters
    print("\n[1] Loading sample book data...")
    with open("../sample_book.json", "r", encoding="utf-8") as f:
        chapters = json.load(f)
    print(f"   ✓ Loaded {len(chapters)} chapters from sample_book.json")
    
    # Create book
    print("\n[2] Creating book metadata...")
    
    result = create_book(
        book_id=BOOK_ID,
        title="A Practical Guide to Learning",
        author="John Doe",
        description="A comprehensive guide to effective learning strategies and techniques",
        tags=["learning", "education", "self-improvement"]
    )
    
    if result:
        print(f"   ✓ Book created: {BOOK_ID}")
        print(f"     Title: {result.get('title')}")
        print(f"     Author: {result.get('author')}")
    else:
        print("   ✗ Failed to create book")
        return
    
    # Create chapters (1-indexed: starting from 1)
    print("\n[3] Creating chapters...")
    for i, chapter in enumerate(chapters):
        result = create_chapter(
            book_id=BOOK_ID,
            chapter_id=i + 1,  # 1-indexed
            chapter_title=chapter["chapter_title"],
            chapter_text=chapter["chapter_text"]
        )
        
        if result:
            print(f"   ✓ Chapter {i + 1}: {chapter['chapter_title']}")
        else:
            print(f"   ✗ Failed to create chapter {i + 1}")
            return
    
    # Create book note
    print("\n[4] Creating book note...")
    
    result = create_or_update_note(
        book_id=BOOK_ID,
        note_content="Excellent book with clear progression from basics to advanced topics. Highly recommend for beginners looking to improve their learning skills.",
        custom_tags=["important", "reference", "beginner-friendly"]
    )
    
    if result:
        print(f"   ✓ Book note created")
    else:
        print(f"   ✗ Failed to create note (this is optional)")
    
    print("\n" + "=" * 60)
    print("✅ SAMPLE BOOK CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nYour book is now in the database!")
    print(f"View it at: http://localhost:3000/books?b={BOOK_ID}")
    print("\nThe book has:")
    print(f"  - {len(chapters)} chapters")
    print(f"  - Complete text for each chapter")
    print(f"  - Book-level notes and tags")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
