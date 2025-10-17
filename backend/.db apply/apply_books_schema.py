"""
Apply books schema to 2nd Supabase database
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get database credentials
supabase_url = os.getenv("SUPABASE_URL_2")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY_2")  # Use service key for admin operations

if not supabase_url or not supabase_key:
    print("ERROR: SUPABASE_URL_2 and SUPABASE_SERVICE_KEY_2 must be set in .env")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 60)
print("APPLYING BOOKS SCHEMA TO 2ND DATABASE")
print("=" * 60)

# Read the schema file
schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books_schema.sql")

if not os.path.exists(schema_path):
    print(f"ERROR: Schema file not found at {schema_path}")
    sys.exit(1)

with open(schema_path, 'r') as f:
    schema_sql = f.read()

print(f"\n1. Schema file loaded: {schema_path}")
print(f"   Size: {len(schema_sql)} characters")

# Note: The Supabase Python client doesn't support direct SQL execution
# You need to execute this SQL in the Supabase SQL Editor or via psycopg2

print("\n2. MANUAL STEPS REQUIRED:")
print("   Please execute the following SQL in your Supabase SQL Editor:")
print("   " + "-" * 56)
print(f"   Navigate to: {supabase_url.replace('https://', 'https://supabase.com/dashboard/project/')}")
print("   Go to: SQL Editor > New Query")
print("   Copy and paste the contents of books_schema.sql")
print("   Run the query")
print()

# Try to create the storage bucket
print("3. Creating storage bucket...")
try:
    # List existing buckets
    buckets = supabase.storage.list_buckets()
    bucket_names = [b.name for b in buckets]
    
    if "book-chapters" in bucket_names:
        print("   ✓ Bucket 'book-chapters' already exists")
    else:
        # Create bucket
        result = supabase.storage.create_bucket(
            "book-chapters",
            options={"public": False}
        )
        print("   ✓ Bucket 'book-chapters' created successfully")
except Exception as e:
    print(f"   ⚠ Could not create bucket automatically: {str(e)}")
    print("   Please create the bucket manually in Supabase:")
    print("     1. Go to Storage in Supabase dashboard")
    print("     2. Click 'New bucket'")
    print("     3. Name it 'book-chapters'")
    print("     4. Set it to Private")
    print("     5. Click 'Create bucket'")

print("\n" + "=" * 60)
print("SCHEMA APPLICATION COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Execute the SQL schema in Supabase SQL Editor")
print("2. Create the storage bucket if not created automatically")
print("3. Run test_books.py to verify functionality")
