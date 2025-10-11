"""
Subtitle extraction module using yt-dlp
Downloads and parses subtitles with proper timing information
"""

import os
import sys
import tempfile
import re
from typing import Optional, Dict, Any, List
import subprocess
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def parse_srt_time(time_str: str) -> float:
    """
    Convert SRT timestamp to seconds
    Format: HH:MM:SS,mmm
    
    Args:
        time_str: Time string like "00:01:23,456"
        
    Returns:
        Time in seconds as float
    """
    # Remove any whitespace
    time_str = time_str.strip()
    
    # Split into time and milliseconds
    parts = time_str.replace(',', '.').split(':')
    
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    
    return 0.0


def parse_srt_file(srt_content: str) -> List[Dict[str, Any]]:
    """
    Parse SRT subtitle file content into segments with timing
    
    Args:
        srt_content: Raw SRT file content
        
    Returns:
        List of segments with start_time, end_time, and text
    """
    segments = []
    
    # Split into subtitle blocks (separated by blank lines)
    blocks = re.split(r'\n\s*\n', srt_content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        
        if len(lines) < 3:
            continue
        
        # First line is the sequence number (skip)
        # Second line is the timing
        # Remaining lines are the subtitle text
        
        timing_line = lines[1]
        text_lines = lines[2:]
        
        # Parse timing: "00:00:01,000 --> 00:00:04,000"
        timing_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', timing_line)
        
        if timing_match:
            start_time_str = timing_match.group(1)
            end_time_str = timing_match.group(2)
            
            start_time = parse_srt_time(start_time_str)
            end_time = parse_srt_time(end_time_str)
            
            # Join text lines and clean
            text = ' '.join(text_lines).strip()
            
            # Remove formatting tags like <i>, </i>, <b>, </b>
            text = re.sub(r'<[^>]+>', '', text)
            
            if text:  # Only add if there's actual text
                segments.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': text
                })
    
    return segments


class SubtitleExtractor:
    """Handles subtitle extraction using yt-dlp"""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.temp_dir = tempfile.mkdtemp()
    
    def check_yt_dlp_installed(self) -> bool:
        """Check if yt-dlp is installed"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_bash_shell(self) -> Optional[str]:
        """Detect available bash shell (Git Bash or WSL)"""
        # Check for Git Bash
        git_bash_paths = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe"
        ]
        for path in git_bash_paths:
            if os.path.exists(path):
                return path
        
        # Check for WSL
        try:
            result = subprocess.run(['wsl', '--version'], capture_output=True, timeout=2)
            if result.returncode == 0:
                return 'wsl'
        except:
            pass
        
        return None
    
    def download_subtitles(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Download subtitles and parse with timing information
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of segments with start_time, end_time, text or None if not available
        """
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Get bash shell
            bash_shell = self.get_bash_shell()
            if not bash_shell:
                print("❌ No bash shell found (Git Bash or WSL required)")
                return None
            
            # Change to temp directory
            original_dir = os.getcwd()
            os.chdir(self.temp_dir)
            
            try:
                # Download SRT subtitles (don't strip timing yet)
                cmd = f'yt-dlp --write-subs --write-auto-subs --sub-lang {self.language} --skip-download --convert-subs srt -o "subtitle.%(ext)s" {video_url}'
                
                if bash_shell == 'wsl':
                    result = subprocess.run(
                        ['wsl', 'bash', '-c', cmd],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                else:
                    result = subprocess.run(
                        [bash_shell, '-c', cmd],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                
                # Find the downloaded SRT file
                srt_files = glob.glob(os.path.join(self.temp_dir, f'*.{self.language}.srt'))
                
                if not srt_files:
                    print(f"✗ No subtitles found for video: {video_id}")
                    return None
                
                srt_file = srt_files[0]
                
                # Read and parse SRT file
                with open(srt_file, 'r', encoding='utf-8') as f:
                    srt_content = f.read()
                
                segments = parse_srt_file(srt_content)
                
                # Clean up
                for file in glob.glob(os.path.join(self.temp_dir, '*.srt')):
                    try:
                        os.remove(file)
                    except:
                        pass
                
                if segments:
                    print(f"✓ Downloaded {len(segments)} subtitle segments for video: {video_id}")
                    return segments
                else:
                    print(f"✗ No valid segments found in subtitles")
                    return None
                
            finally:
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            print(f"Timeout downloading subtitles for video: {video_id}")
            return None
        except Exception as e:
            print(f"Error downloading subtitles: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def extract_subtitles_for_video(
    video_id: str,
    language: str = 'en'
) -> Optional[Dict[str, Any]]:
    """
    Main function to extract subtitles for a video with proper timing
    
    Args:
        video_id: YouTube video ID
        language: Preferred language code
        
    Returns:
        Dictionary with subtitle data or None if unavailable
    """
    extractor = SubtitleExtractor(language=language)
    
    if not extractor.check_yt_dlp_installed():
        print("✗ yt-dlp is not installed. Run: pip install yt-dlp")
        return None
    
    segments = extractor.download_subtitles(video_id)
    
    if segments:
        # Calculate full transcript text
        full_text = ' '.join(seg['text'] for seg in segments)
        
        return {
            'video_id': video_id,
            'language': language,
            'full_text': full_text,
            'segments': segments,
            'segment_count': len(segments),
            'total_duration': segments[-1]['end_time'] if segments else 0
        }
    else:
        return None


if __name__ == "__main__":
    # Test with a video
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    print(f"\nTesting subtitle extraction for video: {test_video_id}\n")
    print("="*70)
    
    result = extract_subtitles_for_video(test_video_id)
    
    if result:
        print(f"\n✅ Subtitle extraction successful!")
        print(f"Language: {result['language']}")
        print(f"Segments: {result['segment_count']}")
        print(f"Duration: {result['total_duration']:.2f} seconds")
        print(f"\nFirst 3 segments:")
        for i, seg in enumerate(result['segments'][:3], 1):
            print(f"\n  Segment {i}:")
            print(f"  Time: {seg['start_time']:.2f}s - {seg['end_time']:.2f}s")
            print(f"  Text: {seg['text'][:100]}...")
    else:
        print("\n❌ Failed to extract subtitles")
