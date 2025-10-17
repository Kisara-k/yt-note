"""
AI Response Filter Module

This module provides a centralized function to filter and process all AI-generated
responses for AI fields before they are stored or returned to the frontend.
"""

from typing import Optional
import re

def remove_unwanted_lines(text):

    # If chatgpt starts with a conversational message, Remove first and last line
    if not text.strip().startswith("#"):
        lines = text.split('\n')
        if len(lines) > 2:
            lines = lines[1:-1]
        text = '\n'.join(lines)

    # Remove lines that contain '# Study Note'
    lines = text.split('\n')
    lines = [line for line in lines if '# Study Note' not in line]
    text = '\n'.join(lines)

    return text

def replace_text(text):
    text = re.sub(r'[ ]*\\\[', r'\n$$', text)
    text = re.sub(r'[ ]*\\\]', r'$$\n', text)
    text = re.sub(r'\\\( ?| ?\\\)', '$', text)
    return text

def clean(text):
    text = remove_unwanted_lines(text)
    text = replace_text(text)
    # if text.startswith('#'):
    #     text = '#' + text
    # if text.startswith('## '):
    #     text = '#' + text
    # text = text.replace('\n#', '\n##').replace('\n## ', '\n### ')
    return text.replace('\n---\n', '\n').replace('—', ' - ').strip()

def filter_ai_response(response: str, field_name: Optional[str] = None) -> str:
    """
    Central filter function for all AI-generated text responses.
    
    This function processes AI-generated text (either from OpenAI API or user input)
    before it is stored in the database. All AI field updates pass through this
    function to ensure consistent processing and validation.
    
    Args:
        response: The raw AI response text to filter (string)
        field_name: Optional name of the field being updated. Valid values:
                   - 'title' (for video chunks only)
                   - 'field_1' (summary/key points/etc.)
                   - 'field_2' (additional analysis)
                   - 'field_3' (additional analysis)
    
    Returns:
        The filtered/processed response string
    
    Examples:
        >>> filter_ai_response("  AI generated text  ", field_name="title")
        "  AI generated text  "
        
        >>> filter_ai_response("Summary text", field_name="field_1")
        "Summary text"
    """
    # TODO: Implement filtering logic
    # Placeholder implementation - currently returns response as-is
    # Future enhancements could include:
    # - Strip excessive whitespace
    # - Remove special characters or formatting
    # - Length validation (max length per field)
    # - Content sanitization (remove harmful content)
    # - Profanity filtering
    # - HTML/markdown cleaning or normalization
    # - Field-specific transformations:
    #   * 'title' might have stricter length limits
    #   * 'field_1/2/3' might allow more formatting
    # - Error handling for malformed responses
    # - Logging for audit trails
    
    # For now, just return the string as-is
    return clean(response)
