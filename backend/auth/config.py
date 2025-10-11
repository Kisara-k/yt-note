"""
Authentication Configuration
Stores SHA-256 hashes of verified emails that are allowed to access the application

Security Note:
- Only hashes are stored in this file (safe to commit to git)
- Use manage_verified_emails.py to generate hashes and maintain the reference file
- The .verified_emails file (gitignored) contains email->hash mapping for reference only
"""

import hashlib

# SHA-256 hashes of verified emails
# To add a new email hash:
#   1. Run: python manage_verified_emails.py
#   2. Use option 4 to generate hash for your email
#   3. Add the hash below
# Or use: python -c "import hashlib; print(hashlib.sha256('your@email.com'.lower().encode()).hexdigest())"
VERIFIED_EMAIL_HASHES = [
    # Add your email hashes here
    "4522e3c5008e3f5b1709cf0d4c229ddc0231c7e2cb368d3e68c4ae6170e1f434",
]

def hash_email(email: str) -> str:
    """
    Generate SHA-256 hash of an email address
    
    Args:
        email: Email address to hash
        
    Returns:
        SHA-256 hash of the lowercase email
    """
    return hashlib.sha256(email.lower().encode()).hexdigest()


def is_email_verified(email: str) -> bool:
    """
    Check if an email is in the verified list (by comparing hashes)
    
    Args:
        email: Email address to check
        
    Returns:
        True if email is verified, False otherwise
    """
    email_hash = hash_email(email)
    return email_hash in VERIFIED_EMAIL_HASHES
