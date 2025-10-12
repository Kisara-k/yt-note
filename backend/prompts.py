"""
AI Prompts for chunk enrichment
All prompt templates and related functions
"""

from config import OPENAI_MAX_TOKENS_TITLE, OPENAI_MAX_TOKENS_OTHER


# AI Prompts for chunk enrichment
PROMPTS = {
    'short_title': {
        'label': 'Short Title',
        'max_tokens': OPENAI_MAX_TOKENS_TITLE,
        'template': '''Create a concise title (max 10 words) that captures the main topic of this video segment.

Segment text:
{chunk_text}

Generate only the title, no additional text.'''
    },
    
    'ai_field_1': {
        'label': 'High-Level Summary',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': '''Provide a high-level summary (2-3 sentences) of this video segment.

Segment text:
{chunk_text}

Focus on the main ideas and key takeaways.'''
    },
    
    'ai_field_2': {
        'label': 'Key Points',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': '''List the key points discussed in this video segment as bullet points.

Segment text:
{chunk_text}

Provide 3-5 bullet points, each focusing on a distinct idea or fact mentioned.'''
    },
    
    'ai_field_3': {
        'label': 'Topics/Themes',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': '''Identify the main topics or themes covered in this video segment.

Segment text:
{chunk_text}

Provide a comma-separated list of 3-5 topics or themes.'''
    }
}


def get_prompt(field_name: str, chunk_text: str) -> str:
    """Get formatted prompt for a specific field"""
    if field_name not in PROMPTS:
        raise ValueError(f"Unknown field name: {field_name}")
    return PROMPTS[field_name]['template'].format(chunk_text=chunk_text)


def get_all_prompts() -> dict:
    """Get all prompt templates as a flat dict"""
    return {
        'title': PROMPTS['short_title']['template'],
        'field_1': PROMPTS['ai_field_1']['template'],
        'field_2': PROMPTS['ai_field_2']['template'],
        'field_3': PROMPTS['ai_field_3']['template']
    }


def get_prompt_label(field_name: str) -> str:
    """Get the label for a specific prompt field"""
    if field_name not in PROMPTS:
        return field_name
    return PROMPTS[field_name]['label']


def get_max_tokens(field_name: str) -> int:
    """Get max tokens for a specific prompt field"""
    if field_name not in PROMPTS:
        return OPENAI_MAX_TOKENS_OTHER
    return PROMPTS[field_name]['max_tokens']
