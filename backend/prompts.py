"""
AI Prompts for chunk enrichment
All prompt templates and related functions
"""

from config import OPENAI_MAX_TOKENS_TITLE, OPENAI_MAX_TOKENS_OTHER

SYSTEM_PROMPT = """
You are an advanced language model. You are helpful and honest. Your knowledge is current up to **June 2024**.

**Your objectives are:**

- **Help the user effectively.** Provide useful, accurate, and relevant information. Prioritize clarity, precision, and completeness in your answers.
- **Be honest about your limitations.** If you don’t know something or your knowledge is outdated, say so clearly.
- **Follow user instructions.** Adjust your tone, style, and format to match what the user asks, unless it conflicts with truthfulness. When a user requests a specific output format or itemized content, produce that format without adding conversational framing.
- **Be neutral and non-conversational.** Avoid greetings, sign-offs, small talk, rhetorical flourishes, or phrases that frame the response as a conversation (for example: "Certainly!", "Here you go:", "If you'd like more information..."). Deliver content directly in the requested format.
- **Make language clear and approachable.** Prefer phrasing that is easy to read and understand, without being overly formal or rigid. Avoid complex or academic wording when simpler phrasing conveys the same idea.

- **Think step-by-step.** When solving problems, especially involving reasoning, calculations, or coding, break them down into logical steps.
- **Ground your answers.** When possible, cite sources, show reasoning, or explain how you arrived at your conclusions.
- **Avoid hallucination.** Don't make up facts. If uncertain, say so, or provide an informed guess clearly labeled as such (for example: "Estimate:" or "Note:").
  
**You are capable of:**

* Answering complex questions
* Writing and editing code
* Helping with writing, research, and analysis
* Supporting creative and technical tasks
* Parsing and generating images when requested
* Adapting tone and personality for different user needs

**Guidelines:**

* **Avoid third-party framing.**  
  DO NOT refer to “the text,” “the content,” “the creator,” “the author,” “the speaker,” or similar terms. Speak directly and naturally about the ideas themselves.  
  - YES: “This approach improves efficiency.”  
  - NO: “The text explains that this approach improves efficiency.”  
  Treat the information as if it is your own knowledge, not something you are describing from a distance.

* **Use natural, professional language.**  
  Write in a tone that feels direct, clear, and human. Avoid stiffness, bureaucratic phrasing, and unnecessary complexity. Prefer plain words over abstract or academic ones. The goal is to sound like an expert explaining something clearly—not like a research paper or a tutorial transcript.  
  - YES: “This method saves time and keeps you focused.”  
  - NO: “This methodology facilitates efficiency and optimizes concentration.”

* **Write from a first-person, knowledgeable perspective.**  
  Present information as if it comes from your own expertise and understanding, not as a detached summary. If personal context or reasoning is relevant, use first-person voice appropriately.  
  - YES: “From experience, this technique works best when kept simple.”  
  - NO: “According to the text, the author believes this technique works best when kept simple.”  
  Maintain a tone of confidence and clarity, as if you are the originator or explainer of the ideas, not a commentator describing someone else’s work.

* **Prioritize clarity and understandability, not theatrics.**  
  Avoid unnecessary complexity or stylistic embellishments. Every sentence should serve understanding and accuracy.

Always maintain a professional, clear, and objective demeanor. Do not ever include conversational openings or closings.
"""




# ============================================================
# VIDEO PROMPTS - Raw Text Templates
# ============================================================

VIDEO_PROMPT_TITLE = '''Create a concise title (max 10 words) that captures the main topic of this video segment.

Segment text:
{chunk_text}

Generate only the title, no additional text.'''

VIDEO_PROMPT_1 = '''
Extract all the KEY FACTS from the content that are essential to understand, ignoring filler and common knowledge. Use emojis in headings for clarity.

Each fact-topic must be a **single, clear sentence** that summarizes the key point, reading just the fact-topic should give a complete understanding of that piece of information. Then list the supporting bullet points under it. 

Use this format:

### 1. [Emoji] [Fact-Topic sentence summarizing the key point]
- [fact1 supporting the fact-topic]
- [fact2 supporting the fact-topic]

### 2. [Emoji] [Fact-Topic sentence summarizing the key point]
- [fact1]
- [fact2]
- [fact3]

content:
{chunk_text}
'''

VIDEO_PROMPT_2 = '''
Create a clear, structured study note based on the following content. 
Focus on explaining key ideas in a way that’s easy to understand, while keeping the note concise and organized. 
Each main section should begin with a short paragraph (around 3–4 sentences) that introduces and explains the concept in plain language, followed by short lists or key points when useful.

Use EMOJIs in main headings for clarity, and number main headings in this EXACT FORMAT:
## 1. [Emoji] Heading

Guidelines:
- Use between 3–10 main headings as needed.
- Each heading’s introductory paragraph (around 3–4 sentences) should explain the concept clearly and provide enough context for understanding.
- Include only as much supporting detail as needed to understand the concept.
- Avoid filler or over-explaining simple ideas.
- The note should be complete, informative, and understandable, but not overly long.
- Focus on clarity and conceptual understanding above brevity.

content:
{chunk_text}
'''


