"""
Simple CRUD operations test for Supabase
Using: Supabase Python Client Library (recommended for persistent apps)
"""

import os
import re
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def validate_book_id(book_id: str) -> bool:
    """
    Validate book ID format
    
    Args:
        book_id: Book identifier to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not book_id or not isinstance(book_id, str):
        return False
    
    # Allow lowercase letters, numbers, and underscores only
    # Must start with a letter or number, and be between 1-100 characters
    pattern = r'^[a-z0-9][a-z0-9_]{0,99}$'
    return bool(re.match(pattern, book_id))


def create_note(title: str, content: str):
    """Create a new note"""
    try:
        response = supabase.table("notes").insert({
            "title": title,
            "content": content
        }).execute()
        print(f"✅ Created: {response.data}")
        return response.data
    except Exception as e:
        print(f"❌ Create Error: {e}")
        return None


def read_notes():
    """Read all notes"""
    try:
        response = supabase.table("notes").select("*").execute()
        print(f"✅ Read {len(response.data)} notes:")
        for note in response.data:
            print(f"   ID: {note.get('id')} | Title: {note.get('title')}")
        return response.data
    except Exception as e:
        print(f"❌ Read Error: {e}")
        return None


def update_note(note_id: int, title: str = None, content: str = None):
    """Update an existing note"""
    try:
        update_data = {}
        if title:
            update_data["title"] = title
        if content:
            update_data["content"] = content
        
        response = supabase.table("notes").update(update_data).eq("id", note_id).execute()
        print(f"✅ Updated: {response.data}")
        return response.data
    except Exception as e:
        print(f"❌ Update Error: {e}")
        return None


def delete_note(note_id: int):
    """Delete a note"""
    try:
        response = supabase.table("notes").delete().eq("id", note_id).execute()
        print(f"✅ Deleted note with ID: {note_id}")
        return response.data
    except Exception as e:
        print(f"❌ Delete Error: {e}")
        return None


def test_crud():
    """Test all CRUD operations"""
    print("\n" + "="*50)
    print("🧪 Testing Supabase CRUD Operations")
    print("="*50 + "\n")
    
    # CREATE
    print("1️⃣ CREATE - Adding a new note...")
    new_note = create_note("Test Note", "This is a test note content")
    if not new_note:
        print("⚠️  Cannot proceed without successful create. Check your connection and table.")
        return
    
    note_id = new_note[0]["id"]
    print()
    
    # READ
    print("2️⃣ READ - Fetching all notes...")
    read_notes()
    print()
    
    # UPDATE
    print("3️⃣ UPDATE - Updating the note...")
    update_note(note_id, title="Updated Test Note", content="This content has been updated!")
    print()
    
    # READ AGAIN
    print("4️⃣ READ - Fetching notes after update...")
    read_notes()
    print()
    
    # DELETE
    print("5️⃣ DELETE - Removing the test note...")
    delete_note(note_id)
    print()
    
    # READ FINAL
    print("6️⃣ READ - Final check after delete...")
    read_notes()
    print()
    
    print("="*50)
    print("✨ CRUD Test Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_crud()
