"""
Apply schema update to add note_content to subtitle_chunks
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def apply_schema():
    """Apply the schema update using Supabase SQL query"""
    try:
        # Read the SQL file
        sql_file = os.path.join(os.path.dirname(__file__), 'add_chunk_notes.sql')
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        print("Applying schema update...")
        print(sql)
        
        # Execute the SQL using Supabase RPC
        result = supabase.rpc('exec_sql', {'query': sql}).execute()
        
        print("✓ Schema updated successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error applying schema: {str(e)}")
        # Try alternative method - direct query
        try:
            print("\nTrying alternative method...")
            # For Supabase, we can just verify the column exists by trying to select it
            test = supabase.table('subtitle_chunks').select('note_content').limit(1).execute()
            print("✓ Column note_content already exists or was added successfully!")
            return True
        except Exception as e2:
            print(f"✗ Column does not exist yet. Error: {str(e2)}")
            print("\nPlease run this SQL manually in Supabase SQL Editor:")
            print("-" * 60)
            with open(sql_file, 'r') as f:
                print(f.read())
            print("-" * 60)
            return False

if __name__ == "__main__":
    apply_schema()
