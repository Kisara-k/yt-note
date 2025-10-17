"""
Test the books feature end-to-end via API
This creates a real book that can be viewed in the frontend
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE = "http://localhost:8000"
BOOK_ID = "practical_guide_123"

# Test user - get token from .env
TOKEN = os.getenv("TEST_JWT_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
} if TOKEN else {}


def test_create_book():
    """Test creating a book with chapters"""
    
    # Load sample book data
    with open("../sample_book.json", "r", encoding="utf-8") as f:
        chapters = json.load(f)
    
    book_data = {
        "book_id": BOOK_ID,
        "title": "A Practical Guide to Learning",
        "author": "John Doe",
        "description": "A comprehensive guide to effective learning strategies and techniques",
        "tags": ["learning", "education", "self-improvement"],
        "chapters": chapters
    }
    
    response = requests.post(
        f"{API_BASE}/api/book",
        headers=headers,
        json=book_data
    )
    
    print("Create Book:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✓ Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"  ✗ Error: {response.text}")
        return None


def test_get_book(book_id):
    """Test getting book metadata"""
    response = requests.get(
        f"{API_BASE}/api/book/{book_id}",
        headers=headers
    )
    
    print("\nGet Book:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✓ Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"  ✗ Error: {response.text}")
        return None


def test_get_chapter_index(book_id):
    """Test getting chapter index"""
    response = requests.get(
        f"{API_BASE}/api/book/{book_id}/chapters/index",
        headers=headers
    )
    
    print("\nGet Chapter Index:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        chapters = response.json()
        print(f"  ✓ Found {len(chapters)} chapters")
        for ch in chapters[:3]:
            print(f"    - {ch.get('short_title')}")
        return chapters
    else:
        print(f"  ✗ Error: {response.text}")
        return None


def test_get_chapter(book_id, chapter_id):
    """Test getting chapter details"""
    response = requests.get(
        f"{API_BASE}/api/book/{book_id}/chapter/{chapter_id}",
        headers=headers
    )
    
    print(f"\nGet Chapter {chapter_id}:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Title: {data.get('short_title')}")
        print(f"    Text length: {len(data.get('text', ''))} chars")
        return data
    else:
        print(f"  ✗ Error: {response.text}")
        return None


def test_update_chapter_note(book_id, chapter_id):
    """Test updating chapter note"""
    note_data = {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "note": "This chapter introduces the core concepts. Key points: patience and systematic learning."
    }
    
    response = requests.post(
        f"{API_BASE}/api/book/chapter/note",
        headers=headers,
        json=note_data
    )
    
    print(f"\nUpdate Chapter {chapter_id} Note:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✓ Note updated successfully")
        return response.json()
    else:
        print(f"  ✗ Error: {response.text}")
        return None


def test_create_book_note(book_id):
    """Test creating/updating book note"""
    note_data = {
        "book_id": book_id,
        "note": "Excellent book with clear progression. Highly recommend for beginners.",
        "tags": ["important", "reference", "beginner-friendly"]
    }
    
    response = requests.post(
        f"{API_BASE}/api/book/note",
        headers=headers,
        json=note_data
    )
    
    print("\nCreate Book Note:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✓ Book note created/updated")
        return response.json()
    else:
        print(f"  ✗ Error: {response.text}")
        return None


def test_get_book_note(book_id):
    """Test getting book note"""
    response = requests.get(
        f"{API_BASE}/api/book/{book_id}/note",
        headers=headers
    )
    
    print("\nGet Book Note:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        note = response.json()
        print(f"  ✓ Note: {note.get('note', '')[:50]}...")
        print(f"    Tags: {note.get('custom_tags', [])}")
        return note
    else:
        print(f"  ✗ Error: {response.text}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("BOOKS API TEST")
    print("=" * 60)
    print("\n⚠️  Make sure:")
    print("  1. Backend is running (python main.py)")
    print("  2. You have a valid auth token in .env as TEST_JWT_TOKEN")
    print("  3. Books database schema is applied")
    print("  4. sample_book.json exists in parent directory")
    print("\n" + "=" * 60)
    
    if not TOKEN:
        print("\n❌ ERROR: No TEST_JWT_TOKEN in .env file")
        print("   Get it by logging in to the frontend and checking browser devtools")
        print("   Add it to .env as: TEST_JWT_TOKEN=your_token_here")
        exit(1)
    
    try:
        # Run tests
        result = test_create_book()
        if not result:
            print("\n❌ Failed to create book - stopping tests")
            exit(1)
            
        test_get_book(BOOK_ID)
        test_get_chapter_index(BOOK_ID)
        test_get_chapter(BOOK_ID, 0)
        test_update_chapter_note(BOOK_ID, 0)
        test_create_book_note(BOOK_ID)
        test_get_book_note(BOOK_ID)
        
        print("\n" + "=" * 60)
        print("✅ ALL API TESTS COMPLETED")
        print("=" * 60)
        print(f"\nYour book is now viewable at:")
        print(f"http://localhost:3000/books?b={BOOK_ID}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
