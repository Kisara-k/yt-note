"""
CRUD operations for book notes in Supabase (2nd database)
Handles user notes for books
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

# Load environment variables
load_dotenv()

# Initialize Supabase client for 2nd database - use SERVICE key for admin operations
url: str = os.getenv("SUPABASE_URL_2")
key: str = os.getenv("SUPABASE_SERVICE_KEY_2")
supabase: Client = create_client(url, key)


def create_or_update_note(
    book_id: str,
    note_content: str,
    custom_tags: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Create or update a note for a book
    
    Args:
        book_id: Book identifier
        note_content: Markdown note content
        custom_tags: Optional list of tags
        
    Returns:
        Note record or None on error
    """
    try:
        note_data = {
            'book_id': book_id,
            'note_content': note_content,
            'custom_tags': custom_tags or []
        }
        
        print(f"[DB->] UPSERT book_notes (book={book_id})")
        response = supabase.table("book_notes").upsert(note_data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Upserted note for book {book_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to upsert note")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_note_by_book_id(book_id: str) -> Optional[Dict[str, Any]]:
    """
    Get note for a book
    
    Args:
        book_id: Book identifier
        
    Returns:
        Note record or None if not found
    """
    try:
        print(f"[DB->] SELECT book_notes WHERE book_id={book_id}")
        response = supabase.table("book_notes").select("*").eq("book_id", book_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found note for book {book_id}")
            return response.data[0]
        else:
            print(f"[DB<-] Note not found")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_notes_with_book_info(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all notes with book information (JOIN query)
    
    Args:
        limit: Maximum number of notes to return
        
    Returns:
        List of notes with book information
    """
    try:
        print(f"[DB->] SELECT book_notes JOIN books LIMIT {limit}")
        response = supabase.table("book_notes").select(
            "*, books(id, title, author, created_at)"
        ).limit(limit).order("updated_at", desc=True).execute()
        
        if response.data:
            print(f"[DB<-] Found {len(response.data)} notes")
            return response.data
        else:
            print(f"[DB<-] No notes found")
            return []
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def delete_note(book_id: str) -> bool:
    """
    Delete a note for a book
    
    Args:
        book_id: Book identifier
        
    Returns:
        True if deleted, False on error
    """
    try:
        print(f"[DB->] DELETE book_notes WHERE book_id={book_id}")
        supabase.table("book_notes").delete().eq("book_id", book_id).execute()
        print(f"[DB<-] Deleted note for book {book_id}")
        return True
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return False
