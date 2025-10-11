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
from openai import enrich_chunk, enrich_chunks_parallel

# Import from db
from db.youtube_crud import create_or_update_video, get_video_by_id, bulk_create_or_update_videos
from db.subtitle_chunks_crud import create_chunk, get_chunks_by_video
from db.video_notes_crud import create_or_update_note, get_note_by_video_id


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
    Enrich a single chunk with AI
    Returns: dict with title, field_1, field_2, field_3
    """
    prompts = get_all_prompts()
    
    result = enrich_chunk(
        text=chunk_text,
        prompts=prompts,
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        max_tokens_title=OPENAI_MAX_TOKENS_TITLE,
        max_tokens_other=OPENAI_MAX_TOKENS_OTHER
    )
    
    return result


def process_chunks_enrichment_parallel(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich multiple chunks in parallel
    Returns: list of enriched chunks
    """
    prompts = get_all_prompts()
    
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


def process_full_video(video_id: str) -> bool:
    """
    Complete video processing pipeline:
    1. Extract and chunk subtitles
    2. Enrich chunks with AI (parallel)
    3. Save to database
    
    Returns: True if successful
    """
    print(f"\n{'='*70}")
    print(f"Processing video: {video_id}")
    print(f"{'='*70}\n")
    
    try:
        # Step 1: Extract subtitles
        print("[1/3] Extracting subtitles...")
        chunks = process_video_subtitles(video_id)
        
        if not chunks:
            print("No subtitles available")
            return False
        
        print(f"Created {len(chunks)} chunks\n")
        
        # Step 2: Enrich with AI (parallel)
        print("[2/3] Enriching chunks with AI (parallel)...")
        enriched_chunks = process_chunks_enrichment_parallel(chunks)
        print(f"Enriched {len(enriched_chunks)} chunks\n")
        
        # Step 3: Save to database
        print("[3/3] Saving to database...")
        for i, chunk in enumerate(enriched_chunks):
            create_chunk(
                video_id=video_id,
                chunk_id=i,
                chunk_text=chunk['text'],
                word_count=chunk['word_count'],
                sentence_count=chunk['sentence_count'],
                short_title=chunk.get('title', ''),
                ai_field_1=chunk.get('field_1', ''),
                ai_field_2=chunk.get('field_2', ''),
                ai_field_3=chunk.get('field_3', '')
            )
        
        print(f"Saved {len(enriched_chunks)} chunks")
        print(f"\n{'='*70}")
        print("Processing complete!")
        print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
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
