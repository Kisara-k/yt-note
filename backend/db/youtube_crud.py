"""
CRUD operations for YouTube videos in Supabase
Handles storing and retrieving YouTube video data from the database
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
from datetime import datetime

# Load environment variables from backend/.env (searches up the directory tree)
load_dotenv()

# Initialize Supabase client with SERVICE ROLE key (server-only, bypasses RLS)
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)


def parse_youtube_video_data(video_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse YouTube API video data into database-friendly format
    
    Args:
        video_data: Raw video data from YouTube API
        
    Returns:
        Dictionary formatted for database insertion
    """
    snippet = video_data.get('snippet', {})
    content_details = video_data.get('contentDetails', {})
    status = video_data.get('status', {})
    statistics = video_data.get('statistics', {})
    
    # Parse data
    parsed_data = {
        'id': video_data.get('id'),
        'kind': video_data.get('kind'),
        'etag': video_data.get('etag'),
        
        # Snippet fields
        'published_at': snippet.get('publishedAt'),
        'channel_id': snippet.get('channelId'),
        'title': snippet.get('title'),
        'description': snippet.get('description'),
        'channel_title': snippet.get('channelTitle'),
        'category_id': snippet.get('categoryId'),
        'live_broadcast_content': snippet.get('liveBroadcastContent'),
        'default_language': snippet.get('defaultLanguage'),
        'default_audio_language': snippet.get('defaultAudioLanguage'),
        
        # Tags as array
        'tags': snippet.get('tags', []),
        
        # Content details
        'duration': content_details.get('duration'),
        'dimension': content_details.get('dimension'),
        'definition': content_details.get('definition'),
        'caption': content_details.get('caption') == 'true' or content_details.get('caption') == True,
        'licensed_content': content_details.get('licensedContent'),
        'projection': content_details.get('projection'),
        
        # Status fields
        'upload_status': status.get('uploadStatus'),
        'privacy_status': status.get('privacyStatus'),
        'license': status.get('license'),
        'embeddable': status.get('embeddable'),
        'public_stats_viewable': status.get('publicStatsViewable'),
        'made_for_kids': status.get('madeForKids'),
        
        # Statistics (as integers)
        'view_count': int(statistics.get('viewCount', 0)),
        'like_count': int(statistics.get('likeCount', 0)),
        'favorite_count': int(statistics.get('favoriteCount', 0)),
        'comment_count': int(statistics.get('commentCount', 0)),
    }
    
    return parsed_data


