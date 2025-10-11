"""
Utility script to manage verified emails

This script helps maintain the .verified_emails reference file.
The actual hashes must be manually added to config.py VERIFIED_EMAIL_HASHES list.

Workflow:
1. Use this script to generate hashes and update the reference file
2. Copy the hash from the reference file to config.py VERIFIED_EMAIL_HASHES
3. Commit config.py (with hashes) to git
4. Keep .verified_emails in .gitignore for local reference only
"""

import hashlib
import json
import os

VERIFIED_EMAILS_FILE = os.path.join(os.path.dirname(__file__), '.verified_emails')


def hash_email(email: str) -> str:
    """Generate SHA-256 hash of an email"""
    return hashlib.sha256(email.lower().encode()).hexdigest()


def load_verified_emails():
    """Load existing verified emails data"""
    if os.path.exists(VERIFIED_EMAILS_FILE):
        with open(VERIFIED_EMAILS_FILE, 'r') as f:
            return json.load(f)
    return {'emails': {}, 'hashes': []}


def save_verified_emails(data):
    """Save verified emails data"""
    with open(VERIFIED_EMAILS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_email(email: str):
    """Add an email to the reference file and display hash to add to config.py"""
    email = email.lower().strip()
    email_hash = hash_email(email)
    
    data = load_verified_emails()
    
    if email in data['emails']:
        print(f"✓ Email already in reference file: {email}")
        print(f"  Hash: {email_hash}")
        print(f"\n⚠️  Make sure this hash is in config.py VERIFIED_EMAIL_HASHES:")
        print(f'     "{email_hash}",')
        return
    
    data['emails'][email] = email_hash
    
    save_verified_emails(data)
    print(f"✓ Added to reference file: {email}")
    print(f"  Hash: {email_hash}")
    print(f"\n⚠️  ACTION REQUIRED: Add this hash to config.py VERIFIED_EMAIL_HASHES:")
    print(f'     "{email_hash}",  # {email}')
    print(f"\n  Then commit config.py to git.")


def remove_email(email: str):
    """Remove an email from the reference file"""
    email = email.lower().strip()
    
    data = load_verified_emails()
    
    if email in data['emails']:
        email_hash = data['emails'][email]
        del data['emails'][email]
        save_verified_emails(data)
        print(f"✓ Removed from reference file: {email}")
        print(f"\n⚠️  ACTION REQUIRED: Remove this hash from config.py VERIFIED_EMAIL_HASHES:")
        print(f'     "{email_hash}",')
    else:
        print(f"✗ Email not found in reference file: {email}")


def list_emails():
    """List all emails in the reference file"""
    data = load_verified_emails()
    
    if not data['emails']:
        print("\nNo emails in reference file yet.")
        print("Note: Check config.py VERIFIED_EMAIL_HASHES for the actual verified hashes.")
        return
    
    print("\nReference File - Email to Hash Mapping:")
    print("=" * 70)
    for email, email_hash in data['emails'].items():
        print(f"  {email}")
        print(f"    → {email_hash}")
    print(f"\nTotal: {len(data['emails'])} emails in reference file")
    print("\n⚠️  Remember: Only hashes in config.py VERIFIED_EMAIL_HASHES are active!")


def main():
    """Interactive menu"""
    while True:
        print("\n" + "=" * 70)
        print("Verified Email Manager")
        print("=" * 70)
        print("1. Add email")
        print("2. Remove email")
        print("3. List all emails")
        print("4. Generate hash for email (without adding)")
        print("5. Exit")
        print("=" * 70)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            email = input("Enter email to add: ").strip()
            if email:
                add_email(email)
        
        elif choice == '2':
            email = input("Enter email to remove: ").strip()
            if email:
                remove_email(email)
        
        elif choice == '3':
            list_emails()
        
        elif choice == '4':
            email = input("Enter email: ").strip()
            if email:
                print(f"\nEmail: {email.lower()}")
                print(f"Hash:  {hash_email(email)}")
        
        elif choice == '5':
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")


if __name__ == '__main__':
    main()
