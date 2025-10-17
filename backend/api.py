"""
FastAPI backend for YouTube Notes
Uses orchestrator for all module coordination
"""

import os
import sys
import threading
import json
import re
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Import orchestrator (handles all module coordination)
from orchestrator import (
    process_video_metadata,
    process_batch_metadata,
    process_full_video,
    process_multiple_videos_parallel,
    process_video_subtitles_only,
    process_ai_enrichment_only,
    process_book_chapter_ai_enrichment,
    process_book_all_chapters_ai_enrichment,
    process_video_chunk_ai_enrichment,
    process_video_all_chunks_ai_enrichment
)

# Import from auth and db directly
from auth import get_current_user, is_email_verified
from prompts import get_all_prompts, get_prompt_label
from db.youtube_crud import get_video_by_id, get_all_videos, delete_video
from db.video_notes_crud import (
    create_or_update_note,
    get_note_by_video_id,
    get_notes_with_video_info
)
from db.subtitle_chunks_crud import (
    get_chunks_by_video,
    get_chunk_index,
    get_chunk_details,
    load_chunks_text,
    update_chunk_note,
    update_chunk_text
)
from db.books_crud import (
    create_book,
    get_book_by_id,
    get_all_books,
    delete_book
)
from db.book_chapters_crud import (
    create_chapter,
    get_chapters_by_book,
    get_chapter_index,
    get_chapter_details,
    update_chapter_note,
    update_chapter_text,
    delete_chapter,
    reorder_chapters
)
from db.book_notes_crud import (
    create_or_update_note as create_or_update_book_note,
    get_note_by_book_id,
    get_notes_with_book_info
)

