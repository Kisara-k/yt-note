# Books Feature - Quick Reference

## 🚀 Quick Start

### 1. Setup Database (One-time)

```bash
# In Supabase SQL Editor (2nd database):
# Copy and paste contents of books_schema.sql
```

### 2. Create Storage Bucket

```bash
cd backend
python apply_books_schema.py
```

### 3. Start Application

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Access Books

Navigate to: **http://localhost:3000/books**

## 📖 Using the Books Feature

### Upload a Book

1. Enter a **Book ID** (short string, e.g., `the_subtle_art`)
2. Enter **Title**, **Author**, **Description** (optional)
3. Paste **JSON** with chapters:
   ```json
   [
     {
       "chapter_title": "Chapter 1: Introduction",
       "chapter_text": "Full chapter text here..."
     },
     {
       "chapter_title": "Chapter 2: Main Ideas",
       "chapter_text": "Full chapter text here..."
     }
   ]
   ```
4. Click **Upload Book**

### Take Notes

- **Overall Book Note**: Use the main editor at the top
- **Chapter Notes**: Select a chapter and use the chapter note editor

### Access Books

- URL format: `/books?b=book_id`
- Example: `/books?b=the_subtle_art`

## 🔌 API Endpoints

Base URL: `http://localhost:8000`

All require `Authorization: Bearer <token>` header.

### Books

- `POST /api/book` - Upload book
- `GET /api/book/{book_id}` - Get book
- `GET /api/books` - List books

### Chapters

- `GET /api/book/{book_id}/chapters/index` - Get chapter list
- `GET /api/book/{book_id}/chapter/{chapter_id}` - Get chapter with text

### Notes

- `POST /api/book/note` - Save book note
- `GET /api/book/{book_id}/note` - Get book note
- `POST /api/book/{book_id}/chapter/{chapter_id}/note` - Save chapter note

## 🧪 Testing

```bash
# Test CRUD operations (requires schema setup)
cd backend
python test_books.py

# Test API (requires running backend + auth token)
python test_books_api.py
```

## 📝 JSON Format

```json
{
  "book_id": "unique_book_id",
  "title": "Book Title",
  "author": "Author Name",
  "description": "Book description",
  "tags": ["tag1", "tag2"],
  "chapters": [
    {
      "chapter_title": "Chapter Title",
      "chapter_text": "Full chapter text..."
    }
  ]
}
```

## 🔧 Troubleshooting

### "Failed to upload chapter text to storage"

- Ensure `book-chapters` bucket exists in 2nd database
- Run: `python backend/apply_books_schema.py`

### "Book not found"

- Check SUPABASE_URL_2 in .env
- Verify schema is applied to 2nd database

### Build errors

- Run: `npm run build` to check for TypeScript errors
- All should be warnings, no errors

## 📂 Key Files

**Backend:**

- `backend/db/books_crud.py`
- `backend/db/book_chapters_crud.py`
- `backend/db/book_notes_crud.py`
- `backend/api.py` (book endpoints)

**Frontend:**

- `frontend/app/books/page.tsx`
- `frontend/components/book-notes-editor.tsx`
- `frontend/components/chunk-viewer.tsx` (supports books)

**Schema:**

- `books_schema.sql` (apply to 2nd database)

**Docs:**

- `BOOKS_SETUP.md` - Detailed setup
- `BOOKS_IMPLEMENTATION.md` - Technical details
- `CHANGELOG.md` - Change history

## ⚡ Quick Commands

```bash
# Full setup
cd backend
python apply_books_schema.py
cd ..
cd frontend
npm run build
npm run dev

# Test everything
cd backend
python test_books.py

# Start backend
cd backend
python main.py
```

## 🎯 Features

✅ Upload books via JSON
✅ Chapter-by-chapter viewing
✅ Chapter notes
✅ Overall book notes
✅ Markdown editor (TipTap)
✅ Separate database
✅ Secure authentication
✅ Storage in Supabase Storage

## 📦 Environment Variables Required

```env
# In .env file
SUPABASE_URL_2=your_second_supabase_url
SUPABASE_KEY_2=your_second_supabase_anon_key
SUPABASE_SERVICE_KEY_2=your_second_supabase_service_key
DB_PASSWORD=your_db_password
```
