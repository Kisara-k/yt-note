"""
OpenAI integration for chunk enrichment with rate limit retry
"""

import os
import sys
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from prompts_config import (
    get_prompt, PROMPTS, OPENAI_MODEL, 
    OPENAI_TEMPERATURE, get_max_tokens
)

try:
    from openai import OpenAI, RateLimitError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI SDK not installed. Run: pip install openai")


class ChunkEnricher:
    
    def __init__(self, model: str = None):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model or OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI SDK not installed. Run: pip install openai")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def call_openai(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = None,
        max_retries: int = 5,
        initial_wait: float = 1.0
    ) -> Optional[str]:
        if temperature is None:
            temperature = OPENAI_TEMPERATURE
        
        for attempt in range(max_retries):
            try:
                print(f"[AI->] model={self.model}, max_tokens={max_tokens}, temp={temperature}, prompt_len={len(prompt)} chars")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that analyzes video transcripts and provides concise, accurate summaries."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                result = response.choices[0].message.content.strip()
                print(f"[AI<-] tokens_used={response.usage.total_tokens}, response_len={len(result)} chars")
                
                return result
                
            except RateLimitError as e:
                wait_time = initial_wait * (2 ** attempt)  # Exponential backoff
                print(f"[AI!!] Rate limit hit (attempt {attempt + 1}/{max_retries}), waiting {wait_time:.1f}s...")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    print(f"[AI!!] Max retries reached: {str(e)}")
                    return None
                    
            except Exception as e:
                print(f"[AI!!] {str(e)}")
                return None
        
        return None
    
    def generate_field(self, field_name: str, chunk_text: str) -> Optional[str]:
        try:
            prompt = get_prompt(field_name, chunk_text)
            max_tokens = get_max_tokens(field_name)
            
            print(f"  -> Generating {field_name}...")
            result = self.call_openai(prompt, max_tokens=max_tokens)
            
            if result:
                print(f"  <- Generated {field_name}: {len(result)} chars")
                return result
            else:
                print(f"  !! Failed to generate {field_name}")
                return None
                
        except Exception as e:
            print(f"  !! Error generating {field_name}: {str(e)}")
            return None
    
    def enrich_chunk(self, chunk_text: str) -> Dict[str, Optional[str]]:
        print(f"\n=== Enriching chunk ({len(chunk_text)} characters) ===")
        
        results = {
            'short_title': self.generate_field('short_title', chunk_text),
            'ai_field_1': self.generate_field('ai_field_1', chunk_text),
            'ai_field_2': self.generate_field('ai_field_2', chunk_text),
            'ai_field_3': self.generate_field('ai_field_3', chunk_text)
        }
        
        successful = sum(1 for v in results.values() if v is not None)
        print(f"=== Enrichment complete: {successful}/4 fields generated ===\n")
        
        return results


def enrich_chunk_with_ai(chunk_text: str, model: str = None) -> Dict[str, Optional[str]]:
    enricher = ChunkEnricher(model=model)
    return enricher.enrich_chunk(chunk_text)


if __name__ == "__main__":
    # Test enrichment with sample text
    sample_text = """
    Today we're going to talk about Python programming and how to write clean code.
    First, let's discuss the importance of following PEP 8 style guidelines.
    These guidelines help maintain code readability and consistency across projects.
    We'll also cover best practices for naming variables, writing functions, and
    organizing your code into modules.
    """
    
    print("="*70)
    print("Testing Chunk Enrichment")
    print("="*70)
    
    try:
        result = enrich_chunk_with_ai(sample_text)
        
        print("\n" + "="*70)
        print("Results:")
        print("="*70)
        
        for field_name, content in result.items():
            label = PROMPTS.get(field_name, {}).get('label', field_name)
            print(f"\n{label}:")
            print(f"{content if content else '(failed)'}")
            print("-"*70)
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
