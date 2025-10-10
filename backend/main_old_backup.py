"""
YouTube Notes Backend API Server
Main entry point to start the FastAPI backend server
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', '.env')
load_dotenv(env_path)


def main():
    """
    Start the FastAPI backend server
    """
    print("\n" + "="*70)
    print("🚀 YouTube Notes API Server")
    print("="*70 + "\n")
    
    # Server configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    print(f"📡 Starting server at http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")
    print("\n" + "="*70 + "\n")
    
    # Start the server
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()



def main():
    """
    Main function demonstrating the complete workflow
    """
    print("\n" + "="*70)
    print("🎬 YouTube Video Fetcher - Main Integration Demo")
    print("="*70 + "\n")
    
    # Example URLs to fetch
    example_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "https://youtu.be/9bZkp7q19f0",  # PSY - Gangnam Style
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Luis Fonsi - Despacito
    ]
    
    print("📋 Example URLs:")
    for i, url in enumerate(example_urls, 1):
        print(f"   {i}. {url}")
    print()
    
    # Step 1: Fetch and store videos
    print("="*70)
    print("STEP 1: Fetch videos from YouTube and store in database")
    print("="*70)
    results = fetch_and_store_videos(example_urls)
    
    if results['success'] > 0:
        # Step 2: Query the database
        print("\n" + "="*70)
        print("STEP 2: Query stored videos from database")
        print("="*70 + "\n")
        
        # Get all videos
        print("📚 All videos in database:")
        all_videos = get_all_videos(limit=10)
        if all_videos:
            for video in all_videos:
                print(f"   • {video['title'][:60]}...")
                print(f"     ID: {video['id']} | Views: {video['view_count']:,}")
        print()
        
        # Get a specific video
        if results['videos']:
            first_video_id = results['videos'][0]['id']
            print(f"🔍 Getting specific video (ID: {first_video_id}):")
            video = get_video_by_id(first_video_id)
            if video:
                print(f"   Title: {video['title']}")
                print(f"   Channel: {video['channel_title']}")
                print(f"   Views: {video['view_count']:,}")
                print(f"   Likes: {video['like_count']:,}")
                print(f"   Duration: {video['duration']}")
                print(f"   Published: {video['published_at']}")
                print(f"   Tags: {', '.join(video['tags'][:5]) if video['tags'] else 'No tags'}")
            print()
        
        # Search by tags
        print("🏷️  Searching for videos with specific tags:")
        tagged_videos = search_videos_by_tags(['music', 'official'])
        if tagged_videos:
            print(f"   Found {len(tagged_videos)} video(s)")
        print()
        
        # Get recently updated
        print("🕐 Recently updated videos (last 24 hours):")
        recent = get_recently_updated_videos(hours=24)
        if recent:
            for video in recent[:5]:
                print(f"   • {video['title'][:50]}... (Updated: {video['updated_at']})")
        print()
    
    print("="*70)
    print("✅ Demo complete!")
    print("="*70 + "\n")
    
    # Show usage instructions
    print("💡 Usage Examples:")
    print("   # Fetch a single video:")
    print("   from backend.fetch_youtube_videos import fetch_single_video")
    print("   video = fetch_single_video('https://www.youtube.com/watch?v=VIDEO_ID')")
    print()
    print("   # Fetch multiple videos:")
    print("   from backend.fetch_youtube_videos import fetch_and_store_videos")
    print("   results = fetch_and_store_videos([url1, url2, url3])")
    print()
    print("   # Query videos:")
    print("   from database.youtube_crud import get_all_videos, search_videos_by_tags")
    print("   videos = get_all_videos()")
    print("   tagged = search_videos_by_tags(['music', 'tutorial'])")
    print()


def interactive_mode():
    """
    Interactive mode for fetching videos
    """
    print("\n" + "="*70)
    print("🎬 YouTube Video Fetcher - Interactive Mode")
    print("="*70 + "\n")
    
    print("Enter YouTube URLs (one per line, empty line to finish):")
    urls = []
    
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)
    
    if urls:
        print(f"\n📋 You entered {len(urls)} URL(s)")
        print("🚀 Fetching and storing videos...\n")
        results = fetch_and_store_videos(urls)
        
        if results['success'] > 0:
            print("\n✅ Videos successfully stored!")
            print("\n📊 Video details:")
            for video in results['videos']:
                print(f"\n   {video['title']}")
                print(f"   ID: {video['id']}")
                print(f"   Channel: {video['channel_title']}")
                print(f"   Views: {video['view_count']:,}")
    else:
        print("❌ No URLs provided")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch YouTube videos and store in database')
    parser.add_argument('urls', nargs='*', help='YouTube URLs or video IDs to fetch')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('-d', '--demo', action='store_true', help='Run demo with example videos')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.demo or not args.urls:
        main()
    else:
        # Fetch provided URLs
        print(f"\n🚀 Fetching {len(args.urls)} video(s)...\n")
        results = fetch_and_store_videos(args.urls)
        
        if results['success'] > 0:
            print("\n✅ Videos successfully stored!")