def create_or_update_video(video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new video record or update existing one
    Uses upsert to handle both create and update operations
    
    Args:
        video_data: Raw video data from YouTube API
        
    Returns:
        Created/updated video record or None on error
    """
    try:
        parsed_data = parse_youtube_video_data(video_data)
        
        print(f"[DB->] UPSERT youtube_videos (id={parsed_data.get('id')}, title={parsed_data.get('title', '')[:30]}...)")
        response = supabase.table("youtube_videos").upsert(
            parsed_data,
            on_conflict='id'
        ).execute()
        
        if response.data:
            video_id = response.data[0].get('id')
            print(f"[DB<-] Upserted video: {video_id}")
            return response.data[0]
        else:
            print(f"[DB!!] No data returned for video upsert")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def bulk_create_or_update_videos(videos_data: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Bulk create or update multiple video records
    
    Args:
        videos_data: List of raw video data from YouTube API
        
    Returns:
        List of created/updated video records or None on error
    """
    try:
        parsed_videos = [parse_youtube_video_data(video) for video in videos_data]
        
        print(f"[DB->] BULK UPSERT youtube_videos (count={len(parsed_videos)})")
        response = supabase.table("youtube_videos").upsert(
            parsed_videos,
            on_conflict='id'
        ).execute()
        
        if response.data:
            print(f"[DB<-] Upserted {len(response.data)} videos")
            return response.data
        else:
            print(f"[DB!!] No data returned for bulk upsert")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_video_by_id(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single video by its ID
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Video record or None if not found
    """
    try:
        print(f"[DB->] SELECT youtube_videos WHERE id={video_id}")
        response = supabase.table("youtube_videos").select("*").eq("id", video_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found video: {response.data[0].get('title', '')[:40]}")
            return response.data[0]
        else:
            print(f"[DB<-] Video not found: {video_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_all_videos(limit: int = 100) -> Optional[List[Dict[str, Any]]]:
    """
    Get all videos (with optional limit)
    
    Args:
        limit: Maximum number of videos to return
        
    Returns:
        List of video records or None on error
    """
    try:
        print(f"[DB->] SELECT youtube_videos (limit={limit}, order=updated_at DESC)")
        response = supabase.table("youtube_videos").select("*").limit(limit).order('updated_at', desc=True).execute()
        
        if response.data:
            print(f"[DB<-] Retrieved {len(response.data)} videos")
            return response.data
        else:
            print(f"[DB<-] No videos found")
            return []
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_videos_by_channel(channel_id: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """
    Get all videos from a specific channel
    
    Args:
        channel_id: YouTube channel ID
        limit: Maximum number of videos to return
        
    Returns:
        List of video records or None on error
    """
    try:
        response = supabase.table("youtube_videos").select("*").eq("channel_id", channel_id).limit(limit).order('published_at', desc=True).execute()
        
        if response.data:
            print(f"✅ Retrieved {len(response.data)} videos from channel {channel_id}")
            return response.data
        else:
            print(f"⚠️  No videos found for channel: {channel_id}")
            return []
            
    except Exception as e:
        print(f"❌ Read Error: {e}")
        return None


def search_videos_by_tags(tags: List[str]) -> Optional[List[Dict[str, Any]]]:
    """
    Search videos that contain any of the specified tags
    
    Args:
        tags: List of tags to search for
        
    Returns:
        List of video records or None on error
    """
    try:
        # PostgreSQL array overlap operator - use cs (contains) instead of ov
        response = supabase.table("youtube_videos").select("*").filter("tags", "cs", f"{{{','.join(tags)}}}").order('view_count', desc=True).execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} videos with tags: {', '.join(tags)}")
            return response.data
        else:
            print(f"⚠️  No videos found with those tags")
            return []
            
    except Exception as e:
        print(f"❌ Search Error: {e}")
        return None


def delete_video(video_id: str) -> bool:
    """
    Delete a video by its ID
    Deletes storage files first, then DB record (which cascades to chunks)
    Note: video_notes are NOT deleted (preserved as orphaned records)
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        # Import here to avoid circular dependency
        from .subtitle_chunks_storage import delete_video_chunks_from_storage
        
        # Step 1: Delete all chunk files from storage
        print(f"[DELETE] Step 1: Deleting storage for video {video_id}")
        delete_video_chunks_from_storage(video_id)
        
        # Step 2: Delete video from DB (cascades to subtitle_chunks, but NOT video_notes)
        print(f"[DELETE] Step 2: Deleting video record {video_id}")
        response = supabase.table("youtube_videos").delete().eq("id", video_id).execute()
        
        print(f"✅ Deleted video: {video_id} (video_notes preserved if they exist)")
        return True
        
    except Exception as e:
        print(f"❌ Delete Error: {e}")
        return False


def get_recently_updated_videos(hours: int = 24, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """
    Get videos that were updated within the specified time period
    
    Args:
        hours: Number of hours to look back
        limit: Maximum number of videos to return
        
    Returns:
        List of video records or None on error
    """
    try:
        # Calculate the timestamp for the cutoff
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat()
        
        response = supabase.table("youtube_videos").select("*").gte("updated_at", cutoff_str).limit(limit).order('updated_at', desc=True).execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} videos updated in last {hours} hours")
            return response.data
        else:
            print(f"⚠️  No recently updated videos found")
            return []
            
    except Exception as e:
        print(f"❌ Read Error: {e}")
        return None


if __name__ == "__main__":
    """Test the CRUD operations with sample data"""
    print("\n" + "="*60)
    print("🎥 Testing YouTube Video CRUD Operations")
    print("="*60 + "\n")
    
    # Sample test data (from the provided JSON)
    sample_video = {
        "kind": "youtube#video",
        "etag": "69pihEvHGLXBHela9eq-UxFZTtA",
        "id": "dQw4w9WgXcQ",
        "snippet": {
            "publishedAt": "2009-10-25T06:57:33Z",
            "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
            "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
            "description": "The official video for Never Gonna Give You Up by Rick Astley.",
            "thumbnails": {
                "default": {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg", "width": 120, "height": 90}
            },
            "channelTitle": "Rick Astley",
            "tags": ["rick astley", "Never Gonna Give You Up", "rickroll"],
            "categoryId": "10",
            "liveBroadcastContent": "none",
            "defaultLanguage": "en"
        },
        "contentDetails": {
            "duration": "PT3M34S",
            "dimension": "2d",
            "definition": "hd",
            "caption": "true",
            "licensedContent": True,
            "projection": "rectangular"
        },
        "status": {
            "uploadStatus": "processed",
            "privacyStatus": "public",
            "license": "youtube",
            "embeddable": True,
            "publicStatsViewable": True,
            "madeForKids": False
        },
        "statistics": {
            "viewCount": "1701474331",
            "likeCount": "18579779",
            "favoriteCount": "0",
            "commentCount": "2405276"
        }
    }
    
    # Test create/update
    print("1️⃣ CREATE/UPDATE - Upserting a video...")
    result = create_or_update_video(sample_video)
    print()
    
    if result:
        # Test read by ID
        print("2️⃣ READ - Getting video by ID...")
        video = get_video_by_id("dQw4w9WgXcQ")
        print()
        
        # Test get all
        print("3️⃣ READ ALL - Getting all videos...")
        all_videos = get_all_videos(limit=10)
        print()
        
        # Test search by tags
        print("4️⃣ SEARCH - Searching by tags...")
        tagged_videos = search_videos_by_tags(["rickroll", "Never Gonna Give You Up"])
        print()
    
    print("\n" + "="*60)
    print("✅ Testing complete!")
    print("="*60 + "\n")
