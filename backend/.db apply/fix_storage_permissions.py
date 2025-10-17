"""
Fix storage bucket permissions for book-chapters
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL_2")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY_2")

if not supabase_url or not supabase_key:
    print("ERROR: Missing environment variables")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 60)
print("FIXING STORAGE BUCKET PERMISSIONS")
print("=" * 60)

# Check if bucket exists
print("\n1. Checking bucket...")
try:
    buckets = supabase.storage.list_buckets()
    bucket_names = [b.name for b in buckets]
    
    if 'book-chapters' in bucket_names:
        print("   ✓ Bucket 'book-chapters' exists")
    else:
        print("   Creating bucket...")
        supabase.storage.create_bucket('book-chapters', options={'public': False})
        print("   ✓ Bucket created")
except Exception as e:
    print(f"   Error: {str(e)}")

# Try to upload a test file
print("\n2. Testing upload with service key...")
try:
    test_content = "Test content"
    result = supabase.storage.from_('book-chapters').upload(
        'test/test.txt',
        test_content.encode('utf-8'),
        file_options={'content-type': 'text/plain', 'upsert': 'true'}
    )
    print("   ✓ Upload successful!")
    
    # Clean up
    supabase.storage.from_('book-chapters').remove(['test/test.txt'])
    print("   ✓ Cleanup successful")
    print("\n✓ Storage bucket is working correctly!")
    
except Exception as e:
    error_msg = str(e)
    print(f"   ✗ Upload failed: {error_msg}")
    
    if 'row-level security' in error_msg.lower() or 'rls' in error_msg.lower():
        print("\n" + "=" * 60)
        print("RLS POLICY ISSUE DETECTED")
        print("=" * 60)
        print("\nTo fix this, run in Supabase SQL Editor (2nd database):")
        print("\n-- Disable RLS for book-chapters bucket")
        print("ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;")
        print("\n-- Or create a permissive policy:")
        print("CREATE POLICY 'Allow all operations' ON storage.objects FOR ALL USING (bucket_id = 'book-chapters');")
        print("\n-- Or make bucket public:")
        print("UPDATE storage.buckets SET public = true WHERE name = 'book-chapters';")
    
    sys.exit(1)
