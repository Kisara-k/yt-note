"""
Fetch YouTube video details using the YouTube Data API v3
Supports batch fetching and stores data in Supabase
"""

import os
import sys
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import re

# Add parent directory to path to import youtube_crud
sys.path.append(os.path.join(os.path.dirname(__file__), 'db'))
from youtube_crud import create_or_update_video, bulk_create_or_update_videos

# Load environment variables
load_dotenv()

# YouTube API setup
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in environment variables. Please set it in your .env file")

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats
    
    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    - VIDEO_ID (plain ID)
    
    Args:
        url: YouTube URL or video ID
        
    Returns:
        Video ID or None if not found
    """
    # Already a video ID (11 characters, alphanumeric and dash/underscore)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    # Extract from various URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def fetch_video_details(video_ids: List[str]) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch video details from YouTube API using batch request
    Can fetch up to 50 videos in a single API call
    
    Args:
        video_ids: List of YouTube video IDs (max 50)
        
    Returns:
        List of video data dictionaries or None on error
    """
    try:
        # YouTube API allows up to 50 IDs per request
        if len(video_ids) > 50:
            print(f"⚠️  Warning: Batch size exceeds 50. Limiting to first 50 videos.")
            video_ids = video_ids[:50]
        
        # Join video IDs with commas
        video_ids_str = ','.join(video_ids)
        
        print(f"[API->] YouTube Data API: videos.list(ids={len(video_ids)})")
        
        # Make API request
        request = youtube.videos().list(
            part='snippet,contentDetails,status,statistics',
            id=video_ids_str
        )
        response = request.execute()
        
        videos = response.get('items', [])
        
        if not videos:
            print(f"[API<-] YouTube: No videos found")
            return []
        
        print(f"[API<-] YouTube: Retrieved {len(videos)} video(s)")
        
        return videos
        
    except HttpError as e:
        print(f"[API!!] YouTube API: {str(e)}")
        return None
    except Exception as e:
        print(f"[API!!] {str(e)}")
        return None


def fetch_and_store_videos(urls: List[str], batch_size: int = 50) -> Dict[str, Any]:
    """
    Fetch videos from YouTube and store them in Supabase
    Handles multiple batches if needed
    
    Args:
        urls: List of YouTube URLs or video IDs
        batch_size: Number of videos to fetch per API call (max 50)
        
    Returns:
        Dictionary with success/failure statistics
    """
    results = {
        'total': len(urls),
        'success': 0,
        'failed': 0,
        'invalid_urls': 0,
        'videos': []
    }
    
    print("\n" + "="*70)
    print(f"🎬 Fetching and storing {len(urls)} YouTube video(s)")
    print("="*70 + "\n")
    
    # Extract video IDs from URLs
    video_ids = []
    invalid_urls = []
    
    for url in urls:
        video_id = extract_video_id(url)
        if video_id:
            video_ids.append(video_id)
        else:
            invalid_urls.append(url)
            results['invalid_urls'] += 1
    
    if invalid_urls:
        print(f"⚠️  {len(invalid_urls)} invalid URL(s) found:")
        for url in invalid_urls:
            print(f"   - {url}")
        print()
    
    if not video_ids:
        print("❌ No valid video IDs found")
        return results
    
    # Process in batches
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(video_ids) + batch_size - 1) // batch_size
        
        print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} video(s))...")
        
        # Fetch from YouTube
        videos_data = fetch_video_details(batch)
        
        if videos_data:
            # Store in database
            print(f"💾 Storing {len(videos_data)} video(s) in database...")
            stored_videos = bulk_create_or_update_videos(videos_data)
            
            if stored_videos:
                results['success'] += len(stored_videos)
                results['videos'].extend(stored_videos)
            else:
                results['failed'] += len(videos_data)
        else:
            results['failed'] += len(batch)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 Summary:")
    print("="*70)
    print(f"   Total URLs provided: {results['total']}")
    print(f"   Invalid URLs: {results['invalid_urls']}")
    print(f"   Successfully stored: {results['success']}")
    print(f"   Failed: {results['failed']}")
    print("="*70 + "\n")
    
    return results


def fetch_single_video(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single video and store it in the database
    
    Args:
        url: YouTube URL or video ID
        
    Returns:
        Video data or None on error
    """
    video_id = extract_video_id(url)
    
    if not video_id:
        print(f"❌ Invalid YouTube URL or ID: {url}")
        return None
    
    print(f"\n🎥 Fetching video: {video_id}")
    
    videos_data = fetch_video_details([video_id])
    
    if videos_data and len(videos_data) > 0:
        video_data = videos_data[0]
        print(f"💾 Storing video in database...")
        result = create_or_update_video(video_data)
        return result
    
    return None


if __name__ == "__main__":
    """
    Test the video fetching functionality
    """
    
    # Test with sample URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "https://youtu.be/9bZkp7q19f0",  # Gangnam Style
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
    ]
    
    print("\n" + "="*70)
    print("🧪 Testing YouTube Video Fetching")
    print("="*70)
    
    # Test single video fetch
    print("\n1️⃣ Testing single video fetch...")
    single_result = fetch_single_video(test_urls[0])
    
    # Test batch fetch
    print("\n2️⃣ Testing batch video fetch...")
    batch_results = fetch_and_store_videos(test_urls)
    
    print("\n✅ Testing complete!")
