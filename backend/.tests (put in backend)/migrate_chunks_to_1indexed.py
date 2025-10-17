"""
Migration script to convert video chunks from 0-indexed to 1-indexed

This script:
1. Fetches all video chunks from the database
2. Updates chunk_id by adding 1 (0 → 1, 1 → 2, etc.)
3. Updates storage paths (chunk_0.txt → chunk_1.txt, etc.)
4. Preserves all chunk data and relationships

Usage:
    python migrate_chunks_to_1indexed.py [--dry-run]
    
Options:
    --dry-run    Show what would be changed without making changes
"""

import sys
from db.subtitle_chunks_crud import supabase
from db.subtitle_chunks_storage import supabase as storage_supabase, BUCKET_NAME

def get_all_videos_with_chunks():
    """Get all unique video IDs that have chunks"""
    try:
        response = supabase.table("subtitle_chunks")\
            .select("video_id")\
            .execute()
        
        if response.data:
            # Get unique video IDs
            video_ids = list(set(chunk['video_id'] for chunk in response.data))
            return video_ids
        return []
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []

def get_chunks_for_video(video_id: str):
    """Get all chunks for a specific video, ordered by chunk_id"""
    try:
        response = supabase.table("subtitle_chunks")\
            .select("*")\
            .eq("video_id", video_id)\
            .order("chunk_id")\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching chunks for video {video_id}: {e}")
        return []

def copy_storage_file(video_id: str, old_chunk_id: int, new_chunk_id: int, dry_run: bool = False):
    """Copy storage file from old path to new path"""
    old_path = f"{video_id}/chunk_{old_chunk_id}.txt"
    new_path = f"{video_id}/chunk_{new_chunk_id}.txt"
    
    if dry_run:
        print(f"  [DRY-RUN] Would copy: {old_path} → {new_path}")
        return True
    
    try:
        # Download content from old path
        response = storage_supabase.storage.from_(BUCKET_NAME).download(old_path)
        if not response:
            print(f"  ❌ Failed to download {old_path}")
            return False
        
        content = response
        
        # Upload to new path (upsert if exists)
        try:
            storage_supabase.storage.from_(BUCKET_NAME).upload(
                new_path,
                content,
                file_options={"content-type": "text/plain", "upsert": "true"}
            )
        except Exception as upload_err:
            # If file exists, try to remove and re-upload
            try:
                storage_supabase.storage.from_(BUCKET_NAME).remove([new_path])
                storage_supabase.storage.from_(BUCKET_NAME).upload(
                    new_path,
                    content,
                    file_options={"content-type": "text/plain"}
                )
            except Exception as retry_err:
                print(f"  ❌ Error uploading {new_path}: {retry_err}")
                return False
        
        print(f"  ✅ Copied: {old_path} → {new_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error copying storage file: {e}")
        return False

def delete_storage_file(video_id: str, chunk_id: int, dry_run: bool = False):
    """Delete old storage file"""
    path = f"{video_id}/chunk_{chunk_id}.txt"
    
    if dry_run:
        print(f"  [DRY-RUN] Would delete: {path}")
        return True
    
    try:
        storage_supabase.storage.from_(BUCKET_NAME).remove([path])
        print(f"  🗑️  Deleted: {path}")
        return True
    except Exception as e:
        print(f"  ❌ Error deleting {path}: {e}")
        return False

def migrate_video_chunks(video_id: str, dry_run: bool = False):
    """Migrate all chunks for a single video from 0-indexed to 1-indexed"""
    print(f"\n📹 Processing video: {video_id}")
    
    # Get all chunks for this video
    chunks = get_chunks_for_video(video_id)
    
    if not chunks:
        print(f"  ℹ️  No chunks found")
        return True
    
    print(f"  Found {len(chunks)} chunks")
    
    # Check if already migrated (if first chunk has chunk_id > 0)
    if chunks and chunks[0]['chunk_id'] > 0:
        print(f"  ⚠️  Already migrated (first chunk_id = {chunks[0]['chunk_id']})")
        return True
    
    # Step 1: Copy storage files to new paths (in reverse order to avoid conflicts)
    print(f"  Step 1: Copying storage files...")
    for chunk in reversed(chunks):
        old_id = chunk['chunk_id']
        new_id = old_id + 1
        
        if not copy_storage_file(video_id, old_id, new_id, dry_run):
            print(f"  ❌ Failed to copy storage file for chunk {old_id}")
            return False
    
    # Step 2: Update database records (in reverse order to avoid unique constraint violations)
    print(f"  Step 2: Updating database records...")
    
    if dry_run:
        for chunk in reversed(chunks):
            old_id = chunk['chunk_id']
            new_id = old_id + 1
            print(f"  [DRY-RUN] Would update chunk {old_id} → {new_id}")
    else:
        # Update in reverse order to avoid conflicts
        for chunk in reversed(chunks):
            old_id = chunk['chunk_id']
            new_id = old_id + 1
            new_path = f"{video_id}/chunk_{new_id}.txt"
            
            try:
                # Delete old record
                supabase.table("subtitle_chunks")\
                    .delete()\
                    .eq("video_id", video_id)\
                    .eq("chunk_id", old_id)\
                    .execute()
                
                # Insert new record with updated chunk_id and path
                new_chunk = {
                    'video_id': video_id,
                    'chunk_id': new_id,
                    'chunk_text_path': new_path,
                    'short_title': chunk.get('short_title'),
                    'ai_field_1': chunk.get('ai_field_1'),
                    'ai_field_2': chunk.get('ai_field_2'),
                    'ai_field_3': chunk.get('ai_field_3'),
                    'note_content': chunk.get('note_content')
                }
                
                supabase.table("subtitle_chunks").insert(new_chunk).execute()
                print(f"  ✅ Updated chunk {old_id} → {new_id}")
                
            except Exception as e:
                print(f"  ❌ Error updating chunk {old_id}: {e}")
                return False
    
    # Step 3: Delete old storage files
    print(f"  Step 3: Cleaning up old storage files...")
    for chunk in chunks:
        old_id = chunk['chunk_id']
        if not delete_storage_file(video_id, old_id, dry_run):
            print(f"  ⚠️  Warning: Failed to delete old storage file for chunk {old_id}")
    
    print(f"  ✅ Migration complete for {video_id}")
    return True

def main():
    """Run the migration"""
    dry_run = '--dry-run' in sys.argv
    
    if dry_run:
        print("=" * 60)
        print("🔍 DRY RUN MODE - No changes will be made")
        print("=" * 60)
    else:
        print("=" * 60)
        print("⚠️  MIGRATION MODE - Changes will be permanent")
        print("=" * 60)
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Migration cancelled")
            return
    
    print("\n🚀 Starting migration: 0-indexed → 1-indexed chunks\n")
    
    # Get all videos with chunks
    video_ids = get_all_videos_with_chunks()
    print(f"Found {len(video_ids)} videos with chunks\n")
    
    if not video_ids:
        print("✅ No videos to migrate")
        return
    
    # Migrate each video
    success_count = 0
    fail_count = 0
    
    for video_id in video_ids:
        try:
            if migrate_video_chunks(video_id, dry_run):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"\n❌ Error migrating video {video_id}: {e}")
            fail_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count} videos")
    print(f"❌ Failed:     {fail_count} videos")
    print(f"📹 Total:      {len(video_ids)} videos")
    
    if dry_run:
        print("\n🔍 This was a dry run. Run without --dry-run to apply changes.")
    else:
        print("\n✅ Migration complete!")

if __name__ == "__main__":
    main()
