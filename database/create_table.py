"""
Create the notes table directly using psycopg2
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string
# Using the session pooler (supports both IPv4 and IPv6)
DB_HOST = "aws-1-us-east-1.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.nkuzhhpjdahuiuysemzg"
DB_PASSWORD = os.getenv("DB_PASSWORD")  # Add this to your .env file

# SQL to create the notes table
create_table_sql = """
-- Create the notes table
CREATE TABLE IF NOT EXISTS notes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Allow all operations for testing" ON notes;

-- Allow all operations (for testing purposes)
CREATE POLICY "Allow all operations for testing" ON notes
FOR ALL 
USING (true)
WITH CHECK (true);
"""

def create_table():
    """Create the notes table using direct database connection"""
    conn = None
    try:
        print("� Connecting to Supabase database...")
        
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        print("🔨 Creating 'notes' table...")
        
        # Execute the SQL
        cursor.execute(create_table_sql)
        
        # Commit the changes
        conn.commit()
        
        print("✅ Table 'notes' created successfully!")
        print("✅ Row Level Security enabled")
        print("✅ Policies configured")
        print("\n🎉 You can now run: python db_crud.py")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure to add DB_PASSWORD to your .env file:")
        print("   DB_PASSWORD=your_database_password")
        return False
        
    finally:
        if conn:
            conn.close()
            print("\n🔌 Connection closed")

if __name__ == "__main__":
    create_table()
