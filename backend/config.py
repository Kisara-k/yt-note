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

CHUNK_STEP_MINUTES = 40
CHUNK_OVERLAP_MINUTES = 1
CHUNK_MIN_DURATION_MINUTES = 20

# ===================================================
# OpenAI Configuration
# ===================================================
OPENAI_MODEL = "gpt-4.1-mini"
OPENAI_MAX_TOKENS_TITLE = 50
OPENAI_MAX_TOKENS_OTHER = 5000
OPENAI_TEMPERATURE = 0.3
OPENAI_TOP_P = 0.3

