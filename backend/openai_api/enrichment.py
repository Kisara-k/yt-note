"""
OpenAI module - Enrich text chunks with AI-generated fields
Uses openai library v1.0+
"""

import os
import time
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI, RateLimitError
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
    """Enrich a text chunk with AI-generated fields (fields processed in parallel)"""
    
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Create OpenAI client instance (v1.0+ API)
    client = OpenAI(api_key=api_key)
    
    # Define fields to process
    fields = {
        'title': (prompts.get('title', ''), max_tokens_title),
        'field_1': (prompts.get('field_1', ''), max_tokens_other),
        'field_2': (prompts.get('field_2', ''), max_tokens_other),
        'field_3': (prompts.get('field_3', ''), max_tokens_other)
    }
    
    def process_field(field_name, prompt_template, max_tokens):
        """Process a single field with retries"""
        if not prompt_template:
            return field_name, ""
        
        prompt = f"{prompt_template}\n\nText:\n{text}"
        
        retries = 0
        while retries <= max_retries:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return field_name, response.choices[0].message.content.strip()
                
            except RateLimitError as e:
                retries += 1
                if retries <= max_retries:
                    print(f"Rate limit hit for {field_name} - waiting {retry_delay}s (retry {retries}/{max_retries})", flush=True)
                    time.sleep(retry_delay)
                else:
                    return field_name, f"[Rate limit exceeded]"
                    
            except Exception as e:
                print(f"Error enriching {field_name}: {e}", flush=True)
                return field_name, f"[Error: {str(e)}]"
        
        return field_name, ""
    
    # Process all fields in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_field, field_name, prompt_template, max_tokens): field_name
            for field_name, (prompt_template, max_tokens) in fields.items()
        }
        
        for future in as_completed(futures):
            field_name, result = future.result()
            results[field_name] = result
    
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
        print(f"    Processing chunk {idx + 1}/{len(chunks)} with OpenAI...", flush=True)
        result = enrich_chunk(
            text=chunk['text'],
            prompts=prompts,
            model=model,
            temperature=temperature,
            max_tokens_title=max_tokens_title,
            max_tokens_other=max_tokens_other
        )
        print(f"    ✓ Completed chunk {idx + 1}/{len(chunks)}", flush=True)
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
