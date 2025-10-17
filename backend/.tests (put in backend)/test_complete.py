"""
Complete test suite for refactored backend
Tests all modules, orchestrator, and API
"""

import sys
import os

def test_imports():
    """Test all module imports"""
    print("\n" + "="*70)
    print("TEST 1: Module Imports")
    print("="*70)
    
    tests = [
        ("youtube module", lambda: __import__('youtube')),
        ("subtitles module", lambda: __import__('subtitles')),
        ("openai module", lambda: __import__('openai')),
        ("orchestrator", lambda: __import__('orchestrator')),
        ("config", lambda: __import__('config')),
        ("prompts", lambda: __import__('prompts')),
        ("API", lambda: __import__('api')),
    ]
    
    passed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
    
    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)


def test_youtube_module():
    """Test YouTube module functions"""
    print("\n" + "="*70)
    print("TEST 2: YouTube Module")
    print("="*70)
    
    from youtube import extract_video_id, fetch_video_metadata
    
    # Test URL extraction
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ]
    
    passed = 0
    for url, expected in test_cases:
        result = extract_video_id(url)
        if result == expected:
            print(f"✓ Extract from: {url[:40]}")
            passed += 1
        else:
            print(f"✗ Extract failed: {url}")
    
    # Test metadata fetch
    try:
        metadata = fetch_video_metadata("dQw4w9WgXcQ")
        if metadata and 'title' in metadata:
            print(f"✓ Fetch metadata: {metadata['title'][:40]}")
            passed += 1
        else:
            print("✗ Fetch metadata failed")
    except Exception as e:
        print(f"✗ Fetch metadata error: {e}")
    
    print(f"\nPassed: {passed}/{len(test_cases) + 1}")
    return passed == len(test_cases) + 1


def test_subtitles_module():
    """Test subtitles module"""
    print("\n" + "="*70)
    print("TEST 3: Subtitles Module")
    print("="*70)
    
    from subtitles import extract_and_chunk_subtitles
    
    try:
        chunks = extract_and_chunk_subtitles(
            video_id="dQw4w9WgXcQ",
            target_words=500,
            max_words=700,
            overlap_words=50,
            min_final_words=300
        )
        
        if chunks and len(chunks) > 0:
            print(f"✓ Extracted {len(chunks)} chunks")
            print(f"  Chunk 0: {chunks[0]['word_count']} words, {chunks[0]['sentence_count']} sentences")
            print(f"  Preview: {chunks[0]['text'][:80]}...")
            return True
        else:
            print("✗ No chunks created")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_orchestrator():
    """Test orchestrator functions"""
    print("\n" + "="*70)
    print("TEST 4: Orchestrator")
    print("="*70)
    
    from orchestrator import (
        process_video_metadata,
        process_video_subtitles,
        process_chunk_enrichment
    )
    
    passed = 0
    
    # Test metadata processing
    try:
        metadata = process_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        if metadata:
            print(f"✓ process_video_metadata: {metadata['title'][:40]}")
            passed += 1
        else:
            print("✗ process_video_metadata failed")
    except Exception as e:
        print(f"✗ process_video_metadata error: {e}")
    
    # Test subtitle processing
    try:
        chunks = process_video_subtitles("dQw4w9WgXcQ")
        if chunks:
            print(f"✓ process_video_subtitles: {len(chunks)} chunks")
            passed += 1
        else:
            print("✗ process_video_subtitles failed")
    except Exception as e:
        print(f"✗ process_video_subtitles error: {e}")
    
    print(f"\nPassed: {passed}/2")
    return passed == 2


def test_config():
    """Test configuration"""
    print("\n" + "="*70)
    print("TEST 5: Configuration")
    print("="*70)
    
    from config import (
        CHUNK_TARGET_WORDS,
        CHUNK_MAX_WORDS,
        CHUNK_OVERLAP_WORDS,
        CHUNK_MIN_FINAL_WORDS,
        OPENAI_MODEL,
        OPENAI_TEMPERATURE
    )
    
    configs = [
        ("CHUNK_TARGET_WORDS", CHUNK_TARGET_WORDS, 1000),
        ("CHUNK_MAX_WORDS", CHUNK_MAX_WORDS, 1500),
        ("CHUNK_OVERLAP_WORDS", CHUNK_OVERLAP_WORDS, 100),
        ("CHUNK_MIN_FINAL_WORDS", CHUNK_MIN_FINAL_WORDS, 500),
        ("OPENAI_MODEL", OPENAI_MODEL, "gpt-4o-mini"),
        ("OPENAI_TEMPERATURE", OPENAI_TEMPERATURE, 0.5),
    ]
    
    passed = 0
    for name, value, expected in configs:
        if value == expected:
            print(f"✓ {name} = {value}")
            passed += 1
        else:
            print(f"✗ {name} = {value} (expected {expected})")
    
    print(f"\nPassed: {passed}/{len(configs)}")
    return passed == len(configs)


def test_database_schema():
    """Test database schema is updated"""
    print("\n" + "="*70)
    print("TEST 6: Database Schema")
    print("="*70)
    
    from db.subtitle_chunks_crud import create_chunk
    import inspect
    
    # Check function signature
    sig = inspect.signature(create_chunk)
    params = list(sig.parameters.keys())
    
    required_params = ['video_id', 'chunk_id', 'chunk_text', 'word_count', 'sentence_count']
    obsolete_params = ['start_time', 'end_time']
    
    passed = 0
    total = len(required_params) + len(obsolete_params)
    
    for param in required_params:
        if param in params:
            print(f"✓ Has parameter: {param}")
            passed += 1
        else:
            print(f"✗ Missing parameter: {param}")
    
    for param in obsolete_params:
        if param not in params:
            print(f"✓ Removed parameter: {param}")
            passed += 1
        else:
            print(f"✗ Still has obsolete parameter: {param}")
    
    print(f"\nPassed: {passed}/{total}")
    return passed == total


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE BACKEND TEST SUITE")
    print("="*70)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("YouTube", test_youtube_module()))
    results.append(("Subtitles", test_subtitles_module()))
    results.append(("Orchestrator", test_orchestrator()))
    results.append(("Config", test_config()))
    results.append(("Database Schema", test_database_schema()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
