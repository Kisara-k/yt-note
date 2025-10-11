"""
Refactored chunking - word-based with sentence boundaries and overlap
No timestamp tracking
"""

import re
from typing import List, Dict, Any

# Import config from central location
from config import (
    CHUNK_TARGET_WORDS,
    CHUNK_MAX_WORDS,
    CHUNK_OVERLAP_WORDS,
    CHUNK_MIN_FINAL_WORDS
)


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into fixed-size word chunks (not actual sentences)
    This is more reliable than trying to detect sentences in poorly formatted transcripts
    
    Args:
        text: Input text
        
    Returns:
        List of fixed-size word chunks
    """
    words = text.split()
    chunk_size = 40  # Fixed word count per pseudo-sentence
    
    sentences = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        sentences.append(' '.join(chunk_words))
    
    return [s for s in sentences if s.strip()]


def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())


def chunk_by_words(
    text: str,
    target_words: int = None,
    max_words: int = None,
    overlap_words: int = None,
    min_final_words: int = None
) -> List[Dict[str, Any]]:
    """
    Chunk text by word count, breaking at sentence boundaries with overlap
    
    Args:
        text: Input text to chunk
        target_words: Target words per chunk (from config)
        max_words: Maximum words per chunk (from config)
        overlap_words: Words to overlap between chunks (from config)
        min_final_words: Minimum words for final chunk (from config)
        
    Returns:
        List of chunks with metadata
    """
    # Use defaults if not provided
    if target_words is None:
        target_words = CHUNK_TARGET_WORDS
    if max_words is None:
        max_words = CHUNK_MAX_WORDS
    if overlap_words is None:
        overlap_words = CHUNK_OVERLAP_WORDS
    if min_final_words is None:
        min_final_words = CHUNK_MIN_FINAL_WORDS
    
    # Split into sentences
    sentences = split_into_sentences(text)
    
    if not sentences:
        return []
    
    chunks = []
    current_chunk_sentences = []
    current_word_count = 0
    chunk_id = 0
    
    for i, sentence in enumerate(sentences):
        sentence_words = count_words(sentence)
        
        # Check if adding this sentence would exceed max_words
        would_exceed_max = current_word_count + sentence_words > max_words
        # Check if we've reached target and should split
        should_split = current_word_count >= target_words and current_chunk_sentences
        
        if would_exceed_max or (should_split and current_word_count > 0):
            # Save current chunk
            chunk_text = ' '.join(current_chunk_sentences)
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'word_count': current_word_count,
                'sentence_count': len(current_chunk_sentences)
            })
            chunk_id += 1
            
            # Start new chunk with overlap
            # Include last N words from previous chunk for context
            if overlap_words > 0 and current_chunk_sentences:
                # Try to find complete sentences in overlap
                overlap_sentences = []
                overlap_count = 0
                
                # Work backwards through recent sentences to build overlap
                for prev_sent in reversed(current_chunk_sentences[-5:]):  # Check last 5 sentences
                    sent_words = count_words(prev_sent)
                    if overlap_count + sent_words <= overlap_words:
                        overlap_sentences.insert(0, prev_sent)
                        overlap_count += sent_words
                    else:
                        break
                
                current_chunk_sentences = overlap_sentences
                current_word_count = overlap_count
            else:
                current_chunk_sentences = []
                current_word_count = 0
        
        # Add sentence to current chunk
        current_chunk_sentences.append(sentence)
        current_word_count += sentence_words
    
    # Handle the last chunk
    if current_chunk_sentences:
        chunk_text = ' '.join(current_chunk_sentences)
        
        # If final chunk is too small, merge with previous chunk
        if current_word_count < min_final_words and len(chunks) > 0:
            # Merge with previous chunk
            prev_chunk = chunks[-1]
            merged_text = prev_chunk['text'] + ' ' + chunk_text
            merged_words = count_words(merged_text)
            
            chunks[-1] = {
                'chunk_id': prev_chunk['chunk_id'],
                'text': merged_text,
                'word_count': merged_words,
                'sentence_count': prev_chunk['sentence_count'] + len(current_chunk_sentences)
            }
        else:
            # Add as separate chunk
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'word_count': current_word_count,
                'sentence_count': len(current_chunk_sentences)
            })
    
    return chunks


def chunk_transcript(
    text: str,
    config: Dict[str, int] = None
) -> Dict[str, Any]:
    """
    Complete chunking pipeline with statistics
    
    Args:
        text: Input text to chunk
        config: Configuration dict with target_words, max_words, overlap_words, min_final_words
        
    Returns:
        Dictionary with chunks and statistics
    """
    if config is None:
        config = {
            'target_words': CHUNK_TARGET_WORDS,
            'max_words': CHUNK_MAX_WORDS,
            'overlap_words': CHUNK_OVERLAP_WORDS,
            'min_final_words': CHUNK_MIN_FINAL_WORDS
        }
    
    chunks = chunk_by_words(
        text,
        target_words=config.get('target_words'),
        max_words=config.get('max_words'),
        overlap_words=config.get('overlap_words'),
        min_final_words=config.get('min_final_words')
    )
    
    total_words = count_words(text)
    total_sentences = len(split_into_sentences(text))
    
    return {
        'chunks': chunks,
        'statistics': {
            'total_chunks': len(chunks),
            'total_words': total_words,
            'total_sentences': total_sentences,
            'avg_words_per_chunk': sum(c['word_count'] for c in chunks) / len(chunks) if chunks else 0,
            'config': config
        }
    }


if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    This is the first sentence. This is the second sentence. This is the third sentence.
    This is the fourth sentence. This is the fifth sentence. This is the sixth sentence.
    This is the seventh sentence. This is the eighth sentence. This is the ninth sentence.
    This is the tenth sentence. And this is the eleventh sentence for good measure.
    """
    
    print("=" * 60)
    print("CHUNKING TEST")
    print("=" * 60)
    
    # Test with small chunks for demonstration
    test_config = {
        'target_words': 15,
        'max_words': 25,
        'overlap_words': 5
    }
    
    result = chunk_transcript(sample_text, test_config)
    
    print(f"\nStatistics:")
    print(f"  Total chunks: {result['statistics']['total_chunks']}")
    print(f"  Total words: {result['statistics']['total_words']}")
    print(f"  Total sentences: {result['statistics']['total_sentences']}")
    print(f"  Avg words/chunk: {result['statistics']['avg_words_per_chunk']:.1f}")
    
    print(f"\nChunks:")
    for chunk in result['chunks']:
        print(f"\n--- Chunk {chunk['chunk_id']} ---")
        print(f"Words: {chunk['word_count']}, Sentences: {chunk['sentence_count']}")
        print(f"Text: {chunk['text'][:100]}...")
