# Email Hash Security Implementation

## Overview

Instead of storing plain email addresses in the codebase, we use SHA-256 hashes for email verification. This provides better security as the actual email addresses are not exposed in the repository.

## How It Works

1. **Hashed Emails in Config** (`backend/auth/config.py`):

   - Contains SHA-256 hashes of verified emails
   - Safe to commit to git (no actual emails visible)
   - This is where the verification happens

2. **Reference File** (`backend/auth/.verified_emails`):
   - Gitignored - NOT committed to repository
   - Maintains email→hash mapping for your convenience
   - Helps you remember which hash corresponds to which email

## Adding a New Verified Email

### Option 1: Using the Management Script (Recommended)

```bash
cd backend/auth
python manage_verified_emails.py
```

Then select option 1 (Add email), and the script will automatically update both `auth/config.py` and `auth/.verified_emails`.

### Option 2: Manual

```bash
# Generate hash
python -c "import hashlib; print(hashlib.sha256('user@example.com'.lower().encode()).hexdigest())"

# Add to backend/auth/config.py VERIFIED_EMAIL_HASHES list
```

### Option 3: Using Python Directly

```bash
cd backend/auth
python -c "import hashlib; email='user@example.com'; print(f'Hash: {hashlib.sha256(email.lower().encode()).hexdigest()}')"
```

## Example

For email: `admin@example.com`

**Hash (stored in auth/config.py):**

```python
VERIFIED_EMAIL_HASHES = [
    "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
]
```

**Reference file (auth/.verified_emails - gitignored):**

```json
{
  "emails": {
    "admin@example.com": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
  }
}
```

## Security Benefits

✅ **No emails in git history** - Only hashes are committed  
✅ **One-way function** - Cannot derive email from hash  
✅ **Safe to share** - Repository can be public without exposing user emails  
✅ **Easy verification** - Backend simply compares hash of login email with stored hashes

## Files

- `backend/auth/config.py` - Contains `VERIFIED_EMAIL_HASHES` list (commit this)
- `backend/auth/.verified_emails` - Reference mapping (gitignored, local only)
- `backend/auth/middleware.py` - JWT verification and email hash checking
- `backend/auth/manage_verified_emails.py` - Helper script to manage emails
- `.gitignore` - Ensures `backend/auth/.verified_emails` is not committed

## Important Notes

⚠️ **The auth/.verified_emails file is only for reference!**  
The actual verification happens against `VERIFIED_EMAIL_HASHES` in `backend/auth/config.py`.

⚠️ **Always update both files (or use the script):**

1. Add hash to `backend/auth/config.py` VERIFIED_EMAIL_HASHES
2. Add email→hash mapping to `backend/auth/.verified_emails` for your reference

⚠️ **Commit config.py, not .verified_emails:**

- `backend/auth/config.py` (with hashes) → Commit to git ✅
- `backend/auth/.verified_emails` (with emails) → Keep local only ❌
