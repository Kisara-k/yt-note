"""
Subtitles module - Extract and chunk YouTube subtitles
Input: video_id (str)
Output: List of chunk dicts with text, word_count, sentence_count
"""

import os
import subprocess
import re
import glob
from typing import Optional, List, Dict, Any


def _download_subtitles(video_id: str, output_dir: str = "./subtitles_temp") -> Optional[str]:
    """Download subtitles using yt-dlp"""
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "yt-dlp",
        "--write-auto-sub",
        "--write-sub",
        "--sub-lang", "en",
        "--skip-download",
        "--sub-format", "srt",
        "-o", f"{output_dir}/%(title)s.%(ext)s",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        srt_files = glob.glob(f"{output_dir}/*.srt")
        if not srt_files:
            return None
        
        return srt_files[0]
    except subprocess.CalledProcessError:
        return None


def _clean_srt_to_text(srt_file: str) -> str:
    """Convert SRT to plain text"""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove timestamp lines
    text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
    # Remove sequence numbers
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    # Remove >> markers (subtitle artifacts)
    text = re.sub(r'>>\s*', '', text)
    # Remove empty lines
    text = re.sub(r'\n\s*\n', '\n', text)
    # Clean extra whitespace
    text = ' '.join(text.split())
    
    return text


def _remove_filler_words(text: str) -> str:
    """Remove common filler words and repeated words while preserving meaning"""
    # Common verbal fillers and hedging words that don't add meaning
    fillers = [
        # Verbal fillers
        r'\buh+\b', r'\bum+\b', r'\buhm+\b', r'\bah+\b', r'\beh+\b',
        r'\ber+\b', r'\bhmm+\b',
        
        # Discourse markers (when overused)
        r'\byou know\b', r'\bI mean\b', r'\bkind of\b', r'\bsort of\b',
        r'\blike\b(?!\s+to\b)',  # Keep "like to" but remove filler "like"
        
        # Unnecessary qualifiers (context-dependent, use sparingly)
        r'\bbasically\b', r'\bactually\b', r'\bliterally\b', 
        r'\bpretty much\b', r'\bmore or less\b',
        
        # Redundant phrases
        r'\bat the end of the day\b', r'\bto be honest\b', r'\bto tell you the truth\b',
        r'\bif you will\b', r'\bso to speak\b',
        
        # Starting phrases (context-dependent)
        r'\bwell,?\s+', r'\bso,?\s+(?!that\b|what\b|when\b|where\b|who\b|why\b|how\b)',  # Keep "so that", "so what" etc.
        r'\balright,?\s+', r'\bokay,?\s+', r'\bright,?\s+',
        
        # Thinking indicators
        r'\blet me see\b', r'\blet\'s see\b', r'\bwhat else\b'
    ]
    
    for filler in fillers:
        text = re.sub(filler, '', text, flags=re.IGNORECASE)
    
    # Remove repeated consecutive words (stuttering or emphasis)
    text = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)

    # YouTube swear filter
    text = re.sub(r'\[ __ \] *', '', text)
    
    # Clean up multiple spaces and normalize whitespace
    text = ' '.join(text.split())
    
    return text


def _split_into_sentences(text: str, words_per_segment: int = 40) -> List[str]:
    """Split text into fixed-size segments"""
    words = text.split()
    sentences = []
    
    for i in range(0, len(words), words_per_segment):
        segment = ' '.join(words[i:i + words_per_segment])
        sentences.append(segment)
    
    return sentences


def _chunk_by_words(sentences: List[str], target_words: int, max_words: int, 
                    overlap_words: int, min_final_words: int) -> List[Dict[str, Any]]:
    """Create chunks from sentences"""
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_word_count + sentence_words > max_words and current_chunk:
            # Save current chunk
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'word_count': current_word_count,
                'sentence_count': len(current_chunk)
            })
            
            # Start new chunk with overlap
            overlap_sentences = []
            overlap_count = 0
            for s in reversed(current_chunk):
                s_words = len(s.split())
                if overlap_count + s_words <= overlap_words:
                    overlap_sentences.insert(0, s)
                    overlap_count += s_words
                else:
                    break
            
            current_chunk = overlap_sentences
            current_word_count = overlap_count
        
        current_chunk.append(sentence)
        current_word_count += sentence_words
        
        if current_word_count >= target_words:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'word_count': current_word_count,
                'sentence_count': len(current_chunk)
            })
            
            # Start new chunk with overlap
            overlap_sentences = []
            overlap_count = 0
            for s in reversed(current_chunk):
                s_words = len(s.split())
                if overlap_count + s_words <= overlap_words:
                    overlap_sentences.insert(0, s)
                    overlap_count += s_words
                else:
                    break
            
            current_chunk = overlap_sentences
            current_word_count = overlap_count
    
    # Handle final chunk
    if current_chunk:
        if current_word_count >= min_final_words or not chunks:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'word_count': current_word_count,
                'sentence_count': len(current_chunk)
            })
        else:
            # Merge with last chunk
            if chunks:
                last_chunk_text = chunks[-1]['text']
                merged_text = last_chunk_text + ' ' + ' '.join(current_chunk)
                chunks[-1] = {
                    'text': merged_text,
                    'word_count': len(merged_text.split()),
                    'sentence_count': chunks[-1]['sentence_count'] + len(current_chunk)
                }
    
    return chunks


def extract_and_chunk_subtitles(
    video_id: str,
    target_words: int = 1000,
    max_words: int = 1500,
    overlap_words: int = 100,
    min_final_words: int = 500
) -> Optional[List[Dict[str, Any]]]:
    """
    Main function: Extract subtitles and return list of chunks
    Returns: List of dicts with 'text', 'word_count', 'sentence_count'
    """
    # Download subtitles
    srt_file = _download_subtitles(video_id)
    if not srt_file:
        return None
    
    try:
        # Clean text
        text = _clean_srt_to_text(srt_file)
        text = _remove_filler_words(text)
        
        # Split and chunk
        sentences = _split_into_sentences(text)
        chunks = _chunk_by_words(sentences, target_words, max_words, overlap_words, min_final_words)
        
        return chunks
    finally:
        # Cleanup temp file
        if os.path.exists(srt_file):
            os.remove(srt_file)
        temp_dir = os.path.dirname(srt_file)
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
