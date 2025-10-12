"""
Central configuration file for all settings
"""

# ===================================================
# Chunking Configuration - Word-based (not time-based)
# ===================================================
CHUNK_TARGET_WORDS = 8000      # Target words per chunk (~40 minutes of speech)
CHUNK_MAX_WORDS = 9000         # Maximum words per chunk
CHUNK_OVERLAP_WORDS = 100      # Words to overlap between chunks for context
CHUNK_MIN_FINAL_WORDS = 3000    # Minimum words for final chunk (otherwise merge with previous)

# ===================================================
# OpenAI Configuration
# ===================================================
OPENAI_MODEL = "gpt-4.1-nano"
OPENAI_MAX_TOKENS_TITLE = 50
OPENAI_MAX_TOKENS_OTHER = 200
OPENAI_TEMPERATURE = 0.5

