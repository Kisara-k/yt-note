"""
CRUD operations for video notes in Supabase
Handles storing and retrieving markdown notes for YouTube videos
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from datetime import datetime

# Load environment variables from the same directory as this script
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def create_or_update_note(video_id: str, note_content: str, user_email: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new note or update existing one for a video
    Uses upsert to handle both create and update operations
    
    Args:
        video_id: YouTube video ID
        note_content: Markdown content of the note
        user_email: Email of the user (optional, for future multi-user support)
        
    Returns:
        Created/updated note record or None on error
    """
    try:
        note_data = {
            'video_id': video_id,
            'note_content': note_content,
            'user_email': user_email
        }
        
        response = supabase.table("video_notes").upsert(
            note_data,
            on_conflict='video_id'
        ).execute()
        
        if response.data and len(response.data) > 0:
            print(f"✓ Note saved for video: {video_id}")
            return response.data[0]
        else:
            print(f"✗ Failed to save note for video: {video_id}")
            return None
            
    except Exception as e:
        print(f"Error saving note: {str(e)}")
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
        response = supabase.table("video_notes").select("*").eq("video_id", video_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching note: {str(e)}")
        return None


def get_all_notes(user_email: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all notes, optionally filtered by user email
    
    Args:
        user_email: Filter by user email (optional)
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of note records
    """
    try:
        query = supabase.table("video_notes").select("*")
        
        if user_email:
            query = query.eq("user_email", user_email)
        
        response = query.order("updated_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        print(f"Error fetching notes: {str(e)}")
        return []


def get_notes_with_video_info(user_email: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get all notes with associated video information
    Uses a JOIN to combine video_notes and youtube_videos tables
    
    Args:
        user_email: Filter by user email (optional)
        limit: Maximum number of records to return
        
    Returns:
        List of note records with video information
    """
    try:
        # Select note fields and join with video info
        query = supabase.table("video_notes").select(
            "video_id, note_content, user_email, created_at, updated_at, "
            "youtube_videos(title, channel_title, published_at)"
        )
        
        if user_email:
            query = query.eq("user_email", user_email)
        
        response = query.order("updated_at", desc=True).limit(limit).execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        print(f"Error fetching notes with video info: {str(e)}")
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
        response = supabase.table("video_notes").delete().eq("video_id", video_id).execute()
        
        if response.data:
            print(f"✓ Deleted note for video: {video_id}")
            return True
        else:
            print(f"✗ Failed to delete note for video: {video_id}")
            return False
            
    except Exception as e:
        print(f"Error deleting note: {str(e)}")
        return False


# Example usage
if __name__ == "__main__":
    # Test creating a note
    test_video_id = "dQw4w9WgXcQ"
    test_note = "# Test Note\n\nThis is a test markdown note for the video."
    
    print("\n1. Creating/Updating a note:")
    note = create_or_update_note(test_video_id, test_note, "test@example.com")
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
