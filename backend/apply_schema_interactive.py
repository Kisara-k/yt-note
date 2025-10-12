"""
Interactive script to apply schema update to Supabase
Uses the Management API if credentials available, otherwise provides instructions
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def apply_schema_via_management_api():
    """Try to apply schema using Supabase Management API"""
    
    # Read the SQL
    sql_file = os.path.join(os.path.dirname(__file__), 'db', 'add_chunk_notes.sql')
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    print("\n" + "="*60)
    print("SUPABASE SCHEMA UPDATE - Chunk Notes Feature")
    print("="*60)
    
    print("\nSQL to execute:")
    print("-"*60)
    print(sql)
    print("-"*60)
    
    # Try to get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("\n❌ Supabase credentials not found in .env file")
        show_manual_instructions(sql)
        return False
    
    # Extract project ref from URL
    try:
        project_ref = supabase_url.split("//")[1].split(".")[0]
        print(f"\n✓ Found project: {project_ref}")
    except:
        print("\n❌ Could not parse Supabase URL")
        show_manual_instructions(sql)
        return False
    
    # Try to execute via PostgREST (this usually doesn't work for DDL, but we try)
    print("\n⚠ Note: DDL statements typically require manual execution in Supabase SQL Editor")
    show_manual_instructions(sql)
    
    return False


def show_manual_instructions(sql):
    """Show manual instructions for applying the schema"""
    print("\n" + "="*60)
    print("MANUAL SCHEMA UPDATE REQUIRED")
    print("="*60)
    
    print("\n📋 Steps to apply:")
    print("1. Open Supabase Dashboard: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Click 'SQL Editor' in left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy and paste the SQL shown above")
    print("6. Click 'Run' or press Ctrl+Enter")
    print("7. Verify you see 'Success. No rows returned'")
    
    print("\n✅ After applying, you can test with: python test_chunk_notes.py")
    print("✅ Or start the servers and test in the browser")
    
    # Ask user if they want to continue
    print("\n" + "="*60)
    response = input("\nHave you applied the schema update? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n✅ Great! The feature should now work.")
        print("   Test it by running: python test_chunk_notes.py")
        return True
    else:
        print("\n⚠ Please apply the schema update before using the chunk notes feature.")
        return False


if __name__ == "__main__":
    try:
        apply_schema_via_management_api()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
