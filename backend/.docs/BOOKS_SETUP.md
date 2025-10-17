# Books Feature Setup Instructions

## 1. Apply Database Schema

The books schema needs to be applied to your second Supabase database.

### Method 1: SQL Editor (Recommended)

1. Go to your Supabase dashboard for the 2nd database
2. Navigate to: **SQL Editor** > **New Query**
3. Copy the entire contents of `books_schema.sql` (in the root directory)
4. Paste and run the query
5. Verify that three tables were created: `books`, `book_chapters`, `book_notes`

### Method 2: psycopg2 (Alternative)

If you have the correct database connection string:

```bash
python apply_books_schema_psycopg2.py
```

## 2. Create Storage Bucket

The storage bucket `book-chapters` should have been created automatically by running:

```bash
python apply_books_schema.py
```

If not, create it manually:

1. Go to **Storage** in Supabase dashboard (2nd database)
2. Click **New bucket**
3. Name: `book-chapters`
4. Privacy: **Private**
5. Click **Create bucket**

## 3. Test Backend

Run the test script to verify all functionality:

```bash
python test_books.py
```

This will test:

- ✓ Book creation
- ✓ Chapter creation and storage
- ✓ Chapter retrieval with text from storage
- ✓ Chapter notes
- ✓ Book notes
- ✓ All CRUD operations

## 4. Start Backend Server

```bash
python main.py
```

Or using the API:

```bash
python api.py
```

## 5. Start Frontend

```bash
cd ../frontend
npm run dev
```

## 6. Access the Application

- **Books page**: http://localhost:3000/books
- **Videos page**: http://localhost:3000/video

## API Endpoints (Books)

All endpoints require authentication (Bearer token).

### Book Management

- `POST /api/book` - Upload a book with chapters
- `GET /api/book/{book_id}` - Get book metadata
- `GET /api/books` - Get all books

### Chapters

- `GET /api/book/{book_id}/chapters` - Get all chapters
- `GET /api/book/{book_id}/chapters/index` - Get chapter index
- `GET /api/book/{book_id}/chapter/{chapter_id}` - Get chapter details with text

### Notes

- `POST /api/book/note` - Create/update book note
- `GET /api/book/{book_id}/note` - Get book note
- `POST /api/book/{book_id}/chapter/{chapter_id}/note` - Update chapter note

## JSON Format for Book Upload

```json
{
  "book_id": "the_subtle_art",
  "title": "The Subtle Art of Not Giving a F*ck",
  "author": "Mark Manson",
  "description": "A counterintuitive approach to living a good life",
  "chapters": [
    {
      "chapter_title": "Chapter 1: Don't Try",
      "chapter_text": "Full text of chapter 1..."
    },
    {
      "chapter_title": "Chapter 2: Happiness Is a Problem",
      "chapter_text": "Full text of chapter 2..."
    }
  ]
}
```

## Troubleshooting

### Database Connection Issues

- Verify `SUPABASE_URL_2` and `SUPABASE_KEY_2` in `.env`
- Check that both databases use the same `DB_PASSWORD`

### Storage Issues

- Ensure the `book-chapters` bucket exists and is private
- Check that you're using the service role key with proper permissions

### Frontend Issues

- Clear browser cache and reload
- Check browser console for errors
- Verify backend is running on port 8000
