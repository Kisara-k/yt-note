"""
Apply the book type migration to the database
Adds a 'type' field to the books table
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply the migration to add type field to books table"""
    
    # Initialize Supabase client for 2nd database - use SERVICE key for admin operations
    url: str = os.getenv("SUPABASE_URL_2")
    key: str = os.getenv("SUPABASE_SERVICE_KEY_2")
    
    if not url or not key:
        print("Error: Missing SUPABASE_URL_2 or SUPABASE_SERVICE_KEY_2")
        print("Please ensure these are set in your .env file")
        return False
        
    supabase: Client = create_client(url, key)
    
    print("=" * 70)
    print("Applying Book Type Migration")
    print("=" * 70)
    print()
    
    # Read the migration SQL
    migration_file = "add_book_type_migration.sql"
    
    if not os.path.exists(migration_file):
        print(f"Error: Migration file '{migration_file}' not found")
        return False
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    print(f"Read migration from {migration_file}")
    print()
    print("Migration SQL:")
    print("-" * 70)
    print(migration_sql)
    print("-" * 70)
    print()
    
    # Ask for confirmation
    response = input("Apply this migration? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Migration cancelled")
        return False
    
    print()
    print("Applying migration...")
    
    try:
        # Execute the migration using Supabase RPC
        # Note: Supabase doesn't have a direct SQL execution method in the Python client
        # We'll need to execute each statement separately
        
        statements = [
            """
            ALTER TABLE books 
            ADD COLUMN IF NOT EXISTS type VARCHAR(50) DEFAULT 'book'
            """,
            """
            UPDATE books SET type = 'book' WHERE type IS NULL
            """
        ]
        
        for i, statement in enumerate(statements, 1):
            print(f"Executing statement {i}/{len(statements)}...")
            result = supabase.rpc('exec_sql', {'query': statement}).execute()
            print(f"  ✓ Statement {i} completed")
        
        print()
        print("=" * 70)
        print("Migration applied successfully!")
        print("=" * 70)
        print()
        print("The 'type' field has been added to the books table.")
        print("Default value: 'book'")
        print("All existing books have been set to type 'book'")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 70)
        print("Migration failed!")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        print("You may need to apply this migration manually using the Supabase SQL editor.")
        print(f"Use the SQL from: {migration_file}")
        return False


if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
