"""
Apply books schema to 2nd Supabase database using psycopg2
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials
supabase_url = os.getenv("SUPABASE_URL_2")
db_password = os.getenv("DB_PASSWORD")

if not supabase_url or not db_password:
    print("ERROR: SUPABASE_URL_2 and DB_PASSWORD must be set in .env")
    sys.exit(1)

# Extract project ref from URL
project_ref = supabase_url.split("//")[1].split(".")[0]

# Build connection string - try different regions/hosts
# The connection details can be found in: Project Settings > Database > Connection String
possible_hosts = [
    f"aws-0-us-east-1.pooler.supabase.com",
    f"aws-0-us-west-1.pooler.supabase.com",
    f"db.{project_ref}.supabase.co",
]

print(f"\nProject ref: {project_ref}")
print("Trying different connection hosts...")

conn = None
for host in possible_hosts:
    conn_string = f"postgresql://postgres.{project_ref}:{db_password}@{host}:6543/postgres"
    print(f"\nTrying: {host}...")
    try:
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        print(f"   ✓ Connected successfully!")
        break
    except Exception as e:
        print(f"   ✗ Failed: {str(e).split(':')[0]}")
        continue

if not conn:
    print("\n✗ ERROR: Could not connect to database with any host")
    print("\nPlease check your database connection details in Supabase:")
    print("  Project Settings > Database > Connection String")
    print("\nOr apply the schema manually in SQL Editor:")
    print(f"  1. Go to {supabase_url.replace('https://', 'https://supabase.com/dashboard/project/')}")
    print("  2. Navigate to SQL Editor")
    print("  3. Copy and paste the contents of books_schema.sql")
    print("  4. Run the query")
    sys.exit(1)

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

# Connect and execute
print("\n2. Executing schema...")
try:
    cursor = conn.cursor()
    print("   Running SQL...")
    cursor.execute(schema_sql)
    print("   ✓ Schema executed successfully")
    
    # Verify tables were created
    print("\n3. Verifying tables...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('books', 'book_chapters', 'book_notes')
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if len(tables) == 3:
        print("   ✓ All tables created:")
        for table in tables:
            print(f"     - {table[0]}")
    else:
        print(f"   ⚠ Only {len(tables)} tables found (expected 3)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("SCHEMA APPLICATION COMPLETE ✓")
    print("=" * 60)
    print("\nYou can now run test_books.py to verify functionality")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
