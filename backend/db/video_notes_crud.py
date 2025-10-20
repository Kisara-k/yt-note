"""
CRUD operations for video notes in Supabase
Handles storing and retrieving markdown notes for YouTube videos
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from datetime import datetime

# Load environment variables from backend/.env (searches up the directory tree)
load_dotenv()

# Initialize Supabase client with SERVICE ROLE key (server-only, bypasses RLS)
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)


def create_or_update_note(
    video_id: str, 
    note_content: str, 
    custom_tags: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a new note or update existing one for a video
    
    Args:
        video_id: YouTube video ID
        note_content: Markdown content of the note
        custom_tags: List of custom tag strings
        
    Returns:
        Created/updated note record or None on error
    """
    try:
        note_data = {
            'video_id': video_id,
            'note_content': note_content,
            'custom_tags': custom_tags or []
        }
        
        print(f"[DB->] UPSERT video_notes (video_id={video_id}, content_len={len(note_content)}, tags={len(custom_tags or [])})")
        response = supabase.table("video_notes").upsert(
            note_data,
            on_conflict='video_id'
        ).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Note saved for video: {video_id}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to save note for video: {video_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_note_by_video_id(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Get note for a specific video
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Note record or None if not found
    """
    try:
        print(f"[DB->] SELECT video_notes WHERE video_id={video_id}")
        response = supabase.table("video_notes").select("*").eq("video_id", video_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found note for video: {video_id}")
            return response.data[0]
        else:
            print(f"[DB<-] No note found for video: {video_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_all_notes(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all notes
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of note records
    """
    try:
        print(f"[DB->] SELECT video_notes (limit={limit}, offset={offset})")
        query = supabase.table("video_notes").select("*")
        
        response = query.order("updated_at", desc=True).range(offset, offset + limit - 1).execute()
        
        print(f"[DB<-] Retrieved {len(response.data) if response.data else 0} notes")
        return response.data if response.data else []
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def get_notes_with_video_info(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get all notes with associated video information
    Uses a JOIN to combine video_notes and youtube_videos tables
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of note records with video information
    """
    try:
        print(f"[DB->] SELECT video_notes JOIN youtube_videos (limit={limit})")
        # Select note fields and join with video info
        query = supabase.table("video_notes").select(
            "video_id, note_content, created_at, updated_at, "
            "youtube_videos(title, channel_title, published_at)"
        )
        
        response = query.order("updated_at", desc=True).limit(limit).execute()
        
        print(f"[DB<-] Retrieved {len(response.data) if response.data else 0} notes with video info")
        return response.data if response.data else []
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def delete_note(video_id: str) -> bool:
    """
    Delete a note by video ID
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"[DB->] DELETE video_notes WHERE video_id={video_id}")
        response = supabase.table("video_notes").delete().eq("video_id", video_id).execute()
        
        if response.data:
            print(f"[DB<-] Deleted note for video: {video_id}")
            return True
        else:
            print(f"[DB<-] No note to delete for video: {video_id}")
            return False
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return False


# Example usage
if __name__ == "__main__":
    # Test creating a note
    test_video_id = "dQw4w9WgXcQ"
    test_note = "# Test Note\n\nThis is a test markdown note for the video."
    
    print("\n1. Creating/Updating a note:")
    note = create_or_update_note(test_video_id, test_note)
    if note:
        print(f"   Note saved: {note}")
    
    print("\n2. Getting note by video ID:")
    note = get_note_by_video_id(test_video_id)
    if note:
        print(f"   Found note: {note}")
    else:
        print("   Note not found")
    
    print("\n3. Getting all notes:")
    notes = get_all_notes()
    print(f"   Found {len(notes)} notes")
    
    print("\n4. Getting notes with video info:")
    notes_with_info = get_notes_with_video_info()
    print(f"   Found {len(notes_with_info)} notes with video info")
    for note in notes_with_info:
        print(f"   - {note.get('video_id')}: {note.get('youtube_videos', {}).get('title', 'N/A')}")
