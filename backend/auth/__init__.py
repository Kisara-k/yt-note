"""
Authentication module for YouTube Notes application
Handles Supabase JWT token verification and email validation
"""

from .middleware import get_current_user, get_optional_user
from .config import is_email_verified, hash_email, VERIFIED_EMAIL_HASHES

__all__ = [
    'get_current_user',
    'get_optional_user',
    'is_email_verified',
    'hash_email',
    'VERIFIED_EMAIL_HASHES',
]
