"""
Apply schema updates to Supabase database using psycopg2
Executes the schema_updates.sql file to create missing tables
"""

import os
import psycopg2
from dotenv import load_dotenv
import re

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def get_connection_string():
    """Build PostgreSQL connection string from Supabase credentials"""
    supabase_url = os.getenv("SUPABASE_URL")
    
    if not supabase_url:
        raise ValueError("SUPABASE_URL must be set in .env file")
    
    # Extract project reference from Supabase URL
    # Format: https://PROJECT_REF.supabase.co
    match = re.search(r'https://([^.]+)\.supabase\.co', supabase_url)
    if not match:
        raise ValueError(f"Invalid SUPABASE_URL format: {supabase_url}")
    
    project_ref = match.group(1)
    
    # Get password from environment
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    
    if not db_password:
        print("\n" + "="*70)
        print("SUPABASE_DB_PASSWORD not found in .env file")
        print("\nTo find your database password:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Click 'Settings' → 'Database'")
        print("4. Look for 'Connection string' section")
        print("5. Copy the password (or reset it)")
        print("6. Add to .env file: SUPABASE_DB_PASSWORD=your_password")
        print("="*70 + "\n")
        
        # Prompt for password
        db_password = input("Enter your Supabase database password: ").strip()
        
        if not db_password:
            raise ValueError("Database password is required")
    
    # Build connection string
    conn_string = (
        f"postgresql://postgres.{project_ref}:{db_password}"
        f"@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    
    return conn_string

def run_schema_updates():
    """
    Execute the schema_updates.sql file
    """
    sql_file = os.path.join(os.path.dirname(__file__), 'schema_updates.sql')
    
    print(f"\nReading SQL file: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("Connecting to Supabase database...")
    
    try:
        conn_string = get_connection_string()
        
        # Connect to database
        conn = psycopg2.connect(conn_string)
        conn.autocommit = False  # Use transactions
        cursor = conn.cursor()
        
        print("✓ Connected successfully\n")
        print("="*70)
        print("Executing schema updates...")
        print("="*70 + "\n")
        
        try:
            # Execute the entire SQL file
            cursor.execute(sql_content)
            
            # Commit the transaction
            conn.commit()
            
            print("\n" + "="*70)
            print("✓ Schema updates applied successfully!")
            print("="*70 + "\n")
            
            # Try to get table counts
            try:
                cursor.execute("""
                    SELECT 
                        'youtube_videos' as table_name, COUNT(*) as row_count 
                    FROM youtube_videos
                    UNION ALL
                    SELECT 'video_notes', COUNT(*) FROM video_notes
                    UNION ALL
                    SELECT 'subtitle_chunks', COUNT(*) FROM subtitle_chunks
                    UNION ALL
                    SELECT 'prompts_config', COUNT(*) FROM prompts_config
                    UNION ALL
                    SELECT 'tag_keys', COUNT(*) FROM tag_keys
                    UNION ALL
                    SELECT 'job_queue', COUNT(*) FROM job_queue
                    ORDER BY table_name;
                """)
                
                results = cursor.fetchall()
                
                print("Current table row counts:")
                print("-" * 40)
                for table_name, row_count in results:
                    print(f"  {table_name:20} {row_count:>6} rows")
                print("-" * 40 + "\n")
                
            except Exception as e:
                print(f"Note: Could not fetch table counts: {str(e)}\n")
            
        except Exception as e:
            conn.rollback()
            print(f"\n✗ Error executing SQL: {str(e)}")
            print("\nTransaction rolled back. No changes were made.")
            raise
        
        finally:
            cursor.close()
            conn.close()
            print("Database connection closed.")
        
    except psycopg2.Error as e:
        print(f"\n✗ Database error: {str(e)}")
        print("\nPlease check:")
        print("  1. SUPABASE_URL is correct in .env")
        print("  2. SUPABASE_DB_PASSWORD is correct in .env")
        print("  3. Database is accessible from your network")
        raise
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  Schema Update Tool for Supabase Database")
    print("="*70)
    
    try:
        run_schema_updates()
        print("\n✓ All done! Your database schema is now up to date.\n")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user. No changes were made.\n")
        
    except Exception as e:
        print(f"\n✗ Failed to apply schema updates.\n")
        print("If you need help, check the documentation or run SQL manually.")
        print("="*70 + "\n")
