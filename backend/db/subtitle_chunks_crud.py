"""
CRUD operations for subtitle chunks in Supabase
Uses Supabase Storage for chunk text, DB for metadata and AI fields
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from .subtitle_chunks_storage import (
    ensure_bucket_exists,
    upload_chunk_text,
    download_chunk_text,
    delete_video_chunks_from_storage,
    delete_chunk_from_storage
)

# Load environment variables
load_dotenv()

# Initialize Supabase client with SERVICE ROLE key (server-only, bypasses RLS)
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

# Ensure storage bucket exists on module load
ensure_bucket_exists()


def load_chunk_text(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load chunk text from storage and add it to the chunk dict
    Modifies chunk in-place and returns it
    
    Args:
        chunk: Chunk dictionary with chunk_text_path
        
    Returns:
        Chunk dictionary with chunk_text added
    """
    if chunk.get('chunk_text_path'):
        chunk_text = download_chunk_text(chunk['chunk_text_path'])
        chunk['chunk_text'] = chunk_text if chunk_text else None
    else:
        chunk['chunk_text'] = None
    return chunk


def load_chunks_text(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Load chunk text from storage for multiple chunks
    Modifies chunks in-place and returns them
    
    Args:
        chunks: List of chunk dictionaries with chunk_text_path
        
    Returns:
        List of chunk dictionaries with chunk_text added
    """
    for chunk in chunks:
        load_chunk_text(chunk)
    return chunks


def create_chunk(
    video_id: str,
    chunk_id: int,
    chunk_text: str,
    short_title: Optional[str] = None,
    ai_field_1: Optional[str] = None,
    ai_field_2: Optional[str] = None,
    ai_field_3: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a new subtitle chunk with optional AI fields
    Stores chunk text in storage, metadata in DB
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier (1-indexed: starts from 1)
        chunk_text: Full text content of the chunk
        short_title: AI-generated short title (optional)
        ai_field_1: AI field 1 (optional)
        ai_field_2: AI field 2 (optional)
        ai_field_3: AI field 3 (optional)
        
    Returns:
        Created chunk record or None on error
    """
    try:
        # Upload chunk text to storage
        chunk_text_path = upload_chunk_text(video_id, chunk_id, chunk_text)
        if not chunk_text_path:
            print(f"[DB!!] Failed to upload chunk text to storage")
            return None
        
        chunk_data = {
            'video_id': video_id,
            'chunk_id': chunk_id,
            'chunk_text_path': chunk_text_path,
            'short_title': short_title,
            'ai_field_1': ai_field_1,
            'ai_field_2': ai_field_2,
            'ai_field_3': ai_field_3
        }
        
        print(f"[DB->] UPSERT subtitle_chunks (video={video_id}, chunk={chunk_id}, storage={chunk_text_path})")
        response = supabase.table("subtitle_chunks").upsert(chunk_data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Upserted chunk {chunk_id} for video {video_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to create chunk {chunk_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def update_chunk_ai_fields(
    video_id: str,
    chunk_id: int,
    short_title: Optional[str] = None,
    ai_field_1: Optional[str] = None,
    ai_field_2: Optional[str] = None,
    ai_field_3: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update AI-derived fields for a chunk (atomic update)
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        short_title: AI-generated short title
        ai_field_1: AI-generated high-level summary
        ai_field_2: AI-generated key points
        ai_field_3: AI-generated topics/themes
        
    Returns:
        Updated chunk record or None on error
    """
    try:
        update_data = {}
        
        if short_title is not None:
            update_data['short_title'] = short_title
        if ai_field_1 is not None:
            update_data['ai_field_1'] = ai_field_1
        if ai_field_2 is not None:
            update_data['ai_field_2'] = ai_field_2
        if ai_field_3 is not None:
            update_data['ai_field_3'] = ai_field_3
        
        if not update_data:
            print("[DB!!] No AI fields to update")
            return None
        
        print(f"[DB->] UPDATE subtitle_chunks (video={video_id}, chunk={chunk_id}, fields={len(update_data)})")
        response = supabase.table("subtitle_chunks").update(
            update_data
        ).eq("video_id", video_id).eq("chunk_id", chunk_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Updated AI fields for chunk {chunk_id}")
            return response.data[0]
        else:
            print(f"[DB!!] No chunk found: {video_id}/{chunk_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def update_chunk_note(
    video_id: str,
    chunk_id: int,
    note_content: str
) -> Optional[Dict[str, Any]]:
    """
    Update user note content for a chunk
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        note_content: Markdown content of the note
        
    Returns:
        Updated chunk record or None on error
    """
    try:
        update_data = {'note_content': note_content}
        
        print(f"[DB->] UPDATE subtitle_chunks note_content (video={video_id}, chunk={chunk_id}, len={len(note_content)})")
        response = supabase.table("subtitle_chunks").update(
            update_data
        ).eq("video_id", video_id).eq("chunk_id", chunk_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Updated note for chunk {chunk_id}")
            return response.data[0]
        else:
            print(f"[DB!!] No chunk found: {video_id}/{chunk_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def update_chunk_text(
    video_id: str,
    chunk_id: int,
    chunk_text: str
) -> Optional[Dict[str, Any]]:
    """
    Update chunk text content in storage
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        chunk_text: New text content for the chunk
        
    Returns:
        Updated chunk record or None on error
    """
    try:
        # Get current chunk to get the text path
        print(f"[DB->] SELECT subtitle_chunks WHERE video_id={video_id}, chunk_id={chunk_id}")
        response = supabase.table("subtitle_chunks").select(
            "chunk_text_path"
        ).eq("video_id", video_id).eq("chunk_id", chunk_id).execute()
        
        if not response.data or len(response.data) == 0:
            print(f"[DB!!] No chunk found: {video_id}/{chunk_id}")
            return None
        
        # Upload new chunk text to storage (this will overwrite the existing file)
        chunk_text_path = upload_chunk_text(video_id, chunk_id, chunk_text)
        if not chunk_text_path:
            print(f"[DB!!] Failed to upload updated chunk text to storage")
            return None
        
        print(f"[DB->] Updated chunk text in storage for chunk {chunk_id}")
        
        # Return the updated chunk with text loaded
        chunk = response.data[0]
        chunk['chunk_text'] = chunk_text
        return chunk
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_chunks_by_video(video_id: str) -> List[Dict[str, Any]]:
    """
    Get all chunks for a video
    Note: chunk_text is loaded from storage on demand
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of chunk records ordered by chunk_id (includes chunk_text_path, not chunk_text)
    """
    try:
        print(f"[DB->] SELECT subtitle_chunks WHERE video_id={video_id}")
        response = supabase.table("subtitle_chunks").select(
            "*"
        ).eq("video_id", video_id).order("chunk_id").execute()
        
        result = response.data if response.data else []
        print(f"[DB<-] Found {len(result)} chunks")
        return result
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def get_chunk_metadata(video_id: str, chunk_id: int) -> Optional[Dict[str, Any]]:
    """
    Get chunk metadata only (no text loading from storage)
    Lightweight query for verification and titles
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        
    Returns:
        Chunk metadata without chunk_text
    """
    try:
        print(f"[DB->] SELECT chunk metadata WHERE video_id={video_id} AND chunk_id={chunk_id}")
        response = supabase.table("subtitle_chunks").select("*").eq("video_id", video_id).eq("chunk_id", chunk_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found chunk {chunk_id} metadata")
            return response.data[0]
        else:
            print(f"[DB<-] Chunk not found")
            return None

    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_chunk_details(video_id: str, chunk_id: int, include_text: bool = True) -> Optional[Dict[str, Any]]:
    """
    Get detailed information for a specific chunk
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        include_text: If True, fetch chunk_text from storage
        
    Returns:
        Chunk record or None if not found
    """
    try:
        print(f"[DB->] SELECT chunk_details WHERE video_id={video_id}, chunk_id={chunk_id}")
        response = supabase.table("subtitle_chunks").select(
            "*"
        ).eq("video_id", video_id).eq("chunk_id", chunk_id).execute()
        
        if response.data and len(response.data) > 0:
            chunk = response.data[0]
            
            # Load chunk text from storage if requested
            if include_text and chunk.get('chunk_text_path'):
                chunk_text = download_chunk_text(chunk['chunk_text_path'])
                if chunk_text:
                    chunk['chunk_text'] = chunk_text
                else:
                    print(f"[DB!!] Failed to load chunk text from storage")
                    chunk['chunk_text'] = None
            
            print(f"[DB<-] Found chunk {chunk_id}")
            return chunk
        print(f"[DB<-] Chunk not found")
        return None
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_chunk_index(video_id: str) -> List[Dict[str, Any]]:
    """
    Get chunk index (chunk_id, short_title) for a video
    Used for dropdown display
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of {chunk_id, short_title} records
    """
    try:
        print(f"[DB->] SELECT chunk_index WHERE video_id={video_id}")
        response = supabase.table("subtitle_chunks").select(
            "chunk_id, short_title"
        ).eq("video_id", video_id).order("chunk_id").execute()
        
        result = response.data if response.data else []
        print(f"[DB<-] Found {len(result)} index entries")
        return result
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def delete_chunks_by_video(video_id: str) -> bool:
    """
    Delete all chunks for a video (both DB records and storage files)
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Delete from storage first
        delete_video_chunks_from_storage(video_id)
        
        # Then delete from database
        print(f"[DB->] DELETE subtitle_chunks WHERE video_id={video_id}")
        response = supabase.table("subtitle_chunks").delete().eq(
            "video_id", video_id
        ).execute()
        
        print(f"[DB<-] Deleted chunks for video: {video_id}")
        return True
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return False


def bulk_create_chunks(chunks: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Create multiple chunks in a single request
    Uploads all chunk texts to storage, then creates DB records
    
    Args:
        chunks: List of chunk dictionaries with required fields:
                video_id, chunk_id, chunk_text
        
    Returns:
        List of created chunks or None on error
    """
    try:
        # First, upload all chunk texts to storage
        db_chunks = []
        for chunk in chunks:
            video_id = chunk['video_id']
            chunk_id = chunk['chunk_id']
            chunk_text = chunk['chunk_text']
            
            chunk_text_path = upload_chunk_text(video_id, chunk_id, chunk_text)
            if not chunk_text_path:
                print(f"[DB!!] Failed to upload chunk {chunk_id} to storage")
                continue
            
            # Prepare DB record with storage path instead of text
            db_chunk = {
                'video_id': video_id,
                'chunk_id': chunk_id,
                'chunk_text_path': chunk_text_path,
                'short_title': chunk.get('short_title'),
                'ai_field_1': chunk.get('ai_field_1'),
                'ai_field_2': chunk.get('ai_field_2'),
                'ai_field_3': chunk.get('ai_field_3')
            }
            db_chunks.append(db_chunk)
        
        if not db_chunks:
            print(f"[DB!!] No chunks to upload")
            return None
        
        # Bulk insert to database
        print(f"[DB->] BULK UPSERT subtitle_chunks (count={len(db_chunks)})")
        response = supabase.table("subtitle_chunks").upsert(db_chunks).execute()
        
        if response.data:
            print(f"[DB<-] Upserted {len(response.data)} chunks")
            return response.data
        else:
            print(f"[DB!!] Failed to create chunks")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def bulk_update_ai_fields(video_id: str, enriched_chunks: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Update AI fields for multiple chunks using targeted UPDATE statements
    
    NOTE: Uses a loop instead of bulk upsert because:
    - Chunk text is 5-10x larger than AI fields
    - UPDATE only sends small AI fields (~400 chars/chunk)
    - UPSERT would require fetching + re-uploading chunk_text (~1400 chars/chunk)
    - Loop with small updates is more efficient than bulk with large data
    
    Args:
        video_id: YouTube video ID
        enriched_chunks: List of dicts with chunk_id and AI fields (title, field_1, field_2, field_3)
        
    Returns:
        List of updated chunks or None on error
    """
    try:
        print(f"[DB->] Updating AI fields for {len(enriched_chunks)} chunks (targeted updates)")
        
        updated_chunks = []
        for chunk in enriched_chunks:
            # Update only AI fields - no need to send chunk_text
            update_data = {
                'short_title': chunk.get('title', ''),
                'ai_field_1': chunk.get('field_1', ''),
                'ai_field_2': chunk.get('field_2', ''),
                'ai_field_3': chunk.get('field_3', '')
            }
            
            response = supabase.table("subtitle_chunks").update(update_data).eq(
                'video_id', video_id
            ).eq(
                'chunk_id', chunk['chunk_id']
            ).execute()
            
            if response.data and len(response.data) > 0:
                updated_chunks.extend(response.data)
        
        if updated_chunks:
            print(f"[DB<-] Updated {len(updated_chunks)} chunks with AI fields")
            return updated_chunks
        else:
            print(f"[DB!!] Failed to update chunks")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_unprocessed_chunks(video_id: str, include_text: bool = True) -> List[Dict[str, Any]]:
    """
    Get all chunks for a video that haven't been AI-processed yet
    (chunks where any AI field is NULL)
    
    Args:
        video_id: YouTube video ID
        include_text: If True, fetch chunk_text from storage for each chunk
        
    Returns:
        List of unprocessed chunk records
    """
    try:
        print(f"[DB->] SELECT subtitle_chunks WHERE video_id={video_id} AND AI fields NULL")
        response = supabase.table("subtitle_chunks").select(
            "*"
        ).eq("video_id", video_id).or_(
            "short_title.is.null,ai_field_1.is.null,ai_field_2.is.null,ai_field_3.is.null"
        ).order("chunk_id").execute()
        
        chunks = response.data if response.data else []
        
        # Load chunk text from storage if requested
        if include_text:
            for chunk in chunks:
                if chunk.get('chunk_text_path'):
                    chunk_text = download_chunk_text(chunk['chunk_text_path'])
                    chunk['chunk_text'] = chunk_text if chunk_text else None
        
        print(f"[DB<-] Found {len(chunks)} unprocessed chunks")
        return chunks
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def is_chunk_processed(chunk: Dict[str, Any]) -> bool:
    """
    Check if a chunk has been fully processed by AI
    
    Args:
        chunk: Chunk dictionary
        
    Returns:
        True if all AI fields are populated, False otherwise
    """
    return all([
        chunk.get('short_title'),
        chunk.get('ai_field_1'),
        chunk.get('ai_field_2'),
        chunk.get('ai_field_3')
    ])


def get_processing_progress(video_id: str) -> Dict[str, Any]:
    """
    Get processing progress for a video's chunks
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Dictionary with total, processed, and unprocessed counts
    """
    try:
        all_chunks = get_chunks_by_video(video_id)
        total = len(all_chunks)
        processed = sum(1 for chunk in all_chunks if is_chunk_processed(chunk))
        
        return {
            'video_id': video_id,
            'total_chunks': total,
            'processed_chunks': processed,
            'unprocessed_chunks': total - processed,
            'progress_percent': (processed / total * 100) if total > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting processing progress: {str(e)}")
        return {
            'video_id': video_id,
            'total_chunks': 0,
            'processed_chunks': 0,
            'unprocessed_chunks': 0,
            'progress_percent': 0
        }
