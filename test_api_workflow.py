"""
Test the full API workflow:
1. POST /api/jobs/process-video
2. Poll GET /api/chunks/{video_id}/index
3. Verify chunks are created with AI fields
"""

import time
import requests

BASE_URL = "http://localhost:8000"
TEST_VIDEO_ID = "fhsbgtdPvOo"  # The video from your logs

def test_process_video():
    print("="*70)
    print("TESTING FULL API WORKFLOW")
    print("="*70)
    print(f"\nTest video: {TEST_VIDEO_ID}")
    
    # Step 1: Start processing (using no-auth endpoint for testing)
    print("\n[1/3] Starting video processing...")
    response = requests.post(f"{BASE_URL}/api/test/process-video-no-auth", json={
        "video_url": f"https://www.youtube.com/watch?v={TEST_VIDEO_ID}"
    })
    
    if response.status_code == 200:
        print(f"✓ Processing started: {response.json()}")
    else:
        print(f"✗ Failed to start processing: {response.status_code}")
        print(f"  Response: {response.text}")
        return
    
    # Step 2: Poll for completion
    print("\n[2/3] Polling for chunks...")
    max_attempts = 30  # 30 seconds timeout
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(1)
        attempt += 1
        
        response = requests.get(f"{BASE_URL}/api/test/chunks/{TEST_VIDEO_ID}/index")
        
        if response.status_code == 200:
            chunks = response.json()
            
            if len(chunks) > 0:
                print(f"\n✓ Found {len(chunks)} chunks after {attempt} seconds!")
                
                # Step 3: Verify AI fields
                print("\n[3/3] Verifying AI enrichment...")
                enriched_count = sum(1 for chunk in chunks if chunk.get('short_title'))
                
                print(f"\nChunks with AI fields: {enriched_count}/{len(chunks)}")
                
                if enriched_count > 0:
                    print("\n✓ Sample enriched chunk:")
                    sample = next(c for c in chunks if c.get('short_title'))
                    print(f"  Chunk ID: {sample['chunk_id']}")
                    print(f"  Title: {sample['short_title']}")
                    print(f"  Field 1: {sample.get('ai_field_1', 'N/A')[:80]}...")
                    print(f"  Field 2: {sample.get('ai_field_2', 'N/A')[:80]}...")
                    print(f"  Field 3: {sample.get('ai_field_3', 'N/A')[:80]}...")
                
                print("\n" + "="*70)
                print("✓ WORKFLOW COMPLETE!")
                print("="*70)
                return
            else:
                print(f"  Attempt {attempt}: No chunks yet...", end='\r')
        else:
            print(f"\n✗ Error fetching chunks: {response.status_code}")
            break
    
    print(f"\n✗ Timeout after {max_attempts} seconds")
    print("="*70)

if __name__ == "__main__":
    test_process_video()
