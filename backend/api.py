"""
FastAPI backend for YouTube Notes application
Provides API endpoints for fetching video data and managing notes
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
load_dotenv()

# Add parent directory to path to import from db and backend folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from db.youtube_crud import create_or_update_video, get_video_by_id
from db.video_notes_crud import (
    create_or_update_note,
    get_note_by_video_id,
    get_all_notes,
    get_notes_with_video_info
)
from fetch_youtube_videos import fetch_video_details, extract_video_id
from auth import get_current_user, is_email_verified

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


class NoteResponse(BaseModel):
    video_id: str
    note_content: str
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
            note_content=request.note_content
        )
        
        if not note:
            raise HTTPException(status_code=500, detail="Failed to save note")
        
        return NoteResponse(
            video_id=note['video_id'],
            note_content=note['note_content'],
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


# Run with: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
