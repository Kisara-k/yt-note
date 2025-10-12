"""
Supabase Storage operations for subtitle chunks
Handles uploading/downloading chunk text to/from buckets
Uses service key for admin operations to bypass RLS
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Initialize Supabase client with service key for storage admin operations
url: str = os.getenv("SUPABASE_URL")
# Try to use service key first, fallback to regular key
service_key: str = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, service_key)

BUCKET_NAME = "subtitle-chunks"


def ensure_bucket_exists():
    """Create the subtitle-chunks bucket if it doesn't exist"""
    try:
        # Check if bucket exists
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if BUCKET_NAME not in bucket_names:
            # Create bucket with public access for reading
            supabase.storage.create_bucket(
                BUCKET_NAME,
                options={"public": False}  # Keep private, access via signed URLs
            )
            print(f"[STORAGE] Created bucket: {BUCKET_NAME}")
        else:
            print(f"[STORAGE] Bucket exists: {BUCKET_NAME}")
        return True
    except Exception as e:
        print(f"[STORAGE!!] Error with bucket: {str(e)}")
        return False


def upload_chunk_text(video_id: str, chunk_id: int, chunk_text: str) -> Optional[str]:
    """
    Upload chunk text to storage
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        chunk_text: Text content to upload
        
    Returns:
        Storage path (e.g., "video_id/chunk_0.txt") or None on error
    """
    try:
        # Create path: video_id/chunk_N.txt
        chunk_text_path = f"{video_id}/chunk_{chunk_id}.txt"
        
        # Upload to storage
        supabase.storage.from_(BUCKET_NAME).upload(
            chunk_text_path,
            chunk_text.encode('utf-8'),
            file_options={"content-type": "text/plain; charset=utf-8"}
        )
        
        print(f"[STORAGE->] Uploaded {chunk_text_path} ({len(chunk_text)} chars)")
        return chunk_text_path
    except Exception as e:
        # If file exists, update it
        if "already exists" in str(e).lower():
            try:
                supabase.storage.from_(BUCKET_NAME).update(
                    chunk_text_path,
                    chunk_text.encode('utf-8'),
                    file_options={"content-type": "text/plain; charset=utf-8"}
                )
                print(f"[STORAGE->] Updated {chunk_text_path} ({len(chunk_text)} chars)")
                return chunk_text_path
            except Exception as update_error:
                print(f"[STORAGE!!] Error updating: {str(update_error)}")
                return None
        else:
            print(f"[STORAGE!!] Error uploading: {str(e)}")
            return None


def download_chunk_text(chunk_text_path: str) -> Optional[str]:
    """
    Download chunk text from storage
    
    Args:
        chunk_text_path: Path in storage (e.g., "video_id/chunk_0.txt")
        
    Returns:
        Chunk text or None on error
    """
    try:
        response = supabase.storage.from_(BUCKET_NAME).download(chunk_text_path)
        text = response.decode('utf-8')
        print(f"[STORAGE<-] Downloaded {chunk_text_path} ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"[STORAGE!!] Error downloading {chunk_text_path}: {str(e)}")
        return None


def delete_video_chunks_from_storage(video_id: str) -> bool:
    """
    Delete all chunk files for a video from storage
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # List all files in the video's folder
        files = supabase.storage.from_(BUCKET_NAME).list(video_id)
        
        if not files:
            print(f"[STORAGE] No files found for video {video_id}")
            return True
        
        # Delete each file
        file_paths = [f"{video_id}/{file['name']}" for file in files]
        supabase.storage.from_(BUCKET_NAME).remove(file_paths)
        
        print(f"[STORAGE] Deleted {len(file_paths)} files for video {video_id}")
        return True
    except Exception as e:
        print(f"[STORAGE!!] Error deleting files: {str(e)}")
        return False


def delete_chunk_from_storage(chunk_text_path: str) -> bool:
    """
    Delete a single chunk file from storage
    
    Args:
        chunk_text_path: Path in storage (e.g., "video_id/chunk_0.txt")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase.storage.from_(BUCKET_NAME).remove([chunk_text_path])
        print(f"[STORAGE] Deleted {chunk_text_path}")
        return True
    except Exception as e:
        print(f"[STORAGE!!] Error deleting {chunk_text_path}: {str(e)}")
        return False
