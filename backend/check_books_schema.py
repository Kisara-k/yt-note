"""
Create tables directly using Supabase client
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL_2")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY_2")

if not supabase_url or not supabase_key:
    print("ERROR: SUPABASE_URL_2 and SUPABASE_SERVICE_KEY_2 must be set")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 60)
print("TESTING DATABASE CONNECTION")
print("=" * 60)

# Try to check if tables exist by querying
try:
    print("\n1. Checking for 'books' table...")
    result = supabase.table("books").select("*").limit(1).execute()
    print("   ✓ 'books' table exists!")
    print(f"   Found {len(result.data)} rows")
    tables_exist = True
except Exception as e:
    if 'does not exist' in str(e).lower() or 'relation' in str(e).lower():
        print("   ✗ 'books' table does not exist")
        tables_exist = False
    else:
        print(f"   ✗ Error: {str(e)}")
        tables_exist = False

if not tables_exist:
    print("\n" + "=" * 60)
    print("SCHEMA NOT APPLIED")
    print("=" * 60)
    print("\nPlease apply the schema manually:")
    print(f"1. Go to: {supabase_url.replace('https://', 'https://supabase.com/dashboard/project/')}")
    print("2. Navigate to: SQL Editor > New Query")
    print("3. Copy contents of: books_schema.sql")
    print("4. Run the query")
    print("\nThen run this script again or run: python test_books.py")
    sys.exit(1)
else:
    print("\n" + "=" * 60)
    print("SCHEMA ALREADY APPLIED ✓")
    print("=" * 60)
    print("\nYou can now run: python test_books.py")
