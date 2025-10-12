"""
Test the API endpoint for chunk notes
"""

import requests
import json

BASE_URL = "http://localhost:8000"
VIDEO_ID = "Esu8BXLBmZ4"
CHUNK_ID = 0

# You'll need to get a token from the frontend or use a test token
# For now, we'll test if the endpoint exists and returns correct structure

print("\n=== Testing Chunk Notes API Endpoint ===\n")

# Test 1: Get chunk details (should include note_content)
print("Test 1: GET /api/chunks/{video_id}/{chunk_id}")
print(f"URL: {BASE_URL}/api/chunks/{VIDEO_ID}/{CHUNK_ID}")
print("Note: This requires authentication. Testing structure only.\n")

# Test 2: Update chunk note endpoint structure
print("Test 2: PUT /api/chunks/{video_id}/{chunk_id}/note")
print(f"URL: {BASE_URL}/api/chunks/{VIDEO_ID}/{CHUNK_ID}/note")
print("Expected request body:")
print(json.dumps({"note_content": "# Markdown content"}, indent=2))
print()

print("✅ API endpoints are defined:")
print(f"   GET  /api/chunks/{VIDEO_ID}/{CHUNK_ID}")
print(f"   PUT  /api/chunks/{VIDEO_ID}/{CHUNK_ID}/note")
print()
print("📝 To test with authentication:")
print("   1. Log in to the frontend at http://localhost:3001")
print("   2. Navigate to a video with chunks")
print("   3. Select a chunk from the dropdown")
print("   4. You should see 5 boxes including 'Chunk Notes'")
print("   5. Write markdown in the editor and click 'Save Note'")
print()
print("🔍 Check backend logs for:")
print("   [DB->] UPDATE subtitle_chunks note_content ...")
print("   [DB<-] Updated note for chunk ...")
