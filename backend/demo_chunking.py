"""
Quick demonstration script - Shows the complete workflow
"""

import os
from subtitle_extractor_v2 import extract_clean_transcript
from text_chunker_v2 import chunk_transcript
from config import (
    CHUNK_TARGET_WORDS,
    CHUNK_MAX_WORDS,
    CHUNK_OVERLAP_WORDS,
    CHUNK_MIN_FINAL_WORDS
)

# Test video (1+ hour long)
VIDEO_URL = "https://www.youtube.com/watch?v=m3ojamMNbKM"

print("=" * 80)
print("SUBTITLE EXTRACTION & CHUNKING DEMO")
print("=" * 80)
print()

# Step 1: Extract subtitles
print("Step 1: Extracting and cleaning subtitles...")
result = extract_clean_transcript(VIDEO_URL, output_dir="./demo_output", remove_fillers=True)

if not result['success']:
    print("✗ Failed to extract subtitles")
    exit(1)

print(f"✓ Extracted {len(result['text'])} characters, {len(result['text'].split())} words")
print()

# Step 2: Chunk the text
print("Step 2: Chunking by word count...")
chunk_config = {
    'target_words': CHUNK_TARGET_WORDS,
    'max_words': CHUNK_MAX_WORDS,
    'overlap_words': CHUNK_OVERLAP_WORDS,
    'min_final_words': CHUNK_MIN_FINAL_WORDS
}

chunked = chunk_transcript(result['text'], chunk_config)

print(f"✓ Created {len(chunked['chunks'])} chunks")
print(f"  Average words per chunk: {chunked['statistics']['avg_words_per_chunk']:.1f}")
print()

# Step 3: Show sample chunks
print("Sample chunks:")
print("-" * 80)
for i, chunk in enumerate(chunked['chunks'][:3]):  # Show first 3 chunks
    print(f"\nChunk {chunk['chunk_id']}:")
    print(f"  Words: {chunk['word_count']}, Sentences: {chunk['sentence_count']}")
    print(f"  Preview: {chunk['text'][:150]}...")

print()

# Step 4: Save chunks to demo_output
print("Step 3: Saving chunks to demo_output...")
chunks_dir = os.path.join("./demo_output", f"chunks_{result['video_id']}")
os.makedirs(chunks_dir, exist_ok=True)

for chunk in chunked['chunks']:
    chunk_file = os.path.join(chunks_dir, f"chunk_{chunk['chunk_id']:03d}.txt")
    with open(chunk_file, 'w', encoding='utf-8') as f:
        f.write(f"Chunk ID: {chunk['chunk_id']}\n")
        f.write(f"Word Count: {chunk['word_count']}\n")
        f.write(f"Sentence Count: {chunk['sentence_count']}\n")
        f.write("-" * 80 + "\n\n")
        f.write(chunk['text'])

print(f"✓ Saved {len(chunked['chunks'])} chunks to: {chunks_dir}")
print()

print("=" * 80)
print("✓ DEMO COMPLETE")
print(f"✓ Successfully processed 1+ hour video into {len(chunked['chunks'])} clean chunks")
print(f"✓ Chunks saved to: {chunks_dir}")
print("=" * 80)
