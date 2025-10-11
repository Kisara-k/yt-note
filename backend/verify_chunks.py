"""
Quick verification of chunking quality
Shows concrete proof that chunks are correct
"""

import os
import glob


def verify_chunks(chunks_dir: str):
    """Verify chunk quality and show proof"""
    
    print("=" * 80)
    print("CHUNK QUALITY VERIFICATION")
    print("=" * 80)
    print()
    
    # Get all chunk files
    chunk_files = sorted(glob.glob(os.path.join(chunks_dir, "chunk_*.txt")))
    
    if not chunk_files:
        print("✗ No chunk files found")
        return False
    
    print(f"Found {len(chunk_files)} chunks")
    print()
    
    total_words = 0
    chunk_details = []
    
    for chunk_file in chunk_files:
        with open(chunk_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Parse metadata
            chunk_id = None
            word_count = None
            sentence_count = None
            text = []
            
            in_text = False
            for line in lines:
                if line.startswith("Chunk ID:"):
                    chunk_id = int(line.split(":")[1].strip())
                elif line.startswith("Word Count:"):
                    word_count = int(line.split(":")[1].strip())
                elif line.startswith("Sentence Count:"):
                    sentence_count = int(line.split(":")[1].strip())
                elif line.startswith("-" * 40):
                    in_text = True
                elif in_text:
                    text.append(line)
            
            text_content = ''.join(text).strip()
            actual_word_count = len(text_content.split())
            
            chunk_details.append({
                'id': chunk_id,
                'claimed_words': word_count,
                'actual_words': actual_word_count,
                'sentence_count': sentence_count,
                'text': text_content
            })
            
            total_words += actual_word_count
    
    # Verify each chunk
    print("CHUNK VERIFICATION:")
    print("-" * 80)
    
    all_valid = True
    for chunk in chunk_details:
        status = "✓" if chunk['claimed_words'] == chunk['actual_words'] else "✗"
        
        print(f"Chunk {chunk['id']:2d}: {status} {chunk['actual_words']:4d} words, {chunk['sentence_count']:2d} sentences")
        
        if chunk['claimed_words'] != chunk['actual_words']:
            print(f"  ⚠ Word count mismatch: claimed={chunk['claimed_words']}, actual={chunk['actual_words']}")
            all_valid = False
    
    print()
    print(f"Total words across all chunks: {total_words}")
    print()
    
    # Show first and last chunk samples
    print("FIRST CHUNK SAMPLE (first 300 chars):")
    print("-" * 80)
    print(chunk_details[0]['text'][:300])
    print("...")
    print()
    
    print("LAST CHUNK SAMPLE (last 300 chars):")
    print("-" * 80)
    print("...")
    print(chunk_details[-1]['text'][-300:])
    print()
    
    # Check for overlap between consecutive chunks
    print("OVERLAP ANALYSIS:")
    print("-" * 80)
    
    for i in range(len(chunk_details) - 1):
        current = chunk_details[i]
        next_chunk = chunk_details[i + 1]
        
        # Get last 20 words of current chunk
        current_end = ' '.join(current['text'].split()[-20:])
        # Get first 20 words of next chunk
        next_start = ' '.join(next_chunk['text'].split()[:20])
        
        # Simple overlap check
        overlap_found = False
        for j in range(10, 0, -1):
            current_words = current['text'].split()[-j:]
            next_words = next_chunk['text'].split()[:j]
            
            if current_words == next_words:
                print(f"Chunk {i} → {i+1}: {j} words overlap")
                overlap_found = True
                break
        
        if not overlap_found:
            print(f"Chunk {i} → {i+1}: No overlap detected")
    
    print()
    
    # Final verdict
    print("=" * 80)
    if all_valid:
        print("✓ ALL CHUNKS VERIFIED - Word counts match, chunking is correct!")
    else:
        print("✗ SOME ISSUES FOUND - Check warnings above")
    print("=" * 80)
    
    return all_valid


if __name__ == "__main__":
    chunks_dir = "./test_output/chunks_m3ojamMNbKM"
    
    if not os.path.exists(chunks_dir):
        print(f"✗ Chunks directory not found: {chunks_dir}")
        print("Run test_subtitle_pipeline.py first!")
    else:
        verify_chunks(chunks_dir)
