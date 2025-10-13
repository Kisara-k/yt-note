"""
FastAPI backend for YouTube Notes
Uses orchestrator for all module coordination
"""

import os
import sys
import threading
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
    process_ai_enrichment_only
)

# Import from auth and db directly
from auth import get_current_user, is_email_verified
from prompts import get_all_prompts, get_prompt_label
from db.youtube_crud import get_video_by_id, get_all_videos
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
    update_chunk_note
)
from db.books_crud import (
    create_book,
    get_book_by_id,
    get_all_books
)
from db.book_chapters_crud import (
    create_chapter,
    get_chapters_by_book,
    get_chapter_index,
    get_chapter_details,
    update_chapter_note
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
    chapters: List[Dict[str, str]]  # List of {chapter_title, chapter_text}


class BookNoteRequest(BaseModel):
    book_id: str
    note_content: str
    custom_tags: Optional[List[str]] = None


class ChapterNoteRequest(BaseModel):
    book_id: str
    chapter_id: int
    note_content: str


class VerifyEmailRequest(BaseModel):
    email: str


class VerifyEmailResponse(BaseModel):
    is_verified: bool
    message: str


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
        # Create book metadata
        book = create_book(
            book_id=request.book_id,
            title=request.title,
            author=request.author,
            publisher=request.publisher,
            publication_year=request.publication_year,
            isbn=request.isbn,
            description=request.description,
            tags=request.tags
        )
        
        if not book:
            raise HTTPException(status_code=500, detail="Failed to create book")
        
        # Create chapters
        chapter_count = 0
        for idx, chapter_data in enumerate(request.chapters):
            chapter = create_chapter(
                book_id=request.book_id,
                chapter_id=idx,
                chapter_title=chapter_data.get('chapter_title', f'Chapter {idx + 1}'),
                chapter_text=chapter_data.get('chapter_text', '')
            )
            if chapter:
                chapter_count += 1
        
        return {
            "book_id": request.book_id,
            "title": request.title,
            "author": request.author,
            "chapter_count": chapter_count,
            "message": "Book created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/api/book/{book_id}/chapter/{chapter_id}")
async def get_chapter_endpoint(book_id: str, chapter_id: int, current_user: dict = Depends(get_current_user)):
    """Get chapter details with text"""
    try:
        chapter = get_chapter_details(book_id, chapter_id)
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


@app.get("/api/prompts")
async def get_prompts(current_user: dict = Depends(get_current_user)):
    """Get prompt configurations"""
    try:
        prompts_dict = get_all_prompts()
        prompts_list = [
            {
                'field_name': key,
                'label': get_prompt_label(key),
                'template': prompts_dict[key]
            }
            for key in prompts_dict
        ]
        return {"prompts": prompts_list, "count": len(prompts_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
