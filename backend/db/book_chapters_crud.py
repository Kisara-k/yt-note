"""
CRUD operations for book chapters in Supabase (2nd database)
Uses Supabase Storage for chapter text, DB for metadata
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from .book_chapters_storage import (
    ensure_bucket_exists,
    upload_chapter_text,
    download_chapter_text,
    delete_book_chapters_from_storage,
    delete_chapter_from_storage
)

# Load environment variables
load_dotenv()

# Initialize Supabase client for 2nd database - use SERVICE key for admin operations
url: str = os.getenv("SUPABASE_URL_2")
key: str = os.getenv("SUPABASE_SERVICE_KEY_2")
supabase: Client = create_client(url, key)

# Ensure storage bucket exists on module load
ensure_bucket_exists()


def load_chapter_text(chapter: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load chapter text from storage and add it to the chapter dict
    Modifies chapter in-place and returns it
    
    Args:
        chapter: Chapter dictionary with chapter_text_path
        
    Returns:
        Chapter dictionary with chapter_text added
    """
    if chapter.get('chapter_text_path'):
        chapter_text = download_chapter_text(chapter['chapter_text_path'])
        chapter['chapter_text'] = chapter_text if chapter_text else None
    else:
        chapter['chapter_text'] = None
    return chapter


def load_chapters_text(chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Load chapter text from storage for multiple chapters
    Modifies chapters in-place and returns them
    
    Args:
        chapters: List of chapter dictionaries with chapter_text_path
        
    Returns:
        List of chapter dictionaries with chapter_text added
    """
    for chapter in chapters:
        load_chapter_text(chapter)
    return chapters


def create_chapter(
    book_id: str,
    chapter_id: int,
    chapter_title: str,
    chapter_text: str,
    ai_field_1: Optional[str] = None,
    ai_field_2: Optional[str] = None,
    ai_field_3: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a new book chapter
    Stores chapter text in storage with unique UUID, metadata in DB
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier (1-indexed: starts from 1)
        chapter_title: Title of the chapter
        chapter_text: Full text content of the chapter
        ai_field_1: AI field 1 (optional)
        ai_field_2: AI field 2 (optional)
        ai_field_3: AI field 3 (optional)
        
    Returns:
        Created chapter record or None on error
    """
    try:
        # Upload chapter text to storage with unique UUID
        chapter_text_path = upload_chapter_text(book_id, chapter_text)
        if not chapter_text_path:
            print(f"[DB!!] Failed to upload chapter text to storage")
            return None
        
        chapter_data = {
            'book_id': book_id,
            'chapter_id': chapter_id,
            'chapter_title': chapter_title,
            'chapter_text_path': chapter_text_path,
            'ai_field_1': ai_field_1,
            'ai_field_2': ai_field_2,
            'ai_field_3': ai_field_3
        }
        
        print(f"[DB->] UPSERT book_chapters (book={book_id}, chapter={chapter_id}, storage={chapter_text_path})")
        response = supabase.table("book_chapters").upsert(chapter_data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Upserted chapter {chapter_id} for book {book_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to create chapter {chapter_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_chapters_by_book(book_id: str) -> List[Dict[str, Any]]:
    """
    Get all chapters for a book (ordered by chapter_id)
    Does NOT load chapter text from storage
    
    Args:
        book_id: Book identifier
        
    Returns:
        List of chapter records (without chapter_text)
    """
    try:
        print(f"[DB->] SELECT book_chapters WHERE book_id={book_id}")
        response = supabase.table("book_chapters").select("*").eq("book_id", book_id).order("chapter_id").execute()
        
        if response.data:
            print(f"[DB<-] Found {len(response.data)} chapters")
            return response.data
        else:
            print(f"[DB<-] No chapters found")
            return []
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def get_chapter_index(book_id: str) -> List[Dict[str, Any]]:
    """
    Get chapter index (chapter_id, chapter_title, short_title only)
    Lightweight query for navigation
    
    Args:
        book_id: Book identifier
        
    Returns:
        List of chapter records with minimal fields
    """
    try:
        print(f"[DB->] SELECT chapter index WHERE book_id={book_id}")
        response = supabase.table("book_chapters").select(
            "chapter_id, chapter_title, ai_field_1"
        ).eq("book_id", book_id).order("chapter_id").execute()
        
        if response.data:
            print(f"[DB<-] Found {len(response.data)} chapters")
            return response.data
        else:
            print(f"[DB<-] No chapters found")
            return []
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def get_chapter_metadata(book_id: str, chapter_id: int) -> Optional[Dict[str, Any]]:
    """
    Get chapter metadata only (no text loading from storage)
    Lightweight query for verification and titles
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        
    Returns:
        Chapter metadata without chapter_text
    """
    try:
        print(f"[DB->] SELECT chapter metadata WHERE book_id={book_id} AND chapter_id={chapter_id}")
        response = supabase.table("book_chapters").select("*").eq("book_id", book_id).eq("chapter_id", chapter_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found chapter {chapter_id} metadata")
            return response.data[0]
        else:
            print(f"[DB<-] Chapter not found")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_chapter_details(book_id: str, chapter_id: int, include_text: bool = True) -> Optional[Dict[str, Any]]:
    """
    Get chapter details with optional text loading from storage
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        include_text: If True, load chapter_text from storage (default: True)
        
    Returns:
        Chapter record with chapter_text (if include_text=True) or None if not found
    """
    try:
        print(f"[DB->] SELECT book_chapters WHERE book_id={book_id} AND chapter_id={chapter_id}")
        response = supabase.table("book_chapters").select("*").eq("book_id", book_id).eq("chapter_id", chapter_id).execute()
        
        if response.data and len(response.data) > 0:
            chapter = response.data[0]
            print(f"[DB<-] Found chapter {chapter_id}")
            # Load chapter text from storage only if requested
            if include_text:
                load_chapter_text(chapter)
            else:
                chapter['chapter_text'] = None
            return chapter
        else:
            print(f"[DB<-] Chapter not found")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def update_chapter_note(book_id: str, chapter_id: int, note_content: str) -> Optional[Dict[str, Any]]:
    """
    Update user note for a chapter
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        note_content: Markdown note content
        
    Returns:
        Updated chapter record or None on error
    """
    try:
        print(f"[DB->] UPDATE book_chapters note WHERE book_id={book_id} AND chapter_id={chapter_id}")
        response = supabase.table("book_chapters").update({
            'note_content': note_content
        }).eq("book_id", book_id).eq("chapter_id", chapter_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Updated note for chapter {chapter_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to update note")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def update_chapter_ai_fields(
    book_id: str,
    chapter_id: int,
    ai_field_1: Optional[str] = None,
    ai_field_2: Optional[str] = None,
    ai_field_3: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update AI-derived fields for a chapter (atomic update)
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        ai_field_1: AI-generated high-level summary
        ai_field_2: AI-generated key points
        ai_field_3: AI-generated topics/themes
        
    Returns:
        Updated chapter record or None on error
    """
    try:
        update_data = {}
        
        if ai_field_1 is not None:
            update_data['ai_field_1'] = ai_field_1
        if ai_field_2 is not None:
            update_data['ai_field_2'] = ai_field_2
        if ai_field_3 is not None:
            update_data['ai_field_3'] = ai_field_3
            
        if not update_data:
            print(f"[DB!!] No AI fields to update")
            return None
        
        print(f"[DB->] UPDATE book_chapters AI fields WHERE book_id={book_id} AND chapter_id={chapter_id}")
        response = supabase.table("book_chapters").update(update_data).eq("book_id", book_id).eq("chapter_id", chapter_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Updated AI fields for chapter {chapter_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to update AI fields")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def delete_chapter(book_id: str, chapter_id: int) -> bool:
    """
    Delete a chapter (removes from DB and storage)
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        
    Returns:
        True if deleted, False on error
    """
    try:
        # Get chapter to find storage path
        chapter = get_chapter_details(book_id, chapter_id)
        if chapter and chapter.get('chapter_text_path'):
            # Delete from storage
            delete_chapter_from_storage(chapter['chapter_text_path'])
        
        # Delete from DB
        print(f"[DB->] DELETE book_chapters WHERE book_id={book_id} AND chapter_id={chapter_id}")
        supabase.table("book_chapters").delete().eq("book_id", book_id).eq("chapter_id", chapter_id).execute()
        print(f"[DB<-] Deleted chapter {chapter_id}")
        return True
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return False


def delete_all_chapters_for_book(book_id: str) -> bool:
    """
    Delete all chapters for a book (removes from DB and storage)
    
    Args:
        book_id: Book identifier
        
    Returns:
        True if deleted, False on error
    """
    try:
        # Delete from storage
        delete_book_chapters_from_storage(book_id)
        
        # Delete from DB
        print(f"[DB->] DELETE book_chapters WHERE book_id={book_id}")
        supabase.table("book_chapters").delete().eq("book_id", book_id).execute()
        print(f"[DB<-] Deleted all chapters for book {book_id}")
        return True
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return False


def update_chapter_text(book_id: str, chapter_id: int, chapter_text: str) -> Optional[Dict[str, Any]]:
    """
    Update chapter text in storage and metadata in DB
    Uses existing storage path to maintain persistence across reorders
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        chapter_text: New chapter text content
        
    Returns:
        Updated chapter dict or None on error
    """
    try:
        # Get existing chapter to find storage path
        print(f"[DB->] SELECT book_chapters WHERE book_id={book_id} AND chapter_id={chapter_id}")
        response = supabase.table("book_chapters")\
            .select("*")\
            .eq("book_id", book_id)\
            .eq("chapter_id", chapter_id)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            print(f"[DB!!] Chapter not found: {book_id}/{chapter_id}")
            return None
        
        chapter = response.data[0]
        storage_path = chapter.get('chapter_text_path')
        
        if not storage_path:
            print(f"[DB!!] No storage path for chapter: {book_id}/{chapter_id}")
            return None
        
        # Upload new text to storage using EXISTING path (maintains UUID)
        updated_storage_path = upload_chapter_text(book_id, chapter_text, existing_path=storage_path)
        if not updated_storage_path:
            print(f"[DB!!] Failed to upload chapter text to storage")
            return None
        
        # Update timestamp in DB
        print(f"[DB->] UPDATE book_chapters SET updated_at=NOW() WHERE book_id={book_id} AND chapter_id={chapter_id}")
        response = supabase.table("book_chapters")\
            .update({"updated_at": "NOW()"})\
            .eq("book_id", book_id)\
            .eq("chapter_id", chapter_id)\
            .execute()
        
        print(f"[DB<-] Updated chapter text for {book_id}/{chapter_id}")
        
        # Return updated chapter with new text
        updated_chapter = response.data[0] if response.data else chapter
        updated_chapter['chapter_text'] = chapter_text
        return updated_chapter
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def reorder_chapters(book_id: str, chapter_order: List[int]) -> bool:
    """
    Reorder chapters by updating their chapter_id values
    Storage paths (UUIDs) remain unchanged, ensuring file persistence
    Reindexes chapters sequentially starting from 1 (1-indexed)
    
    Args:
        book_id: Book identifier
        chapter_order: List of current chapter_ids in desired new order
        
    Returns:
        True if successful, False on error
    """
    try:
        # Get all chapters for this book
        print(f"[DB->] SELECT book_chapters WHERE book_id={book_id}")
        response = supabase.table("book_chapters")\
            .select("*")\
            .eq("book_id", book_id)\
            .order("chapter_id")\
            .execute()
        
        if not response.data:
            print(f"[DB!!] No chapters found for book: {book_id}")
            return False
        
        chapters = {ch['chapter_id']: ch for ch in response.data}
        
        # Verify all chapter_ids in order exist
        for old_id in chapter_order:
            if old_id not in chapters:
                print(f"[DB!!] Invalid chapter_id in order: {old_id}")
                return False
        
        # First, set all chapter_ids to negative temporary values to avoid conflicts
        print(f"[DB->] Setting temporary negative chapter_ids")
        for idx, old_id in enumerate(chapter_order):
            temp_id = -(idx + 1)
            supabase.table("book_chapters")\
                .update({"chapter_id": temp_id})\
                .eq("book_id", book_id)\
                .eq("chapter_id", old_id)\
                .execute()
        
        # Then update to final positions (1-indexed: 1, 2, 3, ...)
        # Note: chapter_text_path (UUID-based) remains unchanged during reordering
        print(f"[DB->] Updating to final chapter_id positions (1-indexed)")
        for idx, old_id in enumerate(chapter_order):
            temp_id = -(idx + 1)
            new_id = idx + 1  # 1-indexed: start from 1
            supabase.table("book_chapters")\
                .update({"chapter_id": new_id, "updated_at": "NOW()"})\
                .eq("book_id", book_id)\
                .eq("chapter_id", temp_id)\
                .execute()
        
        print(f"[DB<-] Reordered {len(chapter_order)} chapters for book {book_id} (1-indexed)")
        return True
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return False
