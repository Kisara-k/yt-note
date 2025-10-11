"""
FastAPI backend for YouTube Notes application
Provides API endpoints for fetching video data and managing notes
"""

import os
import sys
import threading
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
load_dotenv()

# Add parent directory to path to import from db and backend folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from db.youtube_crud import create_or_update_video, get_video_by_id, get_all_videos
from db.video_notes_crud import (
    create_or_update_note,
    get_note_by_video_id,
    get_all_notes,
    get_notes_with_video_info
)
from db.subtitle_chunks_crud import (
    get_chunks_by_video,
    get_chunk_index,
    get_chunk_details
)
from fetch_youtube_videos import fetch_video_details, extract_video_id
from auth import get_current_user, is_email_verified
from prompts import get_all_prompts, get_prompt_label
from background_worker import VideoProcessor

# Initialize FastAPI app
app = FastAPI(title="YouTube Notes API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class VideoRequest(BaseModel):
    video_url: str


class VideoResponse(BaseModel):
    video_id: str
    title: str
    channel_title: str
    channel_id: str
    published_at: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None


class NoteRequest(BaseModel):
    video_id: str
    note_content: str
    custom_tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    video_id: str
    note_content: str
    custom_tags: Optional[List[str]] = None
    created_at: str
    updated_at: str


class LoginRequest(BaseModel):
    email: str
    password: str


class VerifyEmailRequest(BaseModel):
    email: str


class VerifyEmailResponse(BaseModel):
    is_verified: bool
    message: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "YouTube Notes API", "version": "1.0.0"}


