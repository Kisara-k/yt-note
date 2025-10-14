"""
Test book prompts to verify they're different from video prompts
"""

from prompts import get_all_prompts, get_prompt_label

def test_book_prompts():
    """Test that book prompts are different from video prompts"""
    
    print("\n" + "="*70)
    print("TESTING BOOK VS VIDEO PROMPTS")
    print("="*70 + "\n")
    
    # Get video prompts
    video_prompts = get_all_prompts(content_type='video')
    print("VIDEO PROMPTS:")
    print("-" * 70)
    for key, template in video_prompts.items():
        label = get_prompt_label(key.replace('title', 'short_title'), content_type='video')
        print(f"\n{key} ({label}):")
        print(template[:150] + "..." if len(template) > 150 else template)
    
    print("\n" + "="*70 + "\n")
    
    # Get book prompts
    book_prompts = get_all_prompts(content_type='book')
    print("BOOK PROMPTS:")
    print("-" * 70)
    for key, template in book_prompts.items():
        label = get_prompt_label(key.replace('title', 'short_title'), content_type='book')
        print(f"\n{key} ({label}):")
        print(template[:150] + "..." if len(template) > 150 else template)
    
    print("\n" + "="*70)
    print("VERIFICATION:")
    print("-" * 70)
    
    # Verify they're different
    all_different = True
    for key in video_prompts.keys():
        if video_prompts[key] == book_prompts[key]:
            print(f"❌ {key}: Video and book prompts are IDENTICAL (should be different)")
            all_different = False
        else:
            print(f"✓ {key}: Video and book prompts are DIFFERENT")
    
    print("="*70 + "\n")
    
    if all_different:
        print("✓ SUCCESS: All book prompts are different from video prompts")
        return True
    else:
        print("❌ FAILED: Some prompts are identical")
        return False


if __name__ == "__main__":
    success = test_book_prompts()
    exit(0 if success else 1)
