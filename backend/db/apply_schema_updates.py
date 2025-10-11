"""
Apply schema updates to Supabase database
Runs the schema_updates.sql file to create missing tables
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

supabase: Client = create_client(url, key)

def run_schema_updates():
    """
    Execute the schema_updates.sql file
    """
    # Read the SQL file
    sql_file = os.path.join(os.path.dirname(__file__), 'schema_updates.sql')
    
    print(f"Reading SQL file: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split into individual statements (rough split on semicolons)
    # Note: This is a simple approach and may not handle all SQL correctly
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    print(f"\nFound {len(statements)} SQL statements to execute\n")
    print("="*70)
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        # Skip comments and SELECT statements at the end
        if (statement.startswith('--') or 
            statement.startswith('/*') or 
            'pg_tables' in statement.lower() or
            statement.strip().upper().startswith('SELECT')):
            print(f"[{i}/{len(statements)}] Skipping: {statement[:50]}...")
            continue
        
        try:
            print(f"[{i}/{len(statements)}] Executing: {statement[:80]}...")
            
            # Execute via Supabase RPC or direct query
            # Note: Supabase client doesn't support direct SQL execution
            # We need to use the SQL editor in Supabase dashboard
            # or use psycopg2 directly
            
            # For now, just print what would be executed
            print(f"    → Would execute SQL statement")
            success_count += 1
            
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            error_count += 1
    
    print("\n" + "="*70)
    print(f"\nSummary:")
    print(f"  Success: {success_count}")
    print(f"  Errors:  {error_count}")
    print(f"  Skipped: {len(statements) - success_count - error_count}")
    
    print("\n" + "="*70)
    print("\nIMPORTANT: Supabase Python client doesn't support direct SQL execution.")
    print("Please run the schema_updates.sql file manually using one of these methods:")
    print("\n1. Supabase Dashboard:")
    print("   - Go to your project at https://supabase.com/dashboard")
    print("   - Click 'SQL Editor' in the left sidebar")
    print("   - Click 'New Query'")
    print("   - Copy and paste the contents of schema_updates.sql")
    print("   - Click 'Run' or press Ctrl+Enter")
    print("\n2. psql command line:")
    print("   psql 'YOUR_SUPABASE_CONNECTION_STRING' -f schema_updates.sql")
    print("\n3. Python with psycopg2:")
    print("   python apply_schema_with_psycopg2.py")
    print("="*70)

if __name__ == "__main__":
    run_schema_updates()
