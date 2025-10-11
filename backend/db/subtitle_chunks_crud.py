"""
CRUD operations for subtitle chunks in Supabase
Simplified: No storage_path, no created_at, no processing_status
Empty AI fields indicate not yet processed
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def create_chunk(
    video_id: str,
    chunk_id: int,
    chunk_text: str,
    word_count: int,
    sentence_count: int,
    short_title: Optional[str] = None,
    ai_field_1: Optional[str] = None,
    ai_field_2: Optional[str] = None,
    ai_field_3: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a new subtitle chunk with optional AI fields
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier (0-indexed)
        chunk_text: Full text content of the chunk
        word_count: Number of words in chunk
        sentence_count: Number of sentences in chunk
        short_title: AI-generated short title (optional)
        ai_field_1: AI field 1 (optional)
        ai_field_2: AI field 2 (optional)
        ai_field_3: AI field 3 (optional)
        
    Returns:
        Created chunk record or None on error
    """
    try:
        chunk_data = {
            'video_id': video_id,
            'chunk_id': chunk_id,
            'chunk_text': chunk_text,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'short_title': short_title,
            'ai_field_1': ai_field_1,
            'ai_field_2': ai_field_2,
            'ai_field_3': ai_field_3
        }
        
        print(f"[DB->] UPSERT subtitle_chunks (video={video_id}, chunk={chunk_id}, text_len={len(chunk_text)})")
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


def get_chunks_by_video(video_id: str) -> List[Dict[str, Any]]:
    """
    Get all chunks for a video
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of chunk records ordered by chunk_id
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


def get_chunk_index(video_id: str) -> List[Dict[str, Any]]:
    """
    Get chunk index (chunk_id, start_time, end_time, short_title) for a video
    Used for dropdown display
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of {chunk_id, start_time, end_time, short_title} records
    """
    try:
        print(f"[DB->] SELECT chunk_index WHERE video_id={video_id}")
        response = supabase.table("subtitle_chunks").select(
            "chunk_id, start_time, end_time, short_title"
        ).eq("video_id", video_id).order("chunk_id").execute()
        
        result = response.data if response.data else []
        print(f"[DB<-] Found {len(result)} index entries")
        return result
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def get_chunk_details(video_id: str, chunk_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information for a specific chunk
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        
    Returns:
        Chunk record or None if not found
    """
    try:
        print(f"[DB->] SELECT chunk_details WHERE video_id={video_id}, chunk_id={chunk_id}")
        response = supabase.table("subtitle_chunks").select(
            "*"
        ).eq("video_id", video_id).eq("chunk_id", chunk_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found chunk {chunk_id}")
            return response.data[0]
        print(f"[DB<-] Chunk not found")
        return None
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def delete_chunks_by_video(video_id: str) -> bool:
    """
    Delete all chunks for a video
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
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
    
    Args:
        chunks: List of chunk dictionaries with required fields:
                video_id, chunk_id, start_time, end_time, chunk_text
        
    Returns:
        List of created chunks or None on error
    """
    try:
        # Ensure all chunks have the required fields and NULL AI fields
        for chunk in chunks:
            if 'short_title' not in chunk:
                chunk['short_title'] = None
            if 'ai_field_1' not in chunk:
                chunk['ai_field_1'] = None
            if 'ai_field_2' not in chunk:
                chunk['ai_field_2'] = None
            if 'ai_field_3' not in chunk:
                chunk['ai_field_3'] = None
        
        print(f"[DB->] BULK UPSERT subtitle_chunks (count={len(chunks)})")
        response = supabase.table("subtitle_chunks").upsert(chunks).execute()
        
        if response.data:
            print(f"[DB<-] Upserted {len(response.data)} chunks")
            return response.data
        else:
            print(f"[DB!!] Failed to create chunks")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_unprocessed_chunks(video_id: str) -> List[Dict[str, Any]]:
    """
    Get all chunks for a video that haven't been AI-processed yet
    (chunks where any AI field is NULL)
    
    Args:
        video_id: YouTube video ID
        
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
        
        print(f"[DB<-] Found {len(response.data) if response.data else 0} unprocessed chunks")
        return response.data if response.data else []
        
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
