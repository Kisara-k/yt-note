"""
Supabase Storage operations for book chapters (2nd database)
Handles storing chapter text in storage bucket
"""

import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize Supabase client for 2nd database - use SERVICE key for storage operations
url: str = os.getenv("SUPABASE_URL_2")
key: str = os.getenv("SUPABASE_SERVICE_KEY_2")  # Use service key for admin operations
supabase: Client = create_client(url, key)

BUCKET_NAME = "book-chapters"


def ensure_bucket_exists() -> bool:
    """
    Ensure the book-chapters storage bucket exists
    Creates it if it doesn't exist
    
    Returns:
        True if bucket exists or was created, False on error
    """
    try:
        # Try to get bucket
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if BUCKET_NAME in bucket_names:
            print(f"[STORAGE] Bucket '{BUCKET_NAME}' exists")
            return True
        
        # Create bucket if it doesn't exist
        print(f"[STORAGE] Creating bucket '{BUCKET_NAME}'")
        supabase.storage.create_bucket(
            BUCKET_NAME,
            options={"public": False}  # Private bucket
        )
        print(f"[STORAGE] Bucket '{BUCKET_NAME}' created")
        return True
        
    except Exception as e:
        # Bucket might already exist, which throws an error
        print(f"[STORAGE] {str(e)}")
        return True  # Assume it exists


def upload_chapter_text(book_id: str, chapter_text: str, existing_path: Optional[str] = None) -> Optional[str]:
    """
    Upload chapter text to storage with a unique identifier
    
    Args:
        book_id: Book identifier
        chapter_text: Text content of the chapter
        existing_path: If provided, use this path (for updates); otherwise generate new UUID
        
    Returns:
        Storage path or None on error
    """
    try:
        if existing_path:
            # Use existing path for updates
            file_path = existing_path
        else:
            # Generate new unique identifier for new chapters
            unique_id = str(uuid.uuid4())
            file_path = f"{book_id}/{unique_id}.txt"
        
        print(f"[STORAGE->] Uploading to {BUCKET_NAME}/{file_path}")
        
        # Upload or update file
        supabase.storage.from_(BUCKET_NAME).upload(
            file_path,
            chapter_text.encode('utf-8'),
            file_options={"content-type": "text/plain", "upsert": "true"}
        )
        
        print(f"[STORAGE<-] Uploaded {file_path}")
        return file_path
        
    except Exception as e:
        print(f"[STORAGE!!] {str(e)}")
        return None


def download_chapter_text(file_path: str) -> Optional[str]:
    """
    Download chapter text from storage
    
    Args:
        file_path: Path to file in storage bucket
        
    Returns:
        Chapter text or None on error
    """
    try:
        print(f"[STORAGE->] Downloading {BUCKET_NAME}/{file_path}")
        
        response = supabase.storage.from_(BUCKET_NAME).download(file_path)
        
        if response:
            text = response.decode('utf-8')
            print(f"[STORAGE<-] Downloaded {len(text)} characters")
            return text
        else:
            print(f"[STORAGE!!] Failed to download {file_path}")
            return None
            
    except Exception as e:
        print(f"[STORAGE!!] {str(e)}")
        return None


def delete_book_chapters_from_storage(book_id: str) -> bool:
    """
    Delete all chapter files for a book from storage
    
    Args:
        book_id: Book identifier
        
    Returns:
        True if deleted, False on error
    """
    try:
        # List all files in the book's folder
        print(f"[STORAGE->] Listing files for book {book_id}")
        files = supabase.storage.from_(BUCKET_NAME).list(book_id)
        
        if not files:
            print(f"[STORAGE<-] No files found for book {book_id}")
            return True
        
        # Delete each file
        file_paths = [f"{book_id}/{f['name']}" for f in files]
        print(f"[STORAGE->] Deleting {len(file_paths)} files")
        supabase.storage.from_(BUCKET_NAME).remove(file_paths)
        
        print(f"[STORAGE<-] Deleted files for book {book_id}")
        return True
        
    except Exception as e:
        print(f"[STORAGE!!] {str(e)}")
        return False


def delete_chapter_from_storage(file_path: str) -> bool:
    """
    Delete a single chapter file from storage
    
    Args:
        file_path: Path to file in storage bucket
        
    Returns:
        True if deleted, False on error
    """
    try:
        print(f"[STORAGE->] Deleting {BUCKET_NAME}/{file_path}")
        supabase.storage.from_(BUCKET_NAME).remove([file_path])
        print(f"[STORAGE<-] Deleted {file_path}")
        return True
        
    except Exception as e:
        print(f"[STORAGE!!] {str(e)}")
        return False