@app.post("/api/auth/verify-email", response_model=VerifyEmailResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    Verify if an email is in the allowed list
    This can be called before attempting Supabase authentication
    """
    is_verified = is_email_verified(request.email)
    
    if is_verified:
        return VerifyEmailResponse(
            is_verified=True,
            message="Email is verified and can access the application"
        )
    else:
        return VerifyEmailResponse(
            is_verified=False,
            message="Email is not authorized to access this application"
        )


@app.post("/api/video", response_model=VideoResponse)
async def get_video(request: VideoRequest, current_user: dict = Depends(get_current_user)):
    """
    Get video information by URL or ID
    Fetches from database if exists, otherwise calls YouTube API
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL or ID")
        
        # Check if video exists in database
        video = get_video_by_id(video_id)
        
        if not video:
            # Fetch from YouTube API and store in database
            print(f"Video {video_id} not in database, fetching from YouTube API...")
            videos_data = fetch_video_details([video_id])
            
            if not videos_data or len(videos_data) == 0:
                raise HTTPException(status_code=404, detail="Video not found on YouTube")
            
            # Store in database
            video = create_or_update_video(videos_data[0])
            
            if not video:
                raise HTTPException(status_code=500, detail="Failed to store video in database")
        
        # Return video information
        return VideoResponse(
            video_id=video['id'],
            title=video['title'],
            channel_title=video['channel_title'],
            channel_id=video['channel_id'],
            published_at=video.get('published_at'),
            description=video.get('description'),
            duration=video.get('duration'),
            view_count=video.get('view_count'),
            like_count=video.get('like_count')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/note/{video_id}")
async def get_note(video_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get note for a specific video
    Returns None if no note exists
    Requires authentication
    """
    try:
        note = get_note_by_video_id(video_id)
        return note if note else {"video_id": video_id, "note_content": None}
        
    except Exception as e:
        print(f"Error in get_note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/note", response_model=NoteResponse)
async def save_note(request: NoteRequest, current_user: dict = Depends(get_current_user)):
    """
    Create or update a note for a video
    Requires authentication
    """
    try:
        note = create_or_update_note(
            video_id=request.video_id,
            note_content=request.note_content,
            custom_tags=request.custom_tags
        )
        
        if not note:
            raise HTTPException(status_code=500, detail="Failed to save note")
        
        return NoteResponse(
            video_id=note['video_id'],
            note_content=note['note_content'],
            custom_tags=note.get('custom_tags', []),
            created_at=note['created_at'],
            updated_at=note['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in save_note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes")
async def get_notes(limit: int = 50, current_user: dict = Depends(get_current_user)):
    """
    Get all notes with video information
    Requires authentication
    """
    try:
        notes = get_notes_with_video_info(limit=limit)
        return {"notes": notes, "count": len(notes)}
        
    except Exception as e:
        print(f"Error in get_notes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/creator-notes")
async def get_creator_notes(
    channel: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get notes filtered by channel/creator name
    Requires authentication
    """
    try:
        # Get all notes with video info
        all_notes = get_notes_with_video_info(limit=1000)  # Get more to filter
        
        # Filter by channel name (case-insensitive partial match)
        filtered_notes = [
            note for note in all_notes
            if note.get('channel_title') and 
            channel.lower() in note['channel_title'].lower()
        ]
        
        # Limit results
        filtered_notes = filtered_notes[:limit]
        
        return {
            "notes": filtered_notes,
            "count": len(filtered_notes),
            "channel": channel
        }
        
    except Exception as e:
        print(f"Error in get_creator_notes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos")
async def get_videos(limit: int = 100, current_user: dict = Depends(get_current_user)):
    """
    Get all videos
    Requires authentication
    """
    try:
        videos = get_all_videos(limit=limit)
        return {"videos": videos or [], "count": len(videos) if videos else 0}
        
    except Exception as e:
        print(f"Error in get_videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# Chunk Endpoints
# ===================================================

@app.get("/api/chunks/{video_id}")
async def get_video_chunks(video_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get all chunks for a video
    Requires authentication
    """
    try:
        chunks = get_chunks_by_video(video_id)
        return {"video_id": video_id, "chunks": chunks, "count": len(chunks)}
        
    except Exception as e:
        print(f"Error in get_video_chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks/{video_id}/index")
async def get_video_chunk_index(video_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get chunk index (chunk_id and short_title) for a video
    Used for dropdown display
    Requires authentication
    """
    try:
        index = get_chunk_index(video_id)
        return {"video_id": video_id, "index": index, "count": len(index)}
        
    except Exception as e:
        print(f"Error in get_video_chunk_index: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks/{video_id}/{chunk_id}")
async def get_chunk(video_id: str, chunk_id: int, current_user: dict = Depends(get_current_user)):
    """
    Get detailed information for a specific chunk
    Requires authentication
    """
    try:
        chunk = get_chunk_details(video_id, chunk_id)
        
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        return chunk
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_chunk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# Video Processing Endpoint
# ===================================================

@app.post("/api/jobs/process-video")
async def process_video_endpoint(request: VideoRequest, current_user: dict = Depends(get_current_user)):
    """
    Process a video immediately (extract subtitles, chunk, and enrich with AI)
    Runs in background thread. Requires authentication.
    """
    try:
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL or ID")
        
        # Check if video exists
        video = get_video_by_id(video_id)
        
        if not video:
            # Fetch and store video metadata first
            videos_data = fetch_video_details([video_id])
            
            if not videos_data or len(videos_data) == 0:
                raise HTTPException(status_code=404, detail="Video not found on YouTube")
            
            video = create_or_update_video(videos_data[0])
            
            if not video:
                raise HTTPException(status_code=500, detail="Failed to store video in database")
        
        # Start processing in background thread
        def process_in_background():
            try:
                processor = VideoProcessor()
                processor.process_video(video_id)
            except Exception as e:
                print(f"[!!] Background processing error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
        
        return {
            "message": "Video processing started",
            "video_id": video_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[!!] Error starting video processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test/process-video-no-auth")
async def process_video_no_auth(request: VideoRequest):
    """
    TEST ENDPOINT: Process video without authentication (for testing only)
    """
    try:
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL or ID")
        
        print(f"\n{'='*70}")
        print(f"[TEST] Processing video without auth: {video_id}")
        print(f"{'='*70}\n")
        
        # Check if video exists
        video = get_video_by_id(video_id)
        
        if not video:
            # Fetch and store video metadata first
            videos_data = fetch_video_details([video_id])
            
            if not videos_data or len(videos_data) == 0:
                raise HTTPException(status_code=404, detail="Video not found on YouTube")
            
            video = create_or_update_video(videos_data[0])
            
            if not video:
                raise HTTPException(status_code=500, detail="Failed to store video in database")
        
        # Start processing in background thread
        def process_in_background():
            try:
                processor = VideoProcessor()
                processor.process_video(video_id)
            except Exception as e:
                print(f"[!!] Background processing error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
        
        return {
            "message": "Video processing started (TEST MODE - NO AUTH)",
            "video_id": video_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[!!] Error starting video processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================
# Prompts Configuration Endpoints (Read-only - hardcoded)
# ===================================================

@app.get("/api/prompts")
async def get_prompts(current_user: dict = Depends(get_current_user)):
    """
    Get all prompt configurations (hardcoded, read-only)
    Requires authentication
    """
    try:
        prompts = get_all_prompts()
        # Convert to list format expected by frontend
        prompts_list = [
            {
                'field_name': field_name,
                'label': config['label'],
                'template': config['template']
            }
            for field_name, config in prompts.items()
        ]
        return {"prompts": prompts_list, "count": len(prompts_list)}
        
    except Exception as e:
        print(f"Error in get_prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
