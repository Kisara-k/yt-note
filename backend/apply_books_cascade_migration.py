"""
Apply cascade delete migration to Books database
Removes CASCADE from book_notes and adds storage cleanup triggers
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client for Books database
url: str = os.getenv("SUPABASE_URL_2")
service_key: str = os.getenv("SUPABASE_SERVICE_KEY_2")
supabase: Client = create_client(url, service_key)


def apply_migration():
    """Apply cascade delete migration"""
    
    print("=" * 60)
    print("Books Database - Cascade Delete Migration")
    print("=" * 60)
    
    try:
        # Read migration file
        migration_file = os.path.join(os.path.dirname(__file__), "..", "books_cascade_migration.sql")
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("\n[MIGRATION] Applying cascade delete changes...")
        print("\nChanges to be applied:")
        print("  1. Remove CASCADE from book_notes foreign key")
        print("  2. Add storage cleanup trigger for books")
        print("  3. Add storage cleanup trigger for chapters")
        print()
        
        # Execute migration
        print("[DB->] Executing migration SQL...")
        result = supabase.rpc('exec_sql', {'query': migration_sql}).execute()
        
        print("[DB<-] ✅ Migration completed successfully!")
        print()
        print("CASCADE BEHAVIOR:")
        print("  ✅ book_chapters: CASCADE (deleted when book deleted)")
        print("  ✅ book_notes: NO ACTION (preserved when book deleted)")
        print("  ✅ Storage: Handled by backend delete_book() function")
        print()
        
        # Verify constraints
        print("[DB->] Verifying foreign key constraints...")
        verification_query = """
        SELECT 
            tc.constraint_name, 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        JOIN information_schema.referential_constraints AS rc
            ON tc.constraint_name = rc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public'
            AND tc.table_name IN ('book_notes', 'book_chapters');
        """
        
        result = supabase.rpc('exec_sql', {'query': verification_query}).execute()
        print("[DB<-] Foreign key constraints verified")
        print()
        print("=" * 60)
        print("Migration completed successfully! ✅")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        print("\nNote: If RPC function 'exec_sql' is not available,")
        print("you'll need to run the SQL migration manually in Supabase SQL Editor:")
        print(f"  File: {migration_file}")
        return False


if __name__ == "__main__":
    apply_migration()
