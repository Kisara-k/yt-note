"""
Background worker for processing YouTube videos
Orchestrates subtitle extraction, chunking, and AI enrichment
"""

import os
import sys
import time
from typing import Optional, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from subtitle_extraction import extract_subtitles_for_video
from chunking import chunk_subtitles
from openai_enrichment import enrich_chunk_with_ai

sys.path.append(os.path.join(os.path.dirname(__file__), 'db'))
from db.youtube_crud import get_video_by_id
from db.subtitle_chunks_crud import create_chunk, update_chunk_ai_fields


class VideoProcessor:
    
    def __init__(self):
        pass
    
    def process_video(self, video_id: str) -> bool:
        print(f"\n{'='*70}")
        print(f"[>>] Processing video: {video_id}")
        print(f"{'='*70}\n")
        
        try:
            print("[1/3] Extracting subtitles...")
            subtitle_data = extract_subtitles_for_video(video_id)
            
            if not subtitle_data:
                print("[!!] No subtitles available")
                return False
            
            print(f"[OK] Extracted {subtitle_data['segment_count']} segments")
            
            print("\n[2/3] Chunking subtitles...")
            chunks = chunk_subtitles(subtitle_data)
            
            if not chunks:
                print("[!!] Failed to create chunks")
                return False
            
            print(f"[OK] Created {len(chunks)} chunks")
            
            print("\n[3/3] Processing chunks with AI...")
            for i, chunk in enumerate(chunks, 1):
                print(f"\n{'-'*70}")
                print(f"[>>] Chunk {i}/{len(chunks)} (ID: {chunk['chunk_id']})")
                print(f"{'-'*70}")
                
                chunk_id = chunk['chunk_id']
                chunk_text = chunk['text']
                start_time = chunk['start_time']
                end_time = chunk['end_time']
                
                print(f"Duration: {end_time - start_time:.1f}s | Text: {len(chunk_text)} chars")
                print(f"Time range: {start_time:.1f}s - {end_time:.1f}s")
                
                print("\nStarting AI enrichment...")
                ai_results = enrich_chunk_with_ai(chunk_text)
                
                print(f"\nSaving to database...")
                create_chunk(
                    video_id=video_id,
                    chunk_id=chunk_id,
                    start_time=start_time,
                    end_time=end_time,
                    chunk_text=chunk_text,
                    short_title=ai_results.get('short_title'),
                    ai_field_1=ai_results.get('ai_field_1'),
                    ai_field_2=ai_results.get('ai_field_2'),
                    ai_field_3=ai_results.get('ai_field_3')
                )
                
                print(f"[OK] Chunk {chunk_id} complete\n")
            
            print(f"\n{'='*70}")
            print(f"[OK] Video {video_id} processed successfully!")
            print(f"{'='*70}\n")
            
            return True
            
        except Exception as e:
            print(f"\n[!!] Error processing video: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Background worker for video processing")
    parser.add_argument('video_id', type=str, help='YouTube video ID to process')
    
    args = parser.parse_args()
    
    processor = VideoProcessor()
    processor.process_video(args.video_id)
