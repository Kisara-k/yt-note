"""
CRUD operations for books in Supabase (2nd database)
Handles storing and retrieving book metadata
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client for 2nd database - use SERVICE key for admin operations
url: str = os.getenv("SUPABASE_URL_2")
key: str = os.getenv("SUPABASE_SERVICE_KEY_2")
supabase: Client = create_client(url, key)


def create_book(
    book_id: str,
    title: str,
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    publication_year: Optional[int] = None,
    isbn: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    book_type: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a new book entry
    
    Args:
        book_id: User-provided short identifier (e.g., 'the_subtle_art')
        title: Book title
        author: Book author
        publisher: Publisher name
        publication_year: Year of publication
        isbn: ISBN number
        description: Book description
        tags: List of tags
        book_type: Type of book ('book', 'lecture', etc.) - defaults to 'book'
        
    Returns:
        Created book record or None on error
    """
    try:
        book_data = {
            'id': book_id,
            'title': title,
            'author': author,
            'publisher': publisher,
            'publication_year': publication_year,
            'isbn': isbn,
            'description': description,
            'tags': tags or [],
            'type': book_type or 'book'
        }
        
        print(f"[DB->] INSERT books (id={book_id}, type={book_type or 'book'})")
        response = supabase.table("books").insert(book_data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Created book {book_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to create book")
            return None
            
    except Exception as e:
        error_msg = str(e)
        print(f"[DB!!] {error_msg}")
        
        # Check for duplicate key error
        if "duplicate key" in error_msg.lower() or "already exists" in error_msg.lower() or "unique" in error_msg.lower():
            print(f"[DB!!] Book with ID '{book_id}' already exists")
            raise ValueError(f"Book with ID '{book_id}' already exists")
        
        return None


def get_book_by_id(book_id: str) -> Optional[Dict[str, Any]]:
    """
    Get book by ID
    
    Args:
        book_id: Book identifier
        
    Returns:
        Book data or None if not found
    """
    try:
        print(f"[DB->] SELECT books WHERE id={book_id}")
        response = supabase.table("books").select("*").eq("id", book_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found book {book_id}")
            return response.data[0]
        else:
            print(f"[DB<-] Book not found")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_all_books(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all books (most recently updated first)
    
    Args:
        limit: Maximum number of books to return
        
    Returns:
        List of book records
    """
    try:
        print(f"[DB->] SELECT books LIMIT {limit}")
        response = supabase.table("books").select("*").limit(limit).order('updated_at', desc=True).execute()
        
        if response.data:
            print(f"[DB<-] Found {len(response.data)} books")
            return response.data
        else:
            print(f"[DB<-] No books found")
            return []
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def update_book(
    book_id: str,
    title: Optional[str] = None,
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    publication_year: Optional[int] = None,
    isbn: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Update book metadata
    
    Args:
        book_id: Book identifier
        title: Book title
        author: Book author
        publisher: Publisher name
        publication_year: Year of publication
        isbn: ISBN number
        description: Book description
        tags: List of tags
        
    Returns:
        Updated book record or None on error
    """
    try:
        update_data = {}
        
        if title is not None:
            update_data['title'] = title
        if author is not None:
            update_data['author'] = author
        if publisher is not None:
            update_data['publisher'] = publisher
        if publication_year is not None:
            update_data['publication_year'] = publication_year
        if isbn is not None:
            update_data['isbn'] = isbn
        if description is not None:
            update_data['description'] = description
        if tags is not None:
            update_data['tags'] = tags
            
        if not update_data:
            print(f"[DB!!] No fields to update")
            return None
        
        print(f"[DB->] UPDATE books WHERE id={book_id}")
        response = supabase.table("books").update(update_data).eq("id", book_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Updated book {book_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to update book")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def delete_book(book_id: str) -> bool:
    """
    Delete a book (cascades to chapters, but NOT book_notes)
    Deletes storage files first, then DB record
    Note: book_notes are NOT deleted (preserved as orphaned records)
    
    Args:
        book_id: Book identifier
        
    Returns:
        True if deleted, False otherwise
    """
    try:
        # Import here to avoid circular dependency
        from .book_chapters_storage import delete_book_chapters_from_storage
        
        # Step 1: Delete all chapter files from storage
        print(f"[DELETE] Step 1: Deleting storage for book {book_id}")
        delete_book_chapters_from_storage(book_id)
        
        # Step 2: Delete book from DB (cascades to book_chapters, but NOT book_notes)
        print(f"[DELETE] Step 2: Deleting book record {book_id}")
        print(f"[DB->] DELETE books WHERE id={book_id}")
        response = supabase.table("books").delete().eq("id", book_id).execute()
        
        print(f"[DB<-] Deleted book {book_id} (book_notes preserved if they exist)")
        return True
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return False
