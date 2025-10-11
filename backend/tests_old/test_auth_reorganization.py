"""
Quick test to verify auth module reorganization works
"""
import os
from dotenv import load_dotenv

# Load .env first
load_dotenv()

print("✅ Testing auth module imports...")

# Test 1: Import auth module
try:
    from auth import get_current_user, is_email_verified
    from auth.config import VERIFIED_EMAIL_HASHES
    print("✅ Auth module imports successful")
    print(f"   - Found {len(VERIFIED_EMAIL_HASHES)} verified email hash(es)")
except Exception as e:
    print(f"❌ Auth module import failed: {e}")
    exit(1)

# Test 2: Test email verification function
try:
    test_email = "admin@gmail.com"
    is_verified = is_email_verified(test_email)
    print(f"✅ Email verification function works")
    print(f"   - {test_email} is {'verified' if is_verified else 'not verified'}")
except Exception as e:
    print(f"❌ Email verification test failed: {e}")
    exit(1)

# Test 3: Check Supabase env vars
try:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    
    if url and key and jwt_secret:
        print("✅ Supabase environment variables loaded")
    else:
        print("❌ Missing Supabase environment variables")
        exit(1)
except Exception as e:
    print(f"❌ Environment variable check failed: {e}")
    exit(1)

print("\n🎉 All auth module tests passed!")
print("   Auth files successfully reorganized into backend/auth/")
