"""
Central configuration file for all settings
"""

# ===================================================
# Chunking Configuration - Word-based (not time-based)
# ===================================================
CHUNK_TARGET_WORDS = 1000      # Target words per chunk (~4-5 minutes of speech)
CHUNK_MAX_WORDS = 1500         # Maximum words per chunk
CHUNK_OVERLAP_WORDS = 100      # Words to overlap between chunks for context
CHUNK_MIN_FINAL_WORDS = 500    # Minimum words for final chunk (otherwise merge with previous)

# ===================================================
# OpenAI Configuration
# ===================================================
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS_TITLE = 50
OPENAI_MAX_TOKENS_OTHER = 500
OPENAI_TEMPERATURE = 0.7

# ===================================================
# Legacy time-based config (deprecated, kept for backward compatibility)
# ===================================================
CHUNK_TARGET_DURATION = 2400.0  # 40 minutes in seconds
CHUNK_MAX_DURATION = 3600.0     # 60 minutes in seconds
