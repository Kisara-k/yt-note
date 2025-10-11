"""
Refactored subtitle extraction - plain text without timestamps
Uses yt-dlp to download and clean subtitles
"""

import os
import subprocess
import re
import glob
from typing import Optional, List


# Filler words to remove
FILLER_WORDS = [
    r'\b(um|uh|er|ah|like|you know|sort of|kind of|i mean|basically|actually|literally)\b',
    r'\[Music\]',
    r'\[Applause\]',
    r'\[Laughter\]',
    r'\[Inaudible\]',
]


def download_subtitles(video_url: str, output_dir: str = ".") -> Optional[str]:
    """
    Download subtitles using yt-dlp
    Tries English subtitles first, then auto-generated
    
    Args:
        video_url: YouTube video URL
        output_dir: Directory to save subtitle files
        
    Returns:
        Path to the downloaded .srt file or None if failed
    """
    try:
        # Extract video ID from URL
        video_id = video_url.split("watch?v=")[1].split("&")[0]
        
        # Command to download subtitles
        cmd = [
            "yt-dlp",
            "--write-subs",          # Download manual subtitles
            "--write-auto-subs",     # Download auto-generated if manual not available
            "--sub-lang", "en",      # English subtitles
            "--skip-download",       # Don't download video
            "--convert-subs", "srt", # Convert to SRT format
            "-o", f"{output_dir}/%(title)s.%(ext)s",
            video_url
        ]
        
        print(f"Downloading subtitles for {video_id}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Find the downloaded .srt file
        srt_files = glob.glob(os.path.join(output_dir, "*.en.srt"))
        
        if srt_files:
            print(f"✓ Downloaded subtitle file: {srt_files[0]}")
            return srt_files[0]
        else:
            print("✗ No subtitle file found after download")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error downloading subtitles: {e}")
        print(f"STDERR: {e.stderr}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def clean_srt_to_text(srt_file_path: str) -> str:
    """
    Clean SRT file to plain text
    Removes: sequence numbers, timestamps, empty lines, HTML tags
    
    Args:
        srt_file_path: Path to .srt file
        
    Returns:
        Clean plain text
    """
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove sequence numbers (lines with only digits)
        content = re.sub(r'^\d+$', '', content, flags=re.MULTILINE)
        
        # Remove timestamp lines (HH:MM:SS,mmm --> HH:MM:SS,mmm)
        content = re.sub(r'^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}.*$', '', content, flags=re.MULTILINE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove empty lines
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Join lines and normalize whitespace
        # Keep track of previous line to avoid duplicates
        cleaned_lines = []
        prev_line = None
        
        for line in lines:
            # Normalize whitespace within line
            line = ' '.join(line.split())
            
            # Only add if different from previous line
            if line and line != prev_line:
                cleaned_lines.append(line)
                prev_line = line
        
        # Join all lines with spaces
        text = ' '.join(cleaned_lines)
        
        # Final whitespace normalization
        text = ' '.join(text.split())
        
        return text
        
    except Exception as e:
        print(f"✗ Error cleaning SRT file: {e}")
        return ""


def remove_filler_words(text: str, filler_patterns: List[str] = None) -> str:
    """
    Remove filler words and common transcription artifacts
    
    Args:
        text: Input text
        filler_patterns: List of regex patterns to remove (uses default if None)
        
    Returns:
        Text with filler words removed
    """
    if filler_patterns is None:
        filler_patterns = FILLER_WORDS
    
    cleaned = text
    
    for pattern in filler_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Normalize whitespace after removal
    cleaned = ' '.join(cleaned.split())
    
    return cleaned


def extract_clean_transcript(video_url: str, output_dir: str = ".", remove_fillers: bool = True) -> dict:
    """
    Complete pipeline: download, clean, and return transcript
    
    Args:
        video_url: YouTube video URL
        output_dir: Directory for temporary files
        remove_fillers: Whether to remove filler words
        
    Returns:
        Dictionary with 'success', 'text', 'srt_file', 'video_id'
    """
    result = {
        'success': False,
        'text': '',
        'srt_file': None,
        'video_id': None
    }
    
    try:
        # Extract video ID
        video_id = video_url.split("watch?v=")[1].split("&")[0]
        result['video_id'] = video_id
        
        # Download subtitles
        srt_file = download_subtitles(video_url, output_dir)
        if not srt_file:
            return result
        
        result['srt_file'] = srt_file
        
        # Clean to plain text
        text = clean_srt_to_text(srt_file)
        if not text:
            return result
        
        # Remove filler words if requested
        if remove_fillers:
            text = remove_filler_words(text)
        
        result['text'] = text
        result['success'] = True
        
        return result
        
    except Exception as e:
        print(f"✗ Error in transcript extraction: {e}")
        return result


if __name__ == "__main__":
    # Test with the provided video
    video_url = "https://www.youtube.com/watch?v=m3ojamMNbKM"
    
    print("=" * 60)
    print("SUBTITLE EXTRACTION TEST")
    print("=" * 60)
    
    result = extract_clean_transcript(video_url, output_dir="./test_output", remove_fillers=True)
    
    if result['success']:
        print(f"\n✓ Successfully extracted transcript")
        print(f"Video ID: {result['video_id']}")
        print(f"SRT File: {result['srt_file']}")
        print(f"Text length: {len(result['text'])} characters")
        print(f"Word count: {len(result['text'].split())}")
        print(f"\nFirst 500 characters:")
        print("-" * 60)
        print(result['text'][:500])
        print("-" * 60)
        
        # Save to file
        output_file = f"./test_output/transcript_{result['video_id']}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        print(f"\n✓ Saved full transcript to: {output_file}")
    else:
        print(f"\n✗ Failed to extract transcript")
