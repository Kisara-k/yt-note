"""
Chunking module for subtitle segmentation
Chunks segments with proper timing into 40-minute blocks (max 60 minutes for final chunk)
"""

import os
import sys
from typing import List, Dict, Any
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts_config import CHUNK_TARGET_DURATION, CHUNK_MAX_DURATION


def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def chunk_subtitle_segments(
    segments: List[Dict[str, Any]],
    target_duration: float = None,
    max_duration: float = None
) -> List[Dict[str, Any]]:
    if target_duration is None:
        target_duration = CHUNK_TARGET_DURATION
    if max_duration is None:
        max_duration = CHUNK_MAX_DURATION
    
    if not segments:
        return []
    
    chunks = []
    current_chunk = {
        'segments': [],
        'start_time': segments[0]['start_time'],
        'texts': []
    }
    
    chunk_id = 0
    
    for segment in segments:
        current_duration = segment['end_time'] - current_chunk['start_time']
        
        # Check if we should start a new chunk
        # Don't split if we're under max_duration (allows last chunk to be up to 60 min)
        should_split = (
            current_duration >= target_duration and 
            current_chunk['segments'] and
            current_duration < max_duration
        )
        
        if should_split:
            last_segment = current_chunk['segments'][-1]
            chunk = {
                'chunk_id': chunk_id,
                'start_time': current_chunk['start_time'],
                'end_time': last_segment['end_time'],
                'text': ' '.join(current_chunk['texts']),  # Use 'text' not 'chunk_text'
                'segment_count': len(current_chunk['segments'])
            }
            chunks.append(chunk)
            chunk_id += 1
            
            current_chunk = {
                'segments': [],
                'start_time': segment['start_time'],
                'texts': []
            }
        
        current_chunk['segments'].append(segment)
        current_chunk['texts'].append(segment['text'])
    
    if current_chunk['segments']:
        last_segment = current_chunk['segments'][-1]
        chunk = {
            'chunk_id': chunk_id,
            'start_time': current_chunk['start_time'],
            'end_time': last_segment['end_time'],
            'text': ' '.join(current_chunk['texts']),  # Use 'text' not 'chunk_text'
            'segment_count': len(current_chunk['segments'])
        }
        chunks.append(chunk)
    
    return chunks


def chunk_subtitles(
    subtitle_data: Dict[str, Any],
    target_duration: float = None,
    max_duration: float = None
) -> List[Dict[str, Any]]:
    segments = subtitle_data.get('segments', [])
    video_id = subtitle_data.get('video_id', '')
    
    chunks = chunk_subtitle_segments(segments, target_duration, max_duration)
    
    for chunk in chunks:
        chunk['video_id'] = video_id
    
    print(f"\n✓ Created {len(chunks)} chunks")
    
    return chunks


if __name__ == "__main__":
    # Test chunking with sample data
    print("="*70)
    print("Testing Subtitle Chunking")
    print("="*70)
    
    # Create sample segments (simulating 15 minutes of subtitles)
    sample_segments = []
    current_time = 0.0
    
    for i in range(180):  # 180 segments = 15 minutes
        segment = {
            'start_time': current_time,
            'end_time': current_time + 5.0,  # 5 second segments
            'text': f"This is subtitle segment number {i+1} with some sample text content."
        }
        sample_segments.append(segment)
        current_time += 5.0
    
    subtitle_data = {
        'video_id': 'test_video',
        'segments': sample_segments,
        'total_duration': current_time
    }
    
    print(f"\nInput: {len(sample_segments)} segments, {current_time} seconds total")
    
    # Test with default 5-minute chunks
    chunks = chunk_subtitles(subtitle_data, target_duration=300.0)
    
    print("\nChunks created:")
    print("-"*70)
    
    for chunk in chunks:
        duration = chunk['end_time'] - chunk['start_time']
        text_preview = chunk['text'][:50] + "..."
        
        print(f"\nChunk {chunk['chunk_id']}:")
        print(f"  Time: {format_time(chunk['start_time'])} - {format_time(chunk['end_time'])}")
        print(f"  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"  Segments: {chunk['segment_count']}")
        print(f"  Text length: {len(chunk['text'])} chars")
        print(f"  Preview: {text_preview}")
    
    print("\n" + "="*70)
    print(f"✅ Chunking test complete!")
