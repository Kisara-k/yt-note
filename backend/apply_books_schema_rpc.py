"""
Apply books schema using Supabase RPC
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL_2")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY_2")

if not supabase_url or not supabase_key:
    print("ERROR: SUPABASE_URL_2 and SUPABASE_SERVICE_KEY_2 must be set in .env")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 60)
print("APPLYING BOOKS SCHEMA VIA SUPABASE CLIENT")
print("=" * 60)

# Read schema file
schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books_schema.sql")
with open(schema_path, 'r') as f:
    schema_sql = f.read()

print(f"\n1. Schema loaded: {len(schema_sql)} characters")

# Split into individual statements
statements = []
current = []
for line in schema_sql.split('\n'):
    line = line.strip()
    if line and not line.startswith('--'):
        current.append(line)
        if line.endswith(';'):
            statements.append(' '.join(current))
            current = []

print(f"2. Parsed {len(statements)} SQL statements")

# Execute via RPC
print("\n3. Executing SQL statements...")
try:
    for i, stmt in enumerate(statements):
        if stmt.strip():
            try:
                # Use rpc to execute SQL
                supabase.rpc('exec_sql', {'query': stmt}).execute()
                print(f"   ✓ Statement {i+1}/{len(statements)}")
            except Exception as e:
                # If RPC doesn't exist, try postgrest
                if 'does not exist' in str(e).lower():
                    print(f"\n   ⚠ RPC method not available")
                    print("   Schema must be applied manually via SQL Editor")
                    print(f"\n   Go to: {supabase_url.replace('https://', 'https://supabase.com/dashboard/project/')}")
                    print("   Navigate to: SQL Editor > New Query")
                    print("   Paste contents of: books_schema.sql")
                    break
                elif 'already exists' in str(e).lower():
                    print(f"   ↷ Statement {i+1} - already exists")
                else:
                    print(f"   ✗ Statement {i+1} failed: {str(e)[:100]}")
    
    print("\n✓ Schema application attempted")
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    print("\nManual application required - see instructions above")
    sys.exit(1)
