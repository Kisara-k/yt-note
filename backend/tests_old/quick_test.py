"""Quick test of the API endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("\n=== Testing YouTube Notes API ===\n")

# Test 1: Fetch a video
print("1. Testing video fetch...")
response = requests.post(
    f"{BASE_URL}/api/video",
    json={"video_url": "dQw4w9WgXcQ"}
)
print(f"   Status: {response.status_code}")
if response.ok:
    video = response.json()
    print(f"   ✓ Title: {video['title']}")
    print(f"   ✓ Channel: {video['channel_title']}")
    video_id = video['video_id']
else:
    print(f"   ✗ Error: {response.text}")
    video_id = "dQw4w9WgXcQ"

# Test 2: Save a note
print("\n2. Testing note save...")
note_content = "# Test Note\n\nThis is a **test** note."
response = requests.post(
    f"{BASE_URL}/api/note",
    json={
        "video_id": video_id,
        "note_content": note_content,
        "user_email": "test@example.com"
    }
)
print(f"   Status: {response.status_code}")
if response.ok:
    note = response.json()
    print(f"   ✓ Note saved for video: {note['video_id']}")
else:
    print(f"   ✗ Error: {response.text}")

# Test 3: Get the note back
print("\n3. Testing note retrieval...")
response = requests.get(f"{BASE_URL}/api/note/{video_id}")
print(f"   Status: {response.status_code}")
if response.ok:
    note = response.json()
    if note.get('note_content'):
        print(f"   ✓ Note retrieved: {note['note_content'][:50]}...")
    else:
        print(f"   ✓ No note exists yet")
else:
    print(f"   ✗ Error: {response.text}")

# Test 4: Get all notes
print("\n4. Testing get all notes...")
response = requests.get(f"{BASE_URL}/api/notes")
print(f"   Status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"   ✓ Found {data['count']} notes")
else:
    print(f"   ✗ Error: {response.text}")

print("\n=== Tests Complete ===\n")
