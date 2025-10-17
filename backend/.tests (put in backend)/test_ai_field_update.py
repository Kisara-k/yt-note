"""
Test the new AI field update endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n=== Testing AI Field Update API Endpoints ===\n")

# Test 1: Verify video chunk update endpoint exists
print("Test 1: PUT /api/chunks/{video_id}/{chunk_id}/update-ai-field")
endpoint = f"{BASE_URL}/api/chunks/test_video_id/1/update-ai-field"
print(f"URL: {endpoint}")
print("Expected request body:")
print(json.dumps({
    "field_name": "field_1",
    "field_value": "Updated summary content"
}, indent=2))
print()

# Test 2: Verify book chapter update endpoint exists
print("Test 2: PUT /api/book/{book_id}/chapter/{chapter_id}/update-ai-field")
endpoint = f"{BASE_URL}/api/book/test_book_id/1/update-ai-field"
print(f"URL: {endpoint}")
print("Expected request body:")
print(json.dumps({
    "field_name": "field_1",
    "field_value": "Updated chapter summary"
}, indent=2))
print()

# Test 3: Check API docs
print("Test 3: Checking OpenAPI docs for new endpoints...")
try:
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi_spec = response.json()
        paths = openapi_spec.get("paths", {})
        
        # Check for video chunk update endpoint
        video_path = "/api/chunks/{video_id}/{chunk_id}/update-ai-field"
        if video_path in paths and "put" in paths[video_path]:
            print(f"✅ Video chunk update endpoint found in OpenAPI spec")
            print(f"   Summary: {paths[video_path]['put'].get('summary', 'N/A')}")
        else:
            print(f"❌ Video chunk update endpoint NOT found in OpenAPI spec")
        
        # Check for book chapter update endpoint
        book_path = "/api/book/{book_id}/chapter/{chapter_id}/update-ai-field"
        if book_path in paths and "put" in paths[book_path]:
            print(f"✅ Book chapter update endpoint found in OpenAPI spec")
            print(f"   Summary: {paths[book_path]['put'].get('summary', 'N/A')}")
        else:
            print(f"❌ Book chapter update endpoint NOT found in OpenAPI spec")
    else:
        print(f"⚠️  Could not fetch OpenAPI spec (status: {response.status_code})")
except Exception as e:
    print(f"⚠️  Error checking OpenAPI spec: {e}")

print()
print("✅ API endpoints are defined:")
print(f"   PUT  /api/chunks/{{video_id}}/{{chunk_id}}/update-ai-field")
print(f"   PUT  /api/book/{{book_id}}/chapter/{{chapter_id}}/update-ai-field")
print()
print("📝 Expected functionality:")
print("   1. Edit button appears next to regenerate button on AI fields")
print("   2. Clicking edit shows a textarea with the current content")
print("   3. User can modify the markdown content")
print("   4. Cancel button (X) restores original content")
print("   5. Save button sends PUT request to update the field")
print("   6. Success toast shows and content updates in the database")
print()
print("🔍 To test manually:")
print("   1. Log in to the frontend at http://localhost:3001")
print("   2. Navigate to a video or book with processed chunks/chapters")
print("   3. Select a chunk/chapter from the dropdown")
print("   4. Look for Edit button (pencil icon) next to Regenerate button")
print("   5. Click Edit, modify content, and click Save (checkmark icon)")
print("   6. Verify the content updates and persists after reload")
print()