app = FastAPI(title="YouTube Notes API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
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


class BookRequest(BaseModel):
    book_id: str
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    book_type: Optional[str] = None  # 'book', 'lecture', etc. - defaults to 'book'
    chapters: List[Dict[str, Any]]  # Flexible: accept any dict, will normalize later
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"


class BookNoteRequest(BaseModel):
    book_id: str
    note_content: str
    custom_tags: Optional[List[str]] = None


class ChapterNoteRequest(BaseModel):
    book_id: str
    chapter_id: int
    note_content: str


class BookChapterAIRequest(BaseModel):
    book_id: str
    chapter_id: int
    chapter_text: Optional[str] = None  # Optional: provide to avoid database load


class BookAIRequest(BaseModel):
    book_id: str


class VideoAIRequest(BaseModel):
    video_id: str


class VideoChunkAIRequest(BaseModel):
    video_id: str
    chunk_id: int
    chunk_text: Optional[str] = None  # Optional: provide to avoid database load


class RegenerateAIFieldRequest(BaseModel):
    video_id: Optional[str] = None
    chunk_id: Optional[int] = None
    book_id: Optional[str] = None
    chapter_id: Optional[int] = None
    field_name: str  # 'title', 'field_1', 'field_2', or 'field_3' (books don't have 'title')
    chapter_text: Optional[str] = None  # Optional chapter text to avoid storage download
    chunk_text: Optional[str] = None  # Optional chunk text to avoid storage download (for videos)


class VerifyEmailRequest(BaseModel):
    email: str


class VerifyEmailResponse(BaseModel):
    is_verified: bool
    message: str


# Utility Functions for JSON Cleaning
def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string by removing trailing commas, fixing formatting issues
    
    Args:
        json_str: Raw JSON string that may have formatting issues
        
    Returns:
        Cleaned JSON string that's valid JSON
    """
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Remove comments (both // and /* */ style)
    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # Normalize whitespace (but keep it for readability)
    # This is optional but helps with very malformed JSON
    lines = json_str.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    json_str = '\n'.join(cleaned_lines)
    
    return json_str


def normalize_chapter_data(chapters_raw: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Normalize chapter data to expected format, handling various field name variations
    
    Args:
        chapters_raw: Raw chapter data with potentially inconsistent field names
        
    Returns:
        Normalized list of chapters with 'title' and 'content' fields
    """
    normalized = []
    
    for idx, chapter in enumerate(chapters_raw):
        # Handle different field name variations
        title = (
            chapter.get('title') or 
            chapter.get('chapter_title') or 
            chapter.get('name') or 
            chapter.get('heading') or
            f"Chapter {idx + 1}"
        )
        
        content = (
            chapter.get('content') or 
            chapter.get('chapter_text') or 
            chapter.get('text') or 
            chapter.get('body') or
            ""
        )
        
        # Only include chapters with actual content
        if content:
            normalized.append({
                'title': str(title).strip(),
                'content': str(content).strip()
            })
    
    return normalized


# Routes
@app.get("/")
async def root():
    return {"message": "YouTube Notes API", "version": "2.0.0"}


@app.post("/api/auth/verify-email", response_model=VerifyEmailResponse)
async def verify_email(request: VerifyEmailRequest):
    is_verified = is_email_verified(request.email)
    return VerifyEmailResponse(
        is_verified=is_verified,
        message="Email is verified" if is_verified else "Email not authorized"
    )


@app.post("/api/video", response_model=VideoResponse)
async def get_video(request: VideoRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Check database first
        from youtube import extract_video_id
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL")
        
        video = get_video_by_id(video_id)
        
        if not video:
            # Fetch via orchestrator
            metadata = process_video_metadata(request.video_url)
            
            if not metadata:
                raise HTTPException(status_code=404, detail="Video not found")
            
            video = get_video_by_id(video_id)
        
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/{video_id}", response_model=VideoResponse)
async def get_video_by_id_endpoint(video_id: str, current_user: dict = Depends(get_current_user)):
    """Get video metadata by video ID from database"""
    try:
        video = get_video_by_id(video_id)
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found in database")
        
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/note/{video_id}")
async def get_note(video_id: str, current_user: dict = Depends(get_current_user)):
    try:
        note = get_note_by_video_id(video_id)
        return note if note else {"video_id": video_id, "note_content": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/note")
async def save_note(request: NoteRequest, current_user: dict = Depends(get_current_user)):
    try:
        note = create_or_update_note(
            video_id=request.video_id,
            note_content=request.note_content,
            custom_tags=request.custom_tags
        )
        
        if not note:
            raise HTTPException(status_code=500, detail="Failed to save note")
        
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes")
async def get_notes(limit: int = 50, current_user: dict = Depends(get_current_user)):
    try:
        notes = get_notes_with_video_info(limit=limit)
        return {"notes": notes, "count": len(notes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/creator-notes")
async def get_creator_notes(
    channel: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    try:
        all_notes = get_notes_with_video_info(limit=1000)
        
        filtered_notes = [
            note for note in all_notes
            if note.get('channel_title') and 
            channel.lower() in note['channel_title'].lower()
        ]
        
        return {
            "notes": filtered_notes[:limit],
            "count": len(filtered_notes[:limit]),
            "channel": channel
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos")
async def get_videos(limit: int = 100, current_user: dict = Depends(get_current_user)):
    try:
        videos = get_all_videos(limit=limit)
        return {"videos": videos or [], "count": len(videos) if videos else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks/{video_id}")
async def get_video_chunks(video_id: str, include_text: bool = False, current_user: dict = Depends(get_current_user)):
    """
    Get all chunks for a video
    
    Args:
        video_id: YouTube video ID
        include_text: If True, load chunk text from storage (default: False for performance)
    """
    try:
        chunks = get_chunks_by_video(video_id)
        
        # Load chunk text if requested
        if include_text and chunks:
            chunks = load_chunks_text(chunks)
        
        return {"video_id": video_id, "chunks": chunks, "count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks/{video_id}/index")
async def get_video_chunk_index(video_id: str, current_user: dict = Depends(get_current_user)):
    try:
        index = get_chunk_index(video_id)
        return {"video_id": video_id, "index": index, "count": len(index)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks/{video_id}/ai-status")
async def get_chunk_ai_status(video_id: str, chunk_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    """
    Lightweight endpoint to check AI enrichment status
    Returns only minimal data for polling checks
    
    Args:
        video_id: YouTube video ID
        chunk_id: Optional specific chunk to check (if None, checks all chunks)
    
    Returns:
        For single chunk: {chunk_id, short_title, ai_field_1} (~50-100 bytes)
        For all chunks: {chunks: [{chunk_id, short_title, ai_field_1}]} (~50-100 bytes per chunk)
    """
    try:
        from db.subtitle_chunks_crud import get_chunks_by_video
        chunks = get_chunks_by_video(video_id)
        
        if chunk_id is not None:
            # Single chunk check
            chunk = next((c for c in chunks if c.get('chunk_id') == chunk_id), None)
            if not chunk:
                raise HTTPException(status_code=404, detail="Chunk not found")
            return {
                "chunk_id": chunk.get('chunk_id'),
                "short_title": chunk.get('short_title', ''),
                "ai_field_1": chunk.get('ai_field_1', '')
            }
        else:
            # All chunks check - return minimal data
            minimal_chunks = [
                {
                    "chunk_id": c.get('chunk_id'),
                    "short_title": c.get('short_title', ''),
                    "ai_field_1": c.get('ai_field_1', '')
                }
                for c in chunks
            ]
            return {"video_id": video_id, "chunks": minimal_chunks, "count": len(minimal_chunks)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks/{video_id}/{chunk_id}")
async def get_chunk(video_id: str, chunk_id: int, include_text: bool = True, current_user: dict = Depends(get_current_user)):
    """
    Get a specific chunk
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        include_text: If True, load chunk text from storage (default: True)
    """
    try:
        chunk = get_chunk_details(video_id, chunk_id, include_text=include_text)
        
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        return chunk
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ChunkNoteRequest(BaseModel):
    note_content: str


@app.put("/api/chunks/{video_id}/{chunk_id}/note")
async def update_chunk_note_endpoint(
    video_id: str, 
    chunk_id: int, 
    request: ChunkNoteRequest, 
    current_user: dict = Depends(get_current_user)
):
    """
    Update the markdown note content for a specific chunk
    
    Args:
        video_id: YouTube video ID
        chunk_id: Chunk identifier
        request: ChunkNoteRequest with note_content
    """
    try:
        updated_chunk = update_chunk_note(video_id, chunk_id, request.note_content)
        
        if not updated_chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        return updated_chunk
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/process-video")
async def process_video_endpoint(request: VideoRequest, current_user: dict = Depends(get_current_user)):
    """Process video: subtitles + chunking + AI enrichment (background)"""
    try:
        from youtube import extract_video_id
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL")
        
        # Ensure video metadata exists
        video = get_video_by_id(video_id)
        if not video:
            metadata = process_video_metadata(request.video_url)
            if not metadata:
                raise HTTPException(status_code=404, detail="Video not found")
        
        # Process in background
        def background_task():
            import sys
            # Force unbuffered output (try line buffering first, fall back to full unbuffering)
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass  # reconfigure might not work on all systems
            try:
                process_full_video(video_id)
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": "Video processing started",
            "video_id": video_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/process-subtitles")
async def process_subtitles_endpoint(request: VideoRequest, current_user: dict = Depends(get_current_user)):
    """Process subtitles only: download and chunk (background)"""
    try:
        from youtube import extract_video_id
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL")
        
        # Ensure video metadata exists
        video = get_video_by_id(video_id)
        if not video:
            metadata = process_video_metadata(request.video_url)
            if not metadata:
                raise HTTPException(status_code=404, detail="Video not found")
        
        # Store result in a shared dict
        result_holder = {"result": None}
        
        # Process in background
        def background_task():
            import sys
            # Force unbuffered output (try line buffering first, fall back to full unbuffering)
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass  # reconfigure might not work on all systems
            try:
                result = process_video_subtitles_only(video_id)
                result_holder["result"] = result
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
                result_holder["result"] = {"success": False, "chunk_count": 0, "error": str(e)}
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": "Subtitle processing started",
            "video_id": video_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/process-ai-enrichment")
async def process_ai_enrichment_endpoint(request: VideoRequest, current_user: dict = Depends(get_current_user)):
    """Process AI enrichment only: enrich existing chunks (background)"""
    try:
        from youtube import extract_video_id
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL")
        
        # Check if chunks exist
        chunks = get_chunks_by_video(video_id)
        if not chunks:
            raise HTTPException(status_code=400, detail="No subtitle chunks found. Please process subtitles first.")
        
        # Process in background
        def background_task():
            import sys
            # Force unbuffered output (try line buffering first, fall back to full unbuffering)
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass  # reconfigure might not work on all systems
            try:
                process_ai_enrichment_only(video_id)
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": "AI enrichment started",
            "video_id": video_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/process-video-chunk-ai")
async def process_video_chunk_ai_endpoint(
    request: VideoChunkAIRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process AI enrichment for a single video chunk (background)"""
    try:
        # If chunk_text not provided, verify chunk exists (metadata only, no storage load)
        if not request.chunk_text:
            from db.subtitle_chunks_crud import get_chunk_metadata
            chunk = get_chunk_metadata(request.video_id, request.chunk_id)
            if not chunk:
                raise HTTPException(status_code=404, detail="Chunk not found")
        
        # Process in background
        def background_task():
            import sys
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass
            try:
                process_video_chunk_ai_enrichment(
                    request.video_id,
                    request.chunk_id,
                    request.chunk_text
                )
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": "Chunk AI enrichment started",
            "video_id": request.video_id,
            "chunk_id": request.chunk_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/process-video-all-chunks-ai")
async def process_video_all_chunks_ai_endpoint(
    request: VideoAIRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process AI enrichment for all chunks of a video (background)"""
    try:
        # Verify video exists
        video = get_video_by_id(request.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Check if video has chunks
        from db.subtitle_chunks_crud import get_chunks_by_video
        chunks = get_chunks_by_video(request.video_id)
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks found for this video")
        
        # Process in background
        def background_task():
            import sys
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass
            try:
                process_video_all_chunks_ai_enrichment(request.video_id)
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": f"AI enrichment started for {len(chunks)} chunks",
            "video_id": request.video_id,
            "chunk_count": len(chunks),
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chunks/{video_id}/{chunk_id}/regenerate-ai-field")
async def regenerate_ai_field_endpoint(
    video_id: str,
    chunk_id: int,
    request: RegenerateAIFieldRequest,
    current_user: dict = Depends(get_current_user)
):
    """Regenerate a single AI field for a video chunk"""
    try:
        from orchestrator import regenerate_video_chunk_ai_field
        
        # Validate field_name
        valid_fields = ['title', 'field_1', 'field_2', 'field_3']
        if request.field_name not in valid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid field_name. Must be one of: {', '.join(valid_fields)}"
            )
        
        result = regenerate_video_chunk_ai_field(
            video_id=video_id,
            chunk_id=chunk_id,
            field_name=request.field_name,
            chunk_text=request.chunk_text
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/chunks/{video_id}/{chunk_id}/update-ai-field")
async def update_ai_field_endpoint(
    video_id: str,
    chunk_id: int,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Manually update a single AI field for a video chunk"""
    try:
        from db.subtitle_chunks_crud import update_chunk_ai_fields
        
        field_name = request.get('field_name')
        field_value = request.get('field_value')
        
        # Validate field_name
        valid_fields = ['title', 'field_1', 'field_2', 'field_3']
        if field_name not in valid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid field_name. Must be one of: {', '.join(valid_fields)}"
            )
        
        if field_value is None:
            raise HTTPException(status_code=400, detail="field_value is required")
        
        # Map field names to update_chunk_ai_fields parameters
        kwargs = {
            'video_id': video_id,
            'chunk_id': chunk_id
        }
        
        if field_name == 'title':
            kwargs['short_title'] = field_value
        elif field_name == 'field_1':
            kwargs['ai_field_1'] = field_value
        elif field_name == 'field_2':
            kwargs['ai_field_2'] = field_value
        elif field_name == 'field_3':
            kwargs['ai_field_3'] = field_value
        
        result = update_chunk_ai_fields(**kwargs)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update AI field")
        
        return {
            'success': True,
            'field_name': field_name,
            'updated_chunk': result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/chunks/{video_id}/{chunk_id}/text")
async def update_chunk_text_endpoint(
    video_id: str,
    chunk_id: int,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update chunk text content for a video chunk"""
    try:
        chunk_text = request.get("chunk_text")
        if chunk_text is None:
            raise HTTPException(status_code=400, detail="chunk_text is required")
        
        updated_chunk = update_chunk_text(video_id, chunk_id, chunk_text)
        if not updated_chunk:
            raise HTTPException(status_code=500, detail="Failed to update chunk text")
        
        return updated_chunk
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test/process-video-no-auth")
async def process_video_no_auth(request: VideoRequest):
    """TEST: Process video without auth"""
    try:
        from youtube import extract_video_id
        video_id = extract_video_id(request.video_url)
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid video URL")
        
        video = get_video_by_id(video_id)
        if not video:
            metadata = process_video_metadata(request.video_url)
            if not metadata:
                raise HTTPException(status_code=404, detail="Video not found")
        
        def background_task():
            import sys
            # Force unbuffered output (try line buffering first, fall back to full unbuffering)
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass  # reconfigure might not work on all systems
            try:
                process_full_video(video_id)
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": "Video processing started (TEST)",
            "video_id": video_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test/chunks/{video_id}/index")
async def get_video_chunk_index_no_auth(video_id: str):
    """TEST: Get chunk index without auth"""
    try:
        index = get_chunk_index(video_id)
        return {"video_id": video_id, "index": index, "count": len(index)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# BOOK ENDPOINTS
# ============================================================

@app.post("/api/book")
async def create_book_endpoint(request: BookRequest, current_user: dict = Depends(get_current_user)):
    """Create a new book with chapters from uploaded JSON"""
    try:
        # Normalize chapter data (handle different field names, extra fields, etc.)
        normalized_chapters = normalize_chapter_data(request.chapters)
        
        if not normalized_chapters:
            raise HTTPException(
                status_code=400, 
                detail="No valid chapters found. Each chapter must have content (or chapter_text/text field)."
            )
        
        # Validate chapters have required fields after normalization
        missing_fields = []
        for idx, chapter_data in enumerate(normalized_chapters):
            chapter_num = idx + 1
            if not chapter_data.get('title'):
                missing_fields.append(f"Chapter {chapter_num}: missing or empty 'title'")
            if not chapter_data.get('content'):
                missing_fields.append(f"Chapter {chapter_num}: missing or empty 'content'")
        
        if missing_fields:
            error_msg = "Invalid chapters - " + "; ".join(missing_fields)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create book metadata
        book = create_book(
            book_id=request.book_id,
            title=request.title,
            author=request.author,
            publisher=request.publisher,
            publication_year=request.publication_year,
            isbn=request.isbn,
            description=request.description,
            tags=request.tags,
            book_type=request.book_type
        )
        
        if not book:
            raise HTTPException(status_code=500, detail="Failed to create book")
        
        # Create chapters (1-indexed: starting from 1)
        chapter_count = 0
        for idx, chapter_data in enumerate(normalized_chapters):
            chapter = create_chapter(
                book_id=request.book_id,
                chapter_id=idx + 1,  # 1-indexed
                chapter_title=chapter_data['title'],
                chapter_text=chapter_data['content']
            )
            if chapter:
                chapter_count += 1
        
        return {
            "book_id": request.book_id,
            "title": request.title,
            "author": request.author,
            "chapter_count": chapter_count,
            "message": f"Book created successfully with {chapter_count} chapters"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Provide more detailed error message
        error_detail = str(e)
        if "json" in error_detail.lower() or "parse" in error_detail.lower():
            error_detail = f"JSON parsing error: {error_detail}. Please check your JSON format."
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/book/{book_id}")
async def get_book_endpoint(book_id: str, current_user: dict = Depends(get_current_user)):
    """Get book metadata by ID"""
    try:
        book = get_book_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/books")
async def get_books_endpoint(current_user: dict = Depends(get_current_user)):
    """Get all books"""
    try:
        books = get_all_books()
        return {"books": books, "count": len(books)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/book/{book_id}/chapters")
async def get_book_chapters_endpoint(book_id: str, current_user: dict = Depends(get_current_user)):
    """Get all chapters for a book (without text)"""
    try:
        chapters = get_chapters_by_book(book_id)
        return {"book_id": book_id, "chapters": chapters, "count": len(chapters)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/book/{book_id}/chapters/index")
async def get_book_chapter_index_endpoint(book_id: str, current_user: dict = Depends(get_current_user)):
    """Get chapter index (lightweight) for navigation"""
    try:
        index = get_chapter_index(book_id)
        return {"book_id": book_id, "index": index, "count": len(index)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/book/{book_id}/chapters/ai-status")
async def get_chapter_ai_status(book_id: str, chapter_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    """
    Lightweight endpoint to check AI enrichment status for chapters
    Returns only minimal data for polling checks
    
    Args:
        book_id: Book identifier
        chapter_id: Optional specific chapter to check (if None, checks all chapters)
    
    Returns:
        For single chapter: {chapter_id, chapter_title, ai_field_1} (~50-100 bytes)
        For all chapters: {chapters: [{chapter_id, chapter_title, ai_field_1}]} (~50-100 bytes per chapter)
    """
    try:
        from db.book_chapters_crud import get_chapters_by_book
        chapters = get_chapters_by_book(book_id)
        
        if chapter_id is not None:
            # Single chapter check
            chapter = next((c for c in chapters if c.get('chapter_id') == chapter_id), None)
            if not chapter:
                raise HTTPException(status_code=404, detail="Chapter not found")
            return {
                "chapter_id": chapter.get('chapter_id'),
                "chapter_title": chapter.get('chapter_title', ''),
                "ai_field_1": chapter.get('ai_field_1', '')
            }
        else:
            # All chapters check - return minimal data
            minimal_chapters = [
                {
                    "chapter_id": c.get('chapter_id'),
                    "chapter_title": c.get('chapter_title', ''),
                    "ai_field_1": c.get('ai_field_1', '')
                }
                for c in chapters
            ]
            return {"book_id": book_id, "chapters": minimal_chapters, "count": len(minimal_chapters)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/book/{book_id}/chapter/{chapter_id}")
async def get_chapter_endpoint(book_id: str, chapter_id: int, include_text: bool = True, current_user: dict = Depends(get_current_user)):
    """Get chapter details with optional text loading"""
    try:
        chapter = get_chapter_details(book_id, chapter_id, include_text=include_text)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        return chapter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/book/{book_id}/chapter/{chapter_id}/note")
async def update_chapter_note_endpoint(
    book_id: str,
    chapter_id: int,
    request: ChapterNoteRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update note for a specific chapter"""
    try:
        result = update_chapter_note(book_id, chapter_id, request.note_content)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update chapter note")
        return {"message": "Chapter note updated", "book_id": book_id, "chapter_id": chapter_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/book/note")
async def create_or_update_book_note_endpoint(request: BookNoteRequest, current_user: dict = Depends(get_current_user)):
    """Create or update overall note for a book"""
    try:
        result = create_or_update_book_note(
            book_id=request.book_id,
            note_content=request.note_content,
            custom_tags=request.custom_tags
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to save book note")
        return {"message": "Book note saved", "book_id": request.book_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/book/{book_id}/note")
async def get_book_note_endpoint(book_id: str, current_user: dict = Depends(get_current_user)):
    """Get note for a book"""
    try:
        note = get_note_by_book_id(book_id)
        if not note:
            # Return empty note if not found
            return {"book_id": book_id, "note_content": None}
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/book/notes/all")
async def get_all_book_notes_endpoint(current_user: dict = Depends(get_current_user)):
    """Get all book notes with book info"""
    try:
        notes = get_notes_with_book_info()
        return {"notes": notes, "count": len(notes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/book/{book_id}/chapter/{chapter_id}/text")
async def update_chapter_text_endpoint(
    book_id: str,
    chapter_id: int,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update chapter text content"""
    try:
        chapter_text = request.get("chapter_text")
        if chapter_text is None:
            raise HTTPException(status_code=400, detail="chapter_text is required")
        
        updated_chapter = update_chapter_text(book_id, chapter_id, chapter_text)
        if not updated_chapter:
            raise HTTPException(status_code=500, detail="Failed to update chapter text")
        
        return updated_chapter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/book/{book_id}/chapter/{chapter_id}")
async def delete_chapter_endpoint(
    book_id: str,
    chapter_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a chapter"""
    try:
        success = delete_chapter(book_id, chapter_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete chapter")
        
        return {"success": True, "message": f"Chapter {chapter_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/book/{book_id}/chapters/reorder")
async def reorder_chapters_endpoint(
    book_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Reorder chapters for a book"""
    try:
        chapter_order = request.get("chapter_order")
        if not chapter_order or not isinstance(chapter_order, list):
            raise HTTPException(status_code=400, detail="chapter_order array is required")
        
        success = reorder_chapters(book_id, chapter_order)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reorder chapters")
        
        return {"success": True, "message": "Chapters reordered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/process-book-chapter-ai")
async def process_book_chapter_ai_endpoint(
    request: BookChapterAIRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process AI enrichment for a single book chapter (background)"""
    try:
        # If chapter_text not provided, verify chapter exists (metadata only, no storage load)
        if not request.chapter_text:
            from db.book_chapters_crud import get_chapter_metadata
            chapter = get_chapter_metadata(request.book_id, request.chapter_id)
            if not chapter:
                raise HTTPException(status_code=404, detail="Chapter not found")
        
        # Process in background
        def background_task():
            import sys
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass
            try:
                process_book_chapter_ai_enrichment(
                    request.book_id,
                    request.chapter_id,
                    request.chapter_text
                )
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": "Chapter AI enrichment started",
            "book_id": request.book_id,
            "chapter_id": request.chapter_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/book/{book_id}/chapter/{chapter_id}/regenerate-ai-field")
async def regenerate_book_chapter_ai_field_endpoint(
    book_id: str,
    chapter_id: int,
    request: RegenerateAIFieldRequest,
    current_user: dict = Depends(get_current_user)
):
    """Regenerate a single AI field for a book chapter"""
    try:
        from orchestrator import regenerate_book_chapter_ai_field
        
        # Validate field_name (books don't have 'title')
        valid_fields = ['field_1', 'field_2', 'field_3']
        if request.field_name not in valid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid field_name. Must be one of: {', '.join(valid_fields)}"
            )
        
        result = regenerate_book_chapter_ai_field(
            book_id=book_id,
            chapter_id=chapter_id,
            field_name=request.field_name,
            chapter_text=request.chapter_text
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/book/{book_id}/chapter/{chapter_id}/update-ai-field")
async def update_book_chapter_ai_field_endpoint(
    book_id: str,
    chapter_id: int,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Manually update a single AI field for a book chapter"""
    try:
        from db.book_chapters_crud import update_chapter_ai_fields
        
        field_name = request.get('field_name')
        field_value = request.get('field_value')
        
        # Validate field_name (books don't have 'title')
        valid_fields = ['field_1', 'field_2', 'field_3']
        if field_name not in valid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid field_name. Must be one of: {', '.join(valid_fields)}"
            )
        
        if field_value is None:
            raise HTTPException(status_code=400, detail="field_value is required")
        
        # Map field names to update_chapter_ai_fields parameters
        kwargs = {
            'book_id': book_id,
            'chapter_id': chapter_id
        }
        
        if field_name == 'field_1':
            kwargs['ai_field_1'] = field_value
        elif field_name == 'field_2':
            kwargs['ai_field_2'] = field_value
        elif field_name == 'field_3':
            kwargs['ai_field_3'] = field_value
        
        result = update_chapter_ai_fields(**kwargs)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update AI field")
        
        return {
            'success': True,
            'field_name': field_name,
            'updated_chapter': result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/process-book-all-chapters-ai")
async def process_book_all_chapters_ai_endpoint(
    request: BookAIRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process AI enrichment for all chapters of a book (background)"""
    try:
        # Verify book exists
        from db.books_crud import get_book_by_id
        book = get_book_by_id(request.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Check if book has chapters
        from db.book_chapters_crud import get_chapters_by_book
        chapters = get_chapters_by_book(request.book_id)
        if not chapters:
            raise HTTPException(status_code=400, detail="No chapters found for this book")
        
        # Process in background
        def background_task():
            import sys
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except:
                pass
            try:
                process_book_all_chapters_ai_enrichment(request.book_id)
            except Exception as e:
                print(f"Background error: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return {
            "message": f"AI enrichment started for {len(chapters)} chapters",
            "book_id": request.book_id,
            "chapter_count": len(chapters),
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prompts")
async def get_prompts(content_type: str = 'video', current_user: dict = Depends(get_current_user)):
    """Get prompt configurations
    
    Args:
        content_type: 'video', 'book', 'lecture', or other to determine which prompt set to return
    """
    try:
        if content_type not in ['video', 'book', 'lecture']:
            raise HTTPException(status_code=400, detail="content_type must be 'video', 'book', or 'lecture'")
        
        prompts_dict = get_all_prompts(content_type=content_type)
        prompts_list = [
            {
                'field_name': key,
                'label': get_prompt_label(key, content_type=content_type),
                'template': prompts_dict[key]
            }
            for key in prompts_dict
        ]
        return {"prompts": prompts_list, "count": len(prompts_list), "content_type": content_type}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/video/{video_id}")
async def delete_video_endpoint(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a video and its associated chunks
    
    Args:
        video_id: YouTube video ID
        current_user: Authenticated user (required)
        
    Returns:
        Success message
        
    Note:
        - Deletes storage files first, then DB record
        - Cascades to subtitle_chunks
        - Does NOT delete video_notes (preserved as orphaned records)
    """
    try:
        success = delete_video(video_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
        return {"message": f"Video {video_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/book/{book_id}")
async def delete_book_endpoint(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a book and its associated chapters
    
    Args:
        book_id: Book identifier
        current_user: Authenticated user (required)
        
    Returns:
        Success message
        
    Note:
        - Deletes storage files first, then DB record
        - Cascades to book_chapters
        - Does NOT delete book_notes (preserved as orphaned records)
    """
    try:
        success = delete_book(book_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
        return {"message": f"Book {book_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
