"""
Complete test of subtitle extraction and chunking pipeline
Tests with the full 1+ hour video
"""

import os
import sys
from subtitle_extractor_v2 import extract_clean_transcript
from text_chunker_v2 import chunk_transcript
from config import (
    CHUNK_TARGET_WORDS,
    CHUNK_MAX_WORDS,
    CHUNK_OVERLAP_WORDS,
    CHUNK_MIN_FINAL_WORDS
)


def test_complete_pipeline():
    """Test the complete pipeline with the long video"""
    
    # Video URL - over 1 hour long
    video_url = "https://www.youtube.com/watch?v=m3ojamMNbKM"
    
    print("=" * 80)
    print("COMPLETE SUBTITLE EXTRACTION & CHUNKING TEST")
    print("=" * 80)
    print(f"Video URL: {video_url}")
    print()
    
    # Create output directory
    output_dir = "./test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Extract subtitles
    print("STEP 1: Extracting subtitles...")
    print("-" * 80)
    
    result = extract_clean_transcript(video_url, output_dir=output_dir, remove_fillers=True)
    
    if not result['success']:
        print("✗ Failed to extract subtitles")
        return False
    
    print(f"✓ Successfully extracted subtitles")
    print(f"  Video ID: {result['video_id']}")
    print(f"  SRT File: {result['srt_file']}")
    print(f"  Text length: {len(result['text'])} characters")
    print(f"  Word count: {len(result['text'].split())} words")
    print()
    
    # Save raw transcript
    transcript_file = os.path.join(output_dir, f"transcript_{result['video_id']}.txt")
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(result['text'])
    print(f"✓ Saved transcript to: {transcript_file}")
    print()
    
    # Show sample of cleaned text
    print("Sample of cleaned transcript (first 500 chars):")
    print("-" * 80)
    print(result['text'][:500])
    print("-" * 80)
    print()
    
    # Step 2: Chunk the transcript
    print("STEP 2: Chunking transcript...")
    print("-" * 80)
    
    # Configuration for chunking - using values from prompts_config.py
    chunk_config = {
        'target_words': CHUNK_TARGET_WORDS,
        'max_words': CHUNK_MAX_WORDS,
        'overlap_words': CHUNK_OVERLAP_WORDS,
        'min_final_words': CHUNK_MIN_FINAL_WORDS
    }
    
    chunked_result = chunk_transcript(result['text'], chunk_config)
    
    print(f"✓ Successfully chunked transcript")
    print()
    print("Statistics:")
    print(f"  Total chunks: {chunked_result['statistics']['total_chunks']}")
    print(f"  Total words: {chunked_result['statistics']['total_words']}")
    print(f"  Total sentences: {chunked_result['statistics']['total_sentences']}")
    print(f"  Avg words per chunk: {chunked_result['statistics']['avg_words_per_chunk']:.1f}")
    print(f"  Config: target={chunk_config['target_words']}, max={chunk_config['max_words']}, overlap={chunk_config['overlap_words']}")
    print()
    
    # Step 3: Show detailed chunk information
    print("STEP 3: Chunk details...")
    print("-" * 80)
    
    chunks = chunked_result['chunks']
    
    print(f"\nShowing all {len(chunks)} chunks:\n")
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {chunk['chunk_id']}:")
        print(f"  Word count: {chunk['word_count']}")
        print(f"  Sentence count: {chunk['sentence_count']}")
        print(f"  First 200 chars: {chunk['text'][:200]}...")
        
        # Check if within limits
        status = "✓ OK"
        if chunk['word_count'] > chunk_config['max_words']:
            status = "✗ EXCEEDS MAX"
        elif chunk['word_count'] < chunk_config['target_words'] * 0.5 and i < len(chunks) - 1:
            status = "⚠ TOO SHORT (not last chunk)"
        
        print(f"  Status: {status}")
        print()
    
    # Step 4: Save chunks to individual files
    print("STEP 4: Saving chunks...")
    print("-" * 80)
    
    chunks_dir = os.path.join(output_dir, f"chunks_{result['video_id']}")
    os.makedirs(chunks_dir, exist_ok=True)
    
    for chunk in chunks:
        chunk_file = os.path.join(chunks_dir, f"chunk_{chunk['chunk_id']:03d}.txt")
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(f"Chunk ID: {chunk['chunk_id']}\n")
            f.write(f"Word Count: {chunk['word_count']}\n")
            f.write(f"Sentence Count: {chunk['sentence_count']}\n")
            f.write("-" * 80 + "\n\n")
            f.write(chunk['text'])
        
    print(f"✓ Saved {len(chunks)} chunks to: {chunks_dir}")
    print()
    
    # Step 5: Verify overlap between chunks
    print("STEP 5: Verifying overlap between chunks...")
    print("-" * 80)
    
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]
        
        # Get last N words from current chunk
        current_words = current_chunk['text'].split()[-50:]
        next_words = next_chunk['text'].split()[:50]
        
        # Find overlap
        overlap_count = 0
        for j in range(min(len(current_words), len(next_words))):
            if current_words[-(j+1)] == next_words[j]:
                overlap_count += 1
            else:
                break
        
        print(f"Chunk {i} → {i+1}: {overlap_count} overlapping words")
    
    print()
    
    # Step 6: Create summary report
    print("STEP 6: Summary Report...")
    print("=" * 80)
    
    report = f"""
SUBTITLE EXTRACTION & CHUNKING REPORT
Video: {video_url}
Video ID: {result['video_id']}

EXTRACTION:
- Raw text length: {len(result['text'])} characters
- Total words: {chunked_result['statistics']['total_words']}
- Total sentences: {chunked_result['statistics']['total_sentences']}

CHUNKING CONFIG:
- Target words per chunk: {chunk_config['target_words']}
- Max words per chunk: {chunk_config['max_words']}
- Overlap words: {chunk_config['overlap_words']}

RESULTS:
- Total chunks created: {len(chunks)}
- Average words per chunk: {chunked_result['statistics']['avg_words_per_chunk']:.1f}
- Min words in chunk: {min(c['word_count'] for c in chunks)}
- Max words in chunk: {max(c['word_count'] for c in chunks)}

CHUNK BREAKDOWN:
"""
    
    for chunk in chunks:
        report += f"  Chunk {chunk['chunk_id']}: {chunk['word_count']} words, {chunk['sentence_count']} sentences\n"
    
    report += f"\nOUTPUT FILES:\n"
    report += f"- Transcript: {transcript_file}\n"
    report += f"- Chunks directory: {chunks_dir}\n"
    
    print(report)
    
    # Save report
    report_file = os.path.join(output_dir, f"report_{result['video_id']}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Saved report to: {report_file}")
    print()
    
    print("=" * 80)
    print("✓ TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_complete_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
