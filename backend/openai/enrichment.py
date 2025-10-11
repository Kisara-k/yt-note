"""
OpenAI module - Enrich text chunks with AI-generated fields
Uses openai library (not SDK)
"""

import os
import time
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def enrich_chunk(
    text: str,
    prompts: Dict[str, str],
    model: str = "gpt-4o-mini",
    temperature: float = 0.5,
    max_tokens_title: int = 50,
    max_tokens_other: int = 200,
    max_retries: int = 3,
    retry_delay: int = 5
) -> Dict[str, str]:
    """Enrich a text chunk with AI-generated fields"""
    
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    openai.api_key = api_key
    results = {}
    
    # Process each field
    fields = {
        'title': (prompts.get('title', ''), max_tokens_title),
        'field_1': (prompts.get('field_1', ''), max_tokens_other),
        'field_2': (prompts.get('field_2', ''), max_tokens_other),
        'field_3': (prompts.get('field_3', ''), max_tokens_other)
    }
    
    for field_name, (prompt_template, max_tokens) in fields.items():
        if not prompt_template:
            results[field_name] = ""
            continue
        
        prompt = f"{prompt_template}\n\nText:\n{text}"
        
        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                results[field_name] = response.choices[0].message.content.strip()
                break
                
            except openai.error.RateLimitError:
                if attempt < max_retries - 1:
                    print(f"Rate limit hit, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    results[field_name] = f"[Rate limit exceeded]"
            except Exception as e:
                print(f"Error enriching {field_name}: {e}")
                results[field_name] = f"[Error: {str(e)}]"
                break
    
    return results


def enrich_chunks_parallel(
    chunks: list,
    prompts: Dict[str, str],
    model: str = "gpt-4o-mini",
    temperature: float = 0.5,
    max_tokens_title: int = 50,
    max_tokens_other: int = 200,
    max_workers: int = 5
) -> list:
    """Enrich multiple chunks in parallel using ThreadPoolExecutor"""
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def process_chunk(idx, chunk):
        result = enrich_chunk(
            text=chunk['text'],
            prompts=prompts,
            model=model,
            temperature=temperature,
            max_tokens_title=max_tokens_title,
            max_tokens_other=max_tokens_other
        )
        return idx, {**chunk, **result}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_chunk, i, chunk): i 
            for i, chunk in enumerate(chunks)
        }
        
        results_dict = {}
        for future in as_completed(futures):
            idx, enriched = future.result()
            results_dict[idx] = enriched
        
        # Return in original order
        return [results_dict[i] for i in range(len(chunks))]
