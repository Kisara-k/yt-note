"""
Test the new chapter format with 'title' and 'content' fields
"""
import json

# Test Case 1: Valid chapters with title and content
valid_chapters = [
    {
        "title": "Chapter 1: Introduction",
        "content": "This is the introduction content."
    },
    {
        "title": "Chapter 2: Main Content",
        "content": "This is the main content."
    }
]

# Test Case 2: Chapters with extra fields (should be ignored)
chapters_with_extra = [
    {
        "title": "Chapter 1",
        "content": "Content here",
        "author": "John Doe",  # Should be ignored
        "extra_field": "ignored"  # Should be ignored
    }
]

# Test Case 3: Missing title (should fail)
missing_title = [
    {
        "content": "Content without title"
    }
]

# Test Case 4: Missing content (should fail)
missing_content = [
    {
        "title": "Title without content"
    }
]

# Test Case 5: Empty title (should fail)
empty_title = [
    {
        "title": "",
        "content": "Content with empty title"
    }
]

# Test Case 6: Empty content (should fail)
empty_content = [
    {
        "title": "Title",
        "content": ""
    }
]

# Test Case 7: Mixed valid and invalid (should fail)
mixed_chapters = [
    {
        "title": "Chapter 1",
        "content": "Good content"
    },
    {
        "title": "",  # Invalid
        "content": "More content"
    }
]

def validate_chapters(chapters):
    """Validate chapter format"""
    missing_fields = []
    for idx, chapter in enumerate(chapters):
        chapter_num = idx + 1
        if 'title' not in chapter or not chapter.get('title', '').strip():
            missing_fields.append(f"Chapter {chapter_num}: missing or empty 'title'")
        if 'content' not in chapter or not chapter.get('content', '').strip():
            missing_fields.append(f"Chapter {chapter_num}: missing or empty 'content'")
    
    if missing_fields:
        return False, missing_fields
    return True, []

def filter_chapters(chapters):
    """Filter chapters to only include title and content"""
    return [{"title": ch["title"], "content": ch["content"]} for ch in chapters]

# Run tests
print("=" * 60)
print("Testing New Chapter Format Validation")
print("=" * 60)

test_cases = [
    ("Valid chapters", valid_chapters, True),
    ("Chapters with extra fields", chapters_with_extra, True),
    ("Missing title", missing_title, False),
    ("Missing content", missing_content, False),
    ("Empty title", empty_title, False),
    ("Empty content", empty_content, False),
    ("Mixed valid/invalid", mixed_chapters, False),
]

for test_name, chapters, should_pass in test_cases:
    print(f"\n📝 Test: {test_name}")
    print(f"   Input: {json.dumps(chapters, indent=2)[:100]}...")
    
    is_valid, errors = validate_chapters(chapters)
    
    if is_valid == should_pass:
        print(f"   ✅ PASSED")
        if is_valid:
            filtered = filter_chapters(chapters)
            print(f"   Filtered output: {json.dumps(filtered, indent=2)[:100]}...")
    else:
        print(f"   ❌ FAILED")
        if errors:
            print(f"   Errors: {errors}")

print("\n" + "=" * 60)
print("✅ All validation tests completed!")
print("=" * 60)
