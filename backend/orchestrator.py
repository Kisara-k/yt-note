"""
Orchestrator - Coordinates between modules
Handles all inter-module communication and threading
"""

import os
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

# Import from config
from config import (
    CHUNK_TARGET_WORDS, CHUNK_MAX_WORDS, CHUNK_OVERLAP_WORDS, CHUNK_MIN_FINAL_WORDS,
    OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS_TITLE, OPENAI_MAX_TOKENS_OTHER
)
from prompts import get_all_prompts

# Import module functions (no cross-module imports)
from youtube import extract_video_id, fetch_video_metadata, fetch_batch_metadata
from subtitles import extract_and_chunk_subtitles
from openai_api.enrichment import enrich_chunk, enrich_chunks_parallel

# Import from db
from db.youtube_crud import create_or_update_video, get_video_by_id, bulk_create_or_update_videos
from db.subtitle_chunks_crud import create_chunk, get_chunks_by_video, delete_chunks_by_video, update_chunk_ai_fields, bulk_create_chunks, bulk_update_ai_fields
from db.video_notes_crud import create_or_update_note, get_note_by_video_id
from db.book_chapters_crud import get_chapters_by_book, load_chapters_text, update_chapter_ai_fields
from db.books_crud import get_book_by_id


def process_video_metadata(video_url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch and save video metadata
    Returns: video metadata dict
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        return None
    
    metadata = fetch_video_metadata(video_id)
    if not metadata:
        return None
    
    # Convert to YouTube API format for create_or_update_video
    video_data = {
        'id': metadata['video_id'],
        'snippet': {
            'title': metadata['title'],
            'channelTitle': metadata['channel_title'],
            'channelId': metadata['channel_id'],
            'publishedAt': metadata.get('published_at'),
            'description': metadata.get('description'),
        },
        'contentDetails': {
            'duration': metadata.get('duration'),
        },
        'statistics': {
            'viewCount': str(metadata.get('view_count', 0)),
            'likeCount': str(metadata.get('like_count', 0)),
        }
    }
    
    # Save to database
    create_or_update_video(video_data)
    
    return metadata


def process_batch_metadata(video_urls: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch and save metadata for multiple videos (up to 50)
    Returns: list of video metadata dicts
    """
    video_ids = [extract_video_id(url) for url in video_urls]
    video_ids = [vid for vid in video_ids if vid]
    
    if not video_ids:
        return []
    
    metadata_list = fetch_batch_metadata(video_ids)
    
    if metadata_list:
        bulk_create_or_update_videos(metadata_list)
    
    return metadata_list


def process_video_subtitles(video_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Extract and chunk subtitles for a video
    Returns: list of chunks with text, word_count, sentence_count
    """
    chunks = extract_and_chunk_subtitles(
        video_id=video_id,
        target_words=CHUNK_TARGET_WORDS,
        max_words=CHUNK_MAX_WORDS,
        overlap_words=CHUNK_OVERLAP_WORDS,
        min_final_words=CHUNK_MIN_FINAL_WORDS
    )
    
    return chunks


def process_chunk_enrichment(chunk_text: str) -> Dict[str, str]:
    """
    Enrich a single chunk with AI (for videos)
    Returns: dict with title, field_1, field_2, field_3
    """
    prompts = get_all_prompts(content_type='video')
    
    result = enrich_chunk(
        text=chunk_text,
        prompts=prompts,
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
        max_tokens_other=OPENAI_MAX_TOKENS_OTHER
    )
    
    return result


def process_chunks_enrichment_parallel(chunks: List[Dict[str, Any]], content_type: str = 'video') -> List[Dict[str, Any]]:
    """
    Enrich multiple chunks in parallel
    
    Args:
        chunks: List of chunks to enrich
        content_type: Either 'video' or 'book' to determine which prompts to use
    
    Returns: list of enriched chunks
    """
    prompts = get_all_prompts(content_type=content_type)
    
    enriched = enrich_chunks_parallel(
        chunks=chunks,
        prompts=prompts,
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
        max_tokens_other=OPENAI_MAX_TOKENS_OTHER,
        max_workers=5
    )
    
    return enriched


def process_video_subtitles_only(video_id: str) -> Dict[str, Any]:
    """
    Extract and save subtitles for a video (without AI enrichment)
    Deletes existing chunks before processing
    
    Returns: Dict with success status and chunk count
    """
    import sys
    
    print(f"\n{'='*70}", flush=True)
    print(f"Processing subtitles for video: {video_id}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    try:
        # Step 1: Delete existing chunks
        print("[1/3] Deleting existing chunks...", flush=True)
        delete_chunks_by_video(video_id)
        print("Existing chunks deleted\n", flush=True)
        
        # Step 2: Extract subtitles
        print("[2/3] Extracting and chunking subtitles...", flush=True)
        chunks = process_video_subtitles(video_id)
        
        if not chunks:
            print("No subtitles available", flush=True)
            return {"success": False, "chunk_count": 0, "error": "No subtitles available"}
        
        print(f"Created {len(chunks)} chunks\n", flush=True)
        
        # Step 3: Save to database in ONE BULK OPERATION (not a loop)
        print("[3/3] Saving all chunks to database (bulk operation)...", flush=True)
        
        # Prepare chunks for bulk insert (1-indexed)
        chunks_for_db = [
            {
                'video_id': video_id,
                'chunk_id': i + 1,  # 1-indexed: starts from 1
                'chunk_text': chunk['text'],
                'short_title': None,
                'ai_field_1': None,
                'ai_field_2': None,
                'ai_field_3': None
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Single database transaction for all chunks
        result = bulk_create_chunks(chunks_for_db)
        
        if not result:
            print("Failed to save chunks to database", flush=True)
            return {"success": False, "chunk_count": 0, "error": "Database save failed"}
        
        print(f"Saved {len(chunks)} chunks in single transaction", flush=True)
        print(f"\n{'='*70}", flush=True)
        print("Subtitle processing complete!", flush=True)
        print(f"{'='*70}\n", flush=True)
        
        return {"success": True, "chunk_count": len(chunks)}
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {"success": False, "chunk_count": 0, "error": str(e)}


def process_ai_enrichment_only(video_id: str) -> bool:
    """
    Enrich existing subtitle chunks with AI
    Only processes chunks that don't have AI fields yet
    
    Returns: True if successful
    """
    import sys
    
    print(f"\n{'='*70}", flush=True)
    print(f"AI Enrichment for video: {video_id}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    try:
        # Step 1: Get chunks from database
        print("[1/3] Loading chunks from database...", flush=True)
        chunks = get_chunks_by_video(video_id)
        
        if not chunks:
            print("No chunks found. Please process subtitles first.", flush=True)
            return False
        
        print(f"Found {len(chunks)} chunks\n", flush=True)
        
        # Load chunk text from storage for all chunks
        print("[1.5/3] Loading chunk text from storage...", flush=True)
        from db.subtitle_chunks_crud import load_chunks_text
        chunks = load_chunks_text(chunks)
        print(f"Loaded text for {len(chunks)} chunks\n", flush=True)
        
        # Step 2: Enrich with AI (parallel)
        print("[2/3] Enriching chunks with AI (parallel)...", flush=True)
        
        # Convert DB chunks to format expected by enrichment
        chunks_for_enrichment = [
            {
                'text': chunk['chunk_text'],
                'word_count': len(chunk['chunk_text'].split()),
                'sentence_count': chunk['chunk_text'].count('.') + chunk['chunk_text'].count('!') + chunk['chunk_text'].count('?')
            }
            for chunk in chunks
        ]
        
        enriched_chunks = process_chunks_enrichment_parallel(chunks_for_enrichment)
        print(f"Enriched {len(enriched_chunks)} chunks\n", flush=True)
        
        # Step 3: Update database with AI fields (targeted updates)
        # Note: Uses UPDATE loop instead of bulk upsert because chunk_text is 5-10x larger than AI fields
        # Sending only AI fields in N updates is more efficient than fetching + re-uploading chunk_text
        print("[3/3] Updating database with AI fields (targeted updates)...", flush=True)
        
        # Prepare enriched data with chunk_ids for bulk update (1-indexed)
        enriched_with_ids = [
            {
                'chunk_id': i + 1,  # 1-indexed: starts from 1
                'title': enriched.get('title', ''),
                'field_1': enriched.get('field_1', ''),
                'field_2': enriched.get('field_2', ''),
                'field_3': enriched.get('field_3', '')
            }
            for i, enriched in enumerate(enriched_chunks)
        ]
        
        # Single database transaction for all chunk updates
        result = bulk_update_ai_fields(video_id, enriched_with_ids)
        
        if not result:
            print("Failed to update chunks in database", flush=True)
            return False
        
        print(f"Updated {len(enriched_chunks)} chunks with targeted updates", flush=True)
        print(f"\n{'='*70}", flush=True)
        print("AI enrichment complete!", flush=True)
        print(f"{'='*70}\n", flush=True)
        
        return True
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def process_full_video(video_id: str) -> bool:
    """
    Complete video processing pipeline:
    1. Extract and chunk subtitles
    2. Enrich chunks with AI (parallel)
    3. Save to database
    
    Returns: True if successful
    """
    print(f"\n{'='*70}", flush=True)
    print(f"Processing video: {video_id}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    try:
        # Step 1: Process subtitles
        success = process_video_subtitles_only(video_id)
        if not success:
            return False
        
        # Step 2: Enrich with AI
        success = process_ai_enrichment_only(video_id)
        
        return success
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def process_multiple_videos_parallel(video_ids: List[str], max_workers: int = 3) -> Dict[str, bool]:
    """
    Process multiple videos in parallel
    Returns: dict mapping video_id to success status
    """
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_full_video, video_id): video_id 
            for video_id in video_ids
        }
        
        for future in as_completed(futures):
            video_id = futures[future]
            try:
                success = future.result()
                results[video_id] = success
            except Exception as e:
                print(f"Error processing {video_id}: {e}")
                results[video_id] = False
    
    return results


# ==================== BOOK PROCESSING FUNCTIONS ====================

def process_book_chapter_ai_enrichment(book_id: str, chapter_id: int, chapter_text: Optional[str] = None) -> bool:
    """
    Enrich a single book chapter with AI-generated fields
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        chapter_text: Optional chapter text (if not provided, will load from database)
        
    Returns:
        True if successful
    """
    import sys
    
    print(f"\n{'='*70}", flush=True)
    print(f"AI Enrichment for book chapter: {book_id} / Chapter {chapter_id}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    try:
        # Step 1: Get chapter text
        if chapter_text and chapter_text.strip():
            print("[1/3] Using provided chapter text (no database load needed)...", flush=True)
            text_to_enrich = chapter_text
            print(f"Using provided text ({len(text_to_enrich)} characters)\n", flush=True)
        else:
            print("[1/3] Loading chapter from database...", flush=True)
            from db.book_chapters_crud import get_chapter_details
            chapter = get_chapter_details(book_id, chapter_id)
            
            if not chapter:
                print(f"Chapter not found: {book_id} / {chapter_id}", flush=True)
                return False
            
            if not chapter.get('chapter_text'):
                print(f"No chapter text found", flush=True)
                return False
                
            print(f"Found chapter: {chapter.get('chapter_title', 'Untitled')}\n", flush=True)
            text_to_enrich = chapter['chapter_text']
        
        # Step 2: Enrich with AI
        print("[2/3] Enriching chapter with AI...", flush=True)
        
        # Get book prompts
        from prompts import get_all_prompts
        prompts = get_all_prompts(content_type='book')
        
        # Enrich the chapter
        ai_fields = enrich_chunk(
            text=text_to_enrich,
            prompts=prompts,
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
            max_tokens_other=OPENAI_MAX_TOKENS_OTHER
        )
        
        print(f"AI enrichment complete\n", flush=True)
        
        # Step 3: Update database
        print("[3/3] Saving AI fields to database...", flush=True)
        
        updated = update_chapter_ai_fields(
            book_id=book_id,
            chapter_id=chapter_id,
            ai_field_1=ai_fields.get('field_1'),
            ai_field_2=ai_fields.get('field_2'),
            ai_field_3=ai_fields.get('field_3')
        )
        
        if updated:
            print(f"Successfully enriched chapter {chapter_id}", flush=True)
            print(f"\n{'='*70}", flush=True)
            print("Chapter AI enrichment complete!", flush=True)
            print(f"{'='*70}\n", flush=True)
            return True
        else:
            print(f"Failed to update chapter in database", flush=True)
            return False
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def process_book_all_chapters_ai_enrichment(book_id: str) -> bool:
    """
    Enrich all chapters of a book with AI-generated fields (parallel processing)
    
    Args:
        book_id: Book identifier
        
    Returns:
        True if all chapters processed successfully
    """
    import sys
    
    print(f"\n{'='*70}", flush=True)
    print(f"AI Enrichment for all chapters of book: {book_id}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    try:
        # Step 1: Get all chapters from database
        print("[1/4] Loading chapters from database...", flush=True)
        chapters = get_chapters_by_book(book_id)
        
        if not chapters:
            print("No chapters found for this book.", flush=True)
            return False
        
        print(f"Found {len(chapters)} chapters\n", flush=True)
        
        # Step 2: Load chapter text from storage
        print("[2/4] Loading chapter text from storage...", flush=True)
        chapters = load_chapters_text(chapters)
        print(f"Loaded text for {len(chapters)} chapters\n", flush=True)
        
        # Step 3: Enrich all chapters with AI (parallel)
        print("[3/4] Enriching chapters with AI (parallel)...", flush=True)
        
        # Get book prompts
        from prompts import get_all_prompts
        prompts = get_all_prompts(content_type='book')
        
        # Prepare chapters for enrichment
        chapters_for_enrichment = []
        for chapter in chapters:
            if chapter.get('chapter_text'):
                chapters_for_enrichment.append({
                    'text': chapter['chapter_text'],
                    'chapter_id': chapter['chapter_id'],
                    'book_id': chapter['book_id']
                })
        
        if not chapters_for_enrichment:
            print("No chapters with text to enrich", flush=True)
            return False
        
        # Enrich chapters in parallel
        enriched_chapters = enrich_chunks_parallel(
            chunks=chapters_for_enrichment,
            prompts=prompts,
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
            max_tokens_other=OPENAI_MAX_TOKENS_OTHER,
            max_workers=3
        )
        
        print(f"\nAI enrichment complete for {len(enriched_chapters)} chapters", flush=True)
        
        # Step 4: Update all chapters in database
        print("\n[4/4] Saving AI fields to database...", flush=True)
        
        success_count = 0
        for enriched in enriched_chapters:
            updated = update_chapter_ai_fields(
                book_id=enriched['book_id'],
                chapter_id=enriched['chapter_id'],
                ai_field_1=enriched.get('field_1'),
                ai_field_2=enriched.get('field_2'),
                ai_field_3=enriched.get('field_3')
            )
            if updated:
                success_count += 1
        
        print(f"Successfully updated {success_count}/{len(enriched_chapters)} chapters", flush=True)
        print(f"\n{'='*70}", flush=True)
        print("Book AI enrichment complete!", flush=True)
        print(f"{'='*70}\n", flush=True)
        
        return success_count == len(enriched_chapters)
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def process_video_all_chunks_ai_enrichment(video_id: str) -> bool:
    """
    Enrich all chunks of a video with AI-generated fields (parallel processing)
    
    Args:
        video_id: Video identifier
        
    Returns:
        True if all chunks processed successfully
    """
    import sys
    
    print(f"\n{'='*70}", flush=True)
    print(f"AI Enrichment for all chunks of video: {video_id}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    try:
        # Step 1: Get all chunks from database
        print("[1/4] Loading chunks from database...", flush=True)
        from db.subtitle_chunks_crud import get_chunks_by_video, load_chunks_text
        chunks = get_chunks_by_video(video_id)
        
        if not chunks:
            print("No chunks found for this video.", flush=True)
            return False
        
        print(f"Found {len(chunks)} chunks\n", flush=True)
        
        # Step 2: Load chunk text from storage
        print("[2/4] Loading chunk text from storage...", flush=True)
        chunks = load_chunks_text(chunks)
        print(f"Loaded text for {len(chunks)} chunks\n", flush=True)
        
        # Step 3: Enrich all chunks with AI (parallel)
        print("[3/4] Enriching chunks with AI (parallel)...", flush=True)
        
        # Get video prompts
        from prompts import get_all_prompts
        prompts = get_all_prompts(content_type='video')
        
        # Prepare chunks for enrichment
        chunks_for_enrichment = []
        for chunk in chunks:
            if chunk.get('chunk_text'):
                chunks_for_enrichment.append({
                    'text': chunk['chunk_text'],
                    'chunk_id': chunk['chunk_id'],
                    'video_id': chunk['video_id']
                })
        
        if not chunks_for_enrichment:
            print("No chunks with text to enrich", flush=True)
            return False
        
        # Enrich chunks in parallel
        enriched_chunks = enrich_chunks_parallel(
            chunks=chunks_for_enrichment,
            prompts=prompts,
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
            max_tokens_other=OPENAI_MAX_TOKENS_OTHER,
            max_workers=3
        )
        
        print(f"\nAI enrichment complete for {len(enriched_chunks)} chunks", flush=True)
        
        # Step 4: Update all chunks in database
        print("\n[4/4] Saving AI fields to database...", flush=True)
        
        success_count = 0
        for enriched in enriched_chunks:
            updated = update_chunk_ai_fields(
                video_id=enriched['video_id'],
                chunk_id=enriched['chunk_id'],
                short_title=enriched.get('title'),
                ai_field_1=enriched.get('field_1'),
                ai_field_2=enriched.get('field_2'),
                ai_field_3=enriched.get('field_3')
            )
            if updated:
                success_count += 1
        
        print(f"Successfully updated {success_count}/{len(enriched_chunks)} chunks", flush=True)
        print(f"\n{'='*70}", flush=True)
        print("Video AI enrichment complete!", flush=True)
        print(f"{'='*70}\n", flush=True)
        
        return success_count == len(enriched_chunks)
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def process_video_chunk_ai_enrichment(video_id: str, chunk_id: int, chunk_text: Optional[str] = None) -> bool:
    """
    Enrich a single video chunk with AI-generated fields
    
    Args:
        video_id: Video identifier
        chunk_id: Chunk identifier
        chunk_text: Optional chunk text (if not provided, will load from database)
        
    Returns:
        True if successful
    """
    import sys
    
    print(f"\n{'='*70}", flush=True)
    print(f"AI Enrichment for video chunk: {video_id} / Chunk {chunk_id}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    try:
        # Step 1: Get chunk text
        if chunk_text and chunk_text.strip():
            print("[1/3] Using provided chunk text (no database load needed)...", flush=True)
            text_to_enrich = chunk_text
            print(f"Using provided text ({len(text_to_enrich)} characters)\n", flush=True)
        else:
            print("[1/3] Loading chunk from database...", flush=True)
            from db.subtitle_chunks_crud import get_chunk_details
            chunk = get_chunk_details(video_id, chunk_id)
            
            if not chunk:
                print(f"Chunk not found: {video_id} / {chunk_id}", flush=True)
                return False
            
            if not chunk.get('chunk_text'):
                print(f"No chunk text found", flush=True)
                return False
                
            print(f"Found chunk {chunk_id}\n", flush=True)
            text_to_enrich = chunk['chunk_text']
        
        # Step 2: Enrich with AI
        print("[2/3] Enriching chunk with AI...", flush=True)
        
        # Get video prompts
        from prompts import get_all_prompts
        prompts = get_all_prompts(content_type='video')
        
        # Enrich the chunk
        ai_fields = enrich_chunk(
            text=text_to_enrich,
            prompts=prompts,
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
            max_tokens_other=OPENAI_MAX_TOKENS_OTHER
        )
        
        print(f"AI enrichment complete\n", flush=True)
        
        # Step 3: Update database
        print("[3/3] Saving AI fields to database...", flush=True)
        
        updated = update_chunk_ai_fields(
            video_id=video_id,
            chunk_id=chunk_id,
            short_title=ai_fields.get('title'),
            ai_field_1=ai_fields.get('field_1'),
            ai_field_2=ai_fields.get('field_2'),
            ai_field_3=ai_fields.get('field_3')
        )
        
        if updated:
            print(f"Successfully enriched chunk {chunk_id}", flush=True)
            print(f"\n{'='*70}", flush=True)
            print("Chunk AI enrichment complete!", flush=True)
            print(f"{'='*70}\n", flush=True)
            return True
        else:
            print(f"Failed to update chunk in database", flush=True)
            return False
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def regenerate_video_chunk_ai_field(
    video_id: str,
    chunk_id: int,
    field_name: str,
    chunk_text: Optional[str] = None
) -> dict:
    """
    Regenerate a single AI field for a video chunk
    
    Args:
        video_id: Video identifier
        chunk_id: Chunk identifier
        field_name: Field to regenerate ('title', 'field_1', 'field_2', 'field_3')
        chunk_text: Optional chunk text to use (avoids database/storage load)
        
    Returns:
        Dict with the regenerated field value or error
    """
    try:
        # Step 1: Get chunk text
        if chunk_text and chunk_text.strip():
            print("[1/4] Using provided chunk text (no database load needed)...")
            text_to_enrich = chunk_text
        else:
            print("[1/4] Loading chunk from database...")
            from db.subtitle_chunks_crud import get_chunk_details
            chunk = get_chunk_details(video_id, chunk_id)
            
            if not chunk:
                return {'error': 'Chunk not found'}
            
            if not chunk.get('chunk_text'):
                return {'error': 'No chunk text found'}
            
            text_to_enrich = chunk['chunk_text']
        
        # Step 2: Get prompts with only the requested field
        from prompts import get_all_prompts
        all_prompts = get_all_prompts(content_type='video')
        
        # Create selective prompts - only the requested field
        selective_prompts = {
            'title': all_prompts.get('title', '') if field_name == 'title' else '',
            'field_1': all_prompts.get('field_1', '') if field_name == 'field_1' else '',
            'field_2': all_prompts.get('field_2', '') if field_name == 'field_2' else '',
            'field_3': all_prompts.get('field_3', '') if field_name == 'field_3' else ''
        }
        
        print(f"[2/4] Regenerating field '{field_name}' with AI...")
        
        # Step 3: Enrich with AI (only the selected field)
        ai_fields = enrich_chunk(
            text=text_to_enrich,
            prompts=selective_prompts,
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
            max_tokens_other=OPENAI_MAX_TOKENS_OTHER
        )
        
        print(f"[3/4] Field regenerated successfully")
        
        # Step 4: Update database with only the regenerated field
        from db.subtitle_chunks_crud import update_chunk_ai_fields
        
        update_data = {
            'short_title': ai_fields.get('title') if field_name == 'title' else None,
            'ai_field_1': ai_fields.get('field_1') if field_name == 'field_1' else None,
            'ai_field_2': ai_fields.get('field_2') if field_name == 'field_2' else None,
            'ai_field_3': ai_fields.get('field_3') if field_name == 'field_3' else None
        }
        
        # Filter out None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return {'error': 'Invalid field name'}
        
        print(f"[4/4] Saving regenerated field to database...")
        
        updated = update_chunk_ai_fields(
            video_id=video_id,
            chunk_id=chunk_id,
            **update_data
        )
        
        if updated:
            # Return the updated field value
            field_map = {
                'title': 'short_title',
                'field_1': 'ai_field_1',
                'field_2': 'ai_field_2',
                'field_3': 'ai_field_3'
            }
            db_field = field_map.get(field_name)
            print(f"Field regeneration complete!")
            return {
                'success': True,
                'field': field_name,
                'value': updated.get(db_field, '')
            }
        else:
            return {'error': 'Failed to update database'}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


def regenerate_book_chapter_ai_field(
    book_id: str,
    chapter_id: int,
    field_name: str,
    chapter_text: Optional[str] = None
) -> dict:
    """
    Regenerate a single AI field for a book chapter
    
    Args:
        book_id: Book identifier
        chapter_id: Chapter identifier
        field_name: Field to regenerate ('field_1', 'field_2', 'field_3')
        chapter_text: Optional chapter text to use (avoids database/storage load)
        
    Returns:
        Dict with the regenerated field value or error
    """
    try:
        # Step 1: Get chapter text
        if chapter_text and chapter_text.strip():
            print("[1/4] Using provided chapter text (no database load needed)...")
            text_to_enrich = chapter_text
        else:
            print("[1/4] Loading chapter from database...")
            from db.book_chapters_crud import get_chapter_details
            chapter = get_chapter_details(book_id, chapter_id)
            
            if not chapter:
                return {'error': 'Chapter not found'}
            
            if not chapter.get('chapter_text'):
                return {'error': 'No chapter text found'}
            
            text_to_enrich = chapter['chapter_text']
        
        # Step 2: Get prompts with only the requested field
        from prompts import get_all_prompts
        all_prompts = get_all_prompts(content_type='book')
        
        # Create selective prompts - only the requested field
        # Note: Books don't have 'title' field
        selective_prompts = {
            'field_1': all_prompts.get('field_1', '') if field_name == 'field_1' else '',
            'field_2': all_prompts.get('field_2', '') if field_name == 'field_2' else '',
            'field_3': all_prompts.get('field_3', '') if field_name == 'field_3' else ''
        }
        
        print(f"[2/4] Regenerating field '{field_name}' with AI...")
        
        # Step 3: Enrich with AI (only the selected field)
        ai_fields = enrich_chunk(
            text=text_to_enrich,
            prompts=selective_prompts,
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
            max_tokens_other=OPENAI_MAX_TOKENS_OTHER
        )
        
        print(f"[3/4] Field regenerated successfully")
        
        # Step 4: Update database with only the regenerated field
        from db.book_chapters_crud import update_chapter_ai_fields
        
        update_data = {
            'ai_field_1': ai_fields.get('field_1') if field_name == 'field_1' else None,
            'ai_field_2': ai_fields.get('field_2') if field_name == 'field_2' else None,
            'ai_field_3': ai_fields.get('field_3') if field_name == 'field_3' else None
        }
        
        # Filter out None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return {'error': 'Invalid field name'}
        
        print(f"[4/4] Saving regenerated field to database...")
        
        updated = update_chapter_ai_fields(
            book_id=book_id,
            chapter_id=chapter_id,
            **update_data
        )
        
        if updated:
            # Return the updated field value
            field_map = {
                'field_1': 'ai_field_1',
                'field_2': 'ai_field_2',
                'field_3': 'ai_field_3'
            }
            db_field = field_map.get(field_name)
            print(f"Field regeneration complete!")
            return {
                'success': True,
                'field': field_name,
                'value': updated.get(db_field, '')
            }
        else:
            return {'error': 'Failed to update database'}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