VIDEO_PROMPT_3 = '''
Write 10 multiple choice questions that comprehensively cover this topic (each question having ONE OR MORE CORRECT answer). DO NOT include the answers here. Make sure to cover all the key concepts and ideas in the content. Each question should be clear and concise. Include TRICKY and DIFFICULT questions. Make sure the answer isn't obvious, and REQUIRE A CLEAR UNDERSTANDING of the content. No need to say like "according to the content", as it is implied. Use the following EXACT FORMAT.

### X. [Question]
A)
B)
C)
D)

After writing all 10 questions, AT THE VERY END, for each question, clearly state the correct choices, and clearly state why each choice is correct or incorrect. Make sure to carefully consider each statement, its relation to the question, and the context of the lecture. Keep explanations brief but specific. Use the following EXACT FORMAT.

### X. [Question]
A) ✓/✗ [Short explanation]  
B) ✓/✗ [Short explanation]  
C) ✓/✗ [Short explanation]  
D) ✓/✗ [Short explanation]

**Correct:** P,Q

content:
{chunk_text}
'''


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
# LECTURE PROMPTS - Raw Text Templates
# ============================================================
# Note: No LECTURE_PROMPT_TITLE - it's not saved to DB (chapter_title already exists)

LECTURE_PROMPT_1 = '''Provide a concise summary (2-3 sentences) of this lecture section.

Lecture section:
{chunk_text}

Focus on the main concepts, explanations, or demonstrations covered.'''

LECTURE_PROMPT_2 = '''Identify and list the important formulas, theorems, definitions, or technical concepts presented in this lecture section.

Lecture section:
{chunk_text}

List 3-5 key technical items as bullet points, with brief explanations where relevant.'''

LECTURE_PROMPT_3 = '''Extract the key learning objectives and important points that students should remember from this lecture section.

Lecture section:
{chunk_text}

Provide 3-5 critical learning points or concepts that are essential to understand.'''

BOOK_PROMPT_1 = VIDEO_PROMPT_1
BOOK_PROMPT_2 = VIDEO_PROMPT_2
BOOK_PROMPT_3 = VIDEO_PROMPT_3

LECTURE_PROMPT_1 = VIDEO_PROMPT_1
LECTURE_PROMPT_2 = VIDEO_PROMPT_2
LECTURE_PROMPT_3 = VIDEO_PROMPT_3


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

# AI Prompts for lecture content enrichment
LECTURE_PROMPTS = {
    'ai_field_1': {
        'label': 'Lecture Summary',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': LECTURE_PROMPT_1
    },
    'ai_field_2': {
        'label': 'Technical Concepts',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': LECTURE_PROMPT_2
    },
    'ai_field_3': {
        'label': 'Learning Objectives',
        'max_tokens': OPENAI_MAX_TOKENS_OTHER,
        'template': LECTURE_PROMPT_3
    }
}


# Legacy reference - defaults to video prompts for backward compatibility
PROMPTS = VIDEO_PROMPTS


def _get_prompt_set(content_type: str) -> dict:
    """
    Get the appropriate prompt set based on content type.
    
    Args:
        content_type: 'video', 'book', 'lecture', or other value
        
    Returns:
        Appropriate prompt dictionary
    """
    if content_type == 'lecture':
        return LECTURE_PROMPTS
    elif content_type == 'book':
        return BOOK_PROMPTS
    else:
        # Default to video prompts for unknown types
        return VIDEO_PROMPTS


def get_prompt(field_name: str, chunk_text: str, content_type: str = 'video') -> str:
    """Get formatted prompt for a specific field
    
    Args:
        field_name: Name of the field (short_title, ai_field_1, ai_field_2, ai_field_3)
        chunk_text: The text content to process
        content_type: 'video', 'book', 'lecture', or other (defaults to video)
    """
    prompts = _get_prompt_set(content_type)
    
    if field_name not in prompts:
        raise ValueError(f"Unknown field name: {field_name}")
    return prompts[field_name]['template'].format(chunk_text=chunk_text)


def get_all_prompts(content_type: str = 'video') -> dict:
    """Get all prompt templates as a flat dict
    
    Args:
        content_type: 'video', 'book', 'lecture', or other (defaults to video)
    
    Returns:
        Dict with keys: title (video only), field_1, field_2, field_3
    """
    prompts = _get_prompt_set(content_type)
    
    result = {
        'field_1': prompts['ai_field_1']['template'],
        'field_2': prompts['ai_field_2']['template'],
        'field_3': prompts['ai_field_3']['template']
    }
    
    # Only include title for videos (books/lectures don't save it)
    if content_type == 'video' and 'short_title' in prompts:
        result['title'] = prompts['short_title']['template']
    
    return result


def get_prompt_label(field_name: str, content_type: str = 'video') -> str:
    """Get the label for a specific prompt field
    
    Args:
        field_name: Name of the field
        content_type: 'video', 'book', 'lecture', or other (defaults to video)
    """
    prompts = _get_prompt_set(content_type)
    
    if field_name not in prompts:
        return field_name
    return prompts[field_name]['label']


def get_max_tokens(field_name: str, content_type: str = 'video') -> int:
    """Get max tokens for a specific prompt field
    
    Args:
        field_name: Name of the field
        content_type: 'video', 'book', 'lecture', or other (defaults to video)
    """
    prompts = _get_prompt_set(content_type)
    
    if field_name not in prompts:
        return OPENAI_MAX_TOKENS_OTHER
    return prompts[field_name]['max_tokens']
