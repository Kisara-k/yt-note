"""
Central configuration file for all settings
"""

# ===================================================
# Chunking Configuration
# ===================================================
# Choose chunking method: True for duration-based, False for word-based
USE_DURATION_CHUNKING = False

# Word-based chunking settings
CHUNK_TARGET_WORDS = 8000      # Target words per chunk (~40 minutes of speech)
CHUNK_MAX_WORDS = 9000         # Maximum words per chunk
CHUNK_OVERLAP_WORDS = 100      # Words to overlap between chunks for context
CHUNK_MIN_FINAL_WORDS = 3000    # Minimum words for final chunk (otherwise merge with previous)

# Duration-based chunking settings (in seconds)
CHUNK_TARGET_DURATION = 2400   # Target duration per chunk (40 minutes)
CHUNK_MAX_DURATION = 2700      # Maximum duration per chunk (45 minutes)
CHUNK_OVERLAP_DURATION = 60    # Overlap duration between chunks (1 minute)
CHUNK_MIN_FINAL_DURATION = 1200  # Minimum duration for final chunk (20 minutes)

# ===================================================
# OpenAI Configuration
# ===================================================
OPENAI_MODEL = "gpt-4.1-nano"
OPENAI_MAX_TOKENS_TITLE = 50
OPENAI_MAX_TOKENS_OTHER = 200
OPENAI_TEMPERATURE = 0.5

