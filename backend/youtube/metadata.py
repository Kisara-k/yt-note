"""
YouTube module - Fetch video metadata from YouTube Data API v3
Input: video_id (str) or video_ids (list) - up to 50 IDs for batch
Output: Dict with video metadata
"""

import os
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import re

load_dotenv()


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_video_metadata(video_id: str, api_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Fetch metadata for a single video
    Returns: Dict with video metadata or None if error
    """
    if not api_key:
        api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        raise ValueError("YouTube API key not found")
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )
        
        response = request.execute()
        
        if not response.get('items'):
            return None
        
        item = response['items'][0]
        snippet = item.get('snippet', {})
        content_details = item.get('contentDetails', {})
        statistics = item.get('statistics', {})
        
        return {
            'video_id': video_id,
            'title': snippet.get('title'),
            'channel_title': snippet.get('channelTitle'),
            'channel_id': snippet.get('channelId'),
            'published_at': snippet.get('publishedAt'),
            'description': snippet.get('description'),
            'duration': content_details.get('duration'),
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url')
        }
        
    except HttpError as e:
        print(f"YouTube API error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching video: {e}")
        return None


def fetch_batch_metadata(video_ids: List[str], api_key: str = None) -> List[Dict[str, Any]]:
    """
    Fetch metadata for multiple videos (up to 50)
    Returns: List of video metadata dicts
    """
    if not api_key:
        api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        raise ValueError("YouTube API key not found")
    
    if len(video_ids) > 50:
        raise ValueError("Maximum 50 video IDs per batch request")
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids)
        )
        
        response = request.execute()
        
        results = []
        for item in response.get('items', []):
            video_id = item['id']
            snippet = item.get('snippet', {})
            content_details = item.get('contentDetails', {})
            statistics = item.get('statistics', {})
            
            results.append({
                'video_id': video_id,
                'title': snippet.get('title'),
                'channel_title': snippet.get('channelTitle'),
                'channel_id': snippet.get('channelId'),
                'published_at': snippet.get('publishedAt'),
                'description': snippet.get('description'),
                'duration': content_details.get('duration'),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url')
            })
        
        return results
        
    except HttpError as e:
        print(f"YouTube API error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []
