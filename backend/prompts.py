"""
AI Prompts for chunk enrichment
All prompt templates and related functions
"""

from config import OPENAI_MAX_TOKENS_TITLE, OPENAI_MAX_TOKENS_OTHER


# ============================================================
# VIDEO PROMPTS - Raw Text Templates
# ============================================================

VIDEO_PROMPT_TITLE = '''Create a concise title (max 10 words) that captures the main topic of this video segment.

Segment text:
{chunk_text}

Generate only the title, no additional text.'''

VIDEO_PROMPT_1 = '''Provide a high-level summary (2-3 sentences) of this video segment.

Segment text:
{chunk_text}

Focus on the main ideas and key takeaways.'''

VIDEO_PROMPT_2 = '''List the key points discussed in this video segment as bullet points.

Segment text:
{chunk_text}

Provide 3-5 bullet points, each focusing on a distinct idea or fact mentioned.'''

VIDEO_PROMPT_3 = '''Identify the main topics or themes covered in this video segment.

Segment text:
{chunk_text}

Provide a comma-separated list of 3-5 topics or themes.'''


# ============================================================
# BOOK PROMPTS - Raw Text Templates
# ============================================================
# Note: No BOOK_PROMPT_TITLE - it's not saved to DB (chapter_title already exists)

BOOK_PROMPT_1 = '''Provide a comprehensive summary (2-3 sentences) of this book chapter section.

Chapter section:
{chunk_text}

Focus on the main concepts, arguments, or narrative developments presented.'''

BOOK_PROMPT_2 = '''Identify and explain the important concepts, definitions, or ideas in this book chapter section.

Chapter section:
{chunk_text}

List 3-5 key concepts as bullet points, with brief explanations where relevant.'''

BOOK_PROMPT_3 = '''Extract the key insights, lessons, or takeaways from this book chapter section.

Chapter section:
{chunk_text}

Provide 3-5 actionable insights or important lessons that a reader should remember.'''


# ============================================================
# Structured Prompt Configurations
# ============================================================

# AI Prompts for video chunk enrichment
VIDEO_PROMPTS = {
    'short_title': {
        'label': 'Short Title',
        'max_tokens': OPENAI_MAX_TOKENS_TITLE,
        'template': VIDEO_PROMPT_TITLE
    },
    'ai_field_1': {
        'label': 'High-Level Summary',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': VIDEO_PROMPT_1
    },
    'ai_field_2': {
        'label': 'Key Points',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': VIDEO_PROMPT_2
    },
    'ai_field_3': {
        'label': 'Topics/Themes',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': VIDEO_PROMPT_3
    }
}

# AI Prompts for book chapter enrichment
BOOK_PROMPTS = {
    'ai_field_1': {
        'label': 'Chapter Summary',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': BOOK_PROMPT_1
    },
    'ai_field_2': {
        'label': 'Important Concepts',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': BOOK_PROMPT_2
    },
    'ai_field_3': {
        'label': 'Key Insights',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': BOOK_PROMPT_3
    }
}


# Legacy reference - defaults to video prompts for backward compatibility
PROMPTS = VIDEO_PROMPTS


def get_prompt(field_name: str, chunk_text: str, content_type: str = 'video') -> str:
    """Get formatted prompt for a specific field
    
    Args:
        field_name: Name of the field (short_title, ai_field_1, ai_field_2, ai_field_3)
        chunk_text: The text content to process
        content_type: Either 'video' or 'book' to determine which prompt set to use
    """
    prompts = BOOK_PROMPTS if content_type == 'book' else VIDEO_PROMPTS
    
    if field_name not in prompts:
        raise ValueError(f"Unknown field name: {field_name}")
    return prompts[field_name]['template'].format(chunk_text=chunk_text)


def get_all_prompts(content_type: str = 'video') -> dict:
    """Get all prompt templates as a flat dict
    
    Args:
        content_type: Either 'video' or 'book' to determine which prompt set to use
    
    Returns:
        Dict with keys: title (video only), field_1, field_2, field_3
    """
    prompts = BOOK_PROMPTS if content_type == 'book' else VIDEO_PROMPTS
    
    result = {
        'field_1': prompts['ai_field_1']['template'],
        'field_2': prompts['ai_field_2']['template'],
        'field_3': prompts['ai_field_3']['template']
    }
    
    # Only include title for videos (books don't save it)
    if content_type == 'video' and 'short_title' in prompts:
        result['title'] = prompts['short_title']['template']
    
    return result


def get_prompt_label(field_name: str, content_type: str = 'video') -> str:
    """Get the label for a specific prompt field
    
    Args:
        field_name: Name of the field
        content_type: Either 'video' or 'book' to determine which prompt set to use
    """
    prompts = BOOK_PROMPTS if content_type == 'book' else VIDEO_PROMPTS
    
    if field_name not in prompts:
        return field_name
    return prompts[field_name]['label']


def get_max_tokens(field_name: str, content_type: str = 'video') -> int:
    """Get max tokens for a specific prompt field
    
    Args:
        field_name: Name of the field
        content_type: Either 'video' or 'book' to determine which prompt set to use
    """
    prompts = BOOK_PROMPTS if content_type == 'book' else VIDEO_PROMPTS
    
    if field_name not in prompts:
        return OPENAI_MAX_TOKENS_OTHER
    return prompts[field_name]['max_tokens']
