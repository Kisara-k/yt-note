# Changelog

All notable changes to the YouTube Notes application.

## [2025-01-14] - AI Fields Manual Edit Feature ✅

### Added - Manual Editing for AI-Generated Fields

Added the ability to manually edit AI-generated content (Summary, Key Points, Topics) with proper undo handling and database persistence.

- **Frontend Component Enhancement (`ai-field-display.tsx`)**

  - Edit button (pencil icon) appears to the left of the regenerate button
  - Click to enter edit mode with a markdown textarea
  - Cancel button (X icon) restores original content (proper undo)
  - Save button (checkmark icon) updates the field in the database
  - Save button disabled when no changes are made
  - Loading states during save operation
  - Toast notifications for success/error feedback

- **Backend API Endpoints**

  - `PUT /api/chunks/{video_id}/{chunk_id}/update-ai-field` - Update AI field for video chunks
  - `PUT /api/book/{book_id}/chapter/{chapter_id}/update-ai-field` - Update AI field for book chapters
  - Request body: `{"field_name": "field_1|field_2|field_3", "field_value": "content"}`
  - Validates field names and updates only the specified field
  - Returns updated record on success

- **Integration (`chunk-viewer.tsx`)**

  - Added `handleUpdateField()` function for API calls
  - Wired up `onUpdate` prop for all three AI fields
  - Updates local state immediately after successful save
  - Works for both video chunks and book chapters
  - Proper authentication handling

- **Benefits**
  - ✅ Users can manually correct or enhance AI-generated content
  - ✅ Full undo support with cancel button
  - ✅ Changes persist to database immediately
  - ✅ Works seamlessly alongside AI regenerate feature
  - ✅ Consistent experience across videos and books

## [2025-01-14] - AI Fields Markdown Display Enhancement ✅

### Improved - AI Fields Display

Enhanced the 3 AI fields (Summary, Key Points, Topics) with proper markdown rendering and smaller font size.

- **New Reusable Component: `ai-field-display.tsx`**

  - Markdown support via `react-markdown`
  - Smaller font size using `prose-xs` typography
  - Compact spacing for better readability
  - Dark mode compatible
  - Configurable max height

- **Updated `chunk-viewer.tsx`**

  - Now uses `AIFieldDisplay` component for all 3 AI fields
  - Reduced code duplication
  - Shared by both `/video` and `/book` pages

- **Benefits**
  - ✅ Markdown formatting (lists, bold, italic, headings) renders properly
  - ✅ Smaller, more readable text throughout
  - ✅ Modular design for easy maintenance
  - ✅ Consistent experience across video and book pages

## [2025-01-13] - Books Feature Complete ✅

### Added - Book Chunk Editor

A comprehensive chunk/chapter editor interface for managing book chapters.

- **Backend API Endpoints**

  - `PUT /api/book/{book_id}/chapter/{chapter_id}/text` - Update chapter text
  - `DELETE /api/book/{book_id}/chapter/{chapter_id}` - Delete a chapter
  - `POST /api/book/{book_id}/chapters/reorder` - Reorder chapters

- **Backend CRUD Functions**

  - `update_chapter_text()` - Update chapter text in storage and DB
  - `reorder_chapters()` - Reorder chapters with transactional safety
  - Uses temporary negative IDs to avoid conflicts during reorder

- **Frontend Interface (`/book/chunks?b=book_id`)**

  - Split-view: Chapters list on left, editor on right
  - **Chapter Management:**
    - Add new chapters
    - Edit chapter title and text
    - Delete chapters with confirmation
    - Reorder chapters with up/down arrows
  - **Real-time Operations:**
    - Load chapter text on-demand from storage
    - Save changes with instant feedback
    - Optimistic UI updates for reordering
  - **Navigation:**
    - "Edit Chunks" button appears in book-notes-editor after loading a book
    - Easy access back to main book interface

- **Component: `book-chunk-editor.tsx`**
  - Full CRUD operations for chapters
  - Textarea editor for chapter text (500+ line capacity)
  - Loading states and error handling
  - Toast notifications for all operations

### Added - Separate Book Prompts for AI Enrichment

Books now use specialized prompts distinct from video prompts for AI enrichment of chapter sections.

- **Book-Specific Prompts**

  - `BOOK_PROMPTS` in `prompts.py` with book-focused language
  - Field 1: "Chapter Summary" (vs "High-Level Summary" for videos)
  - Field 2: "Important Concepts" (vs "Key Points" for videos)
  - Field 3: "Key Insights" (vs "Topics/Themes" for videos)
  - All prompts reference "book chapter section" instead of "video segment"

- **Backend Updates**

  - `get_all_prompts(content_type)` now accepts 'video' or 'book' parameter
  - `get_prompt_label(field_name, content_type)` returns appropriate labels
  - `process_chunks_enrichment_parallel()` accepts `content_type` parameter
  - `/api/prompts?content_type=book` endpoint returns book-specific prompts
  - Backward compatible - defaults to 'video' prompts

- **Testing**
  - `test_book_prompts.py` verifies all 4 prompts differ between video/book
  - All prompts validated as unique ✅

### Added - Books Feature

A complete books management system mirroring YouTube video functionality using a separate Supabase database.

- **Books Database (2nd Supabase Instance)**

  - Database schema: `books`, `book_chapters`, `book_notes` tables
  - Storage bucket: `book-chapters` for chapter text files
  - Full CRUD operations with 50+ functions
  - Supabase Storage integration
  - Sample book created: "A Practical Guide to Learning" with 5 chapters

- **Backend Books API (Python/FastAPI)**

  - `backend/db/books_crud.py` - Book metadata CRUD
  - `backend/db/book_chapters_crud.py` - Chapter CRUD with storage
  - `backend/db/book_chapters_storage.py` - Storage operations
  - `backend/db/book_notes_crud.py` - Book notes CRUD
  - 10+ authenticated API endpoints added to `api.py`
  - Service key configuration for storage writes

- **Frontend Books Interface (Next.js/React)**

  - Route: `/books?b=book_id` for viewing books
  - `components/book-notes-editor.tsx` - Main book upload/viewing UI
  - JSON upload format for chapters (title + text)
  - Manual metadata entry (title, author, description, tags)
  - Reused `ChunkViewer` component with `isBook` prop
  - TipTap markdown editors for notes
  - Chapter-by-chapter navigation and note-taking

- **Testing & Verification**

  - `test_books.py` - Comprehensive CRUD tests (13 operations)
  - `create_sample_book.py` - Sample book generator
  - `verify_book.py` - Database verification script
  - `sample_book.json` - Example book data format
  - All tests passing ✅

- **Documentation**
  - `BOOKS_COMPLETE.md` - Complete implementation summary
  - `BOOKS_SETUP.md` - Setup instructions
  - `BOOKS_IMPLEMENTATION.md` - Technical details
  - `BOOKS_QUICKSTART.md` - Quick start guide

### Fixed - Books Feature

- Storage permission issue: Changed from anon key to service key in all CRUD modules
- TypeScript warnings in book components (unused variables, empty interfaces)
- Frontend build errors resolved

### Changed - Books Frontend Structure

- Restructured books routes to mirror video routes exactly:
  - Changed from `/books?b=id` to `/book?b=id` (singular, like `/video?v=id`)
  - Added `/book/add` route for uploading new books (separated from viewing)
  - Added `/book/filter` route for browsing and filtering all books
- Created three focused components:
  - `book-notes-editor.tsx` - View and take notes on books (like video-notes-editor)
  - `book-add.tsx` - Upload new books with JSON chapters
  - `book-filter.tsx` - Browse, search, filter, and sort books
- All book routes now have same navigation patterns as video routes

### Technical Details - Books

- Chapter text stored in Supabase Storage (not DB) for efficiency
- Path pattern: `{book_id}/chapter_{chapter_id}.txt`
- Service role key required for storage writes (RLS enabled)
- JWT authentication from 1st database shared across both instances

---

## [Unreleased] - 2025-10-13

### � Added - Books Feature

- **Books Database (2nd Supabase Instance)**

  - New database schema for books, chapters, and notes
  - Storage bucket for book chapter text
  - Separate from video database for better organization

- **Backend Books API**

  - Book CRUD operations (`backend/db/books_crud.py`)
  - Chapter management with storage (`backend/db/book_chapters_crud.py`)
  - Book notes CRUD (`backend/db/book_notes_crud.py`)
  - API endpoints for books, chapters, and notes

- **Frontend Books Interface**

  - New `/books` route for book management
  - Upload books via JSON (chapters with titles and text)
  - Reuses existing components (ChunkViewer, TiptapMarkdownEditor)
  - Chapter-by-chapter note taking
  - Overall book notes

- **Book Management**
  - User-defined book IDs (e.g., `the_subtle_art`)
  - Manual metadata entry (title, author, publisher, etc.)
  - JSON upload for chapter content
  - URL format: `/books?b=book_id`

### �🔄 Changed - Route Restructuring

- **Frontend Route Organization**
  - Moved all video-related routes to `/video/` namespace:
    - `/` now shows only the login page
    - `/video` - Main video notes editor (formerly `/`)
    - `/video/filter` - Video filter page (formerly `/filter`)
    - `/video/creator-notes` - Creator notes page (formerly `/creator-notes`)
  - Updated all navigation links and router redirects
  - Authenticated users are now redirected to `/video` from root
  - Prepared structure for future book-related features

## [Unreleased] - 2025-10-10

### 🔐 Added - Authentication & Security

- **Supabase Authentication Integration**

  - JWT-based authentication for all API endpoints
  - Secure login and signup flows
  - Session management with automatic token refresh
  - Sign out functionality

- **Email Whitelist System**

  - Hardcoded list of verified emails in `backend/config.py`
  - Backend endpoint to verify email eligibility
  - Only whitelisted users can access the application
  - Case-insensitive email comparison

- **Authentication Middleware**

  - `backend/auth.py` - JWT token validation
  - Token extraction from Authorization headers
  - User information extraction from tokens
  - Protected API endpoints requiring authentication

- **Frontend Authentication**
  - `frontend/lib/auth-context.tsx` - React context for auth state
  - `frontend/components/login-form.tsx` - Login/signup UI
  - Auth-protected main page
  - User email display in header
  - Sign out button

### 🔄 Changed

- **API Endpoints**

  - All main endpoints now require authentication:
    - `POST /api/video` - Requires Bearer token
    - `GET /api/note/{video_id}` - Requires Bearer token
    - `POST /api/note` - Requires Bearer token
    - `GET /api/notes` - Requires Bearer token

- **Database Schema**

  - Removed `user_email` column from `video_notes` table
  - Dropped `idx_video_notes_user_email` index
  - User emails no longer stored in database

- **CRUD Functions**

  - `create_or_update_note()` - Removed `user_email` parameter
  - `get_all_notes()` - Removed `user_email` filter parameter
  - `get_notes_with_video_info()` - Removed `user_email` filter parameter

- **Frontend Components**
  - `video-notes-editor.tsx` - Added auth token to API requests
  - `page.tsx` - Added auth check before rendering editor
  - `layout.tsx` - Wrapped with AuthProvider

### 📦 Dependencies

**Backend:**

- Added `pyjwt==2.9.0` for JWT token validation

**Frontend:**

- Added `@supabase/supabase-js@^2.47.10` for authentication

### 📝 Documentation

- Added `AUTHENTICATION_SETUP.md` - Complete authentication setup guide
- Updated `README.md` with authentication information
- Added `backend/db/.env.example` - Backend environment template
- Added `frontend/.env.example` - Frontend environment template
- Added `backend/db/update_schema.sql` - Database migration script

### 🔧 Configuration

**New Environment Variables:**

Backend (`backend/db/.env`):

- `SUPABASE_JWT_SECRET` - JWT secret for token validation
- Updated `SUPABASE_KEY` usage (now uses service role key)

Frontend (`frontend/.env.local`):

- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key

**New Configuration Files:**

- `backend/config.py` - Verified emails whitelist

### 🛠️ Migration Steps

To upgrade from previous version:

1. Install new backend dependency: `pip install pyjwt==2.9.0`
2. Install new frontend dependency: `pnpm install` (updates package-lock)
3. Update backend `.env` with Supabase JWT secret
4. Create frontend `.env.local` with Supabase credentials
5. Run database migration: Execute `backend/db/update_schema.sql`
6. Configure verified emails in `backend/config.py`
7. Enable Email Auth in Supabase dashboard
8. Create user accounts for verified emails

### ⚠️ Breaking Changes

- **Authentication Required**: All API endpoints now require valid JWT tokens
- **No Anonymous Access**: Users must sign in to use the application
- **Email Whitelist**: Only pre-approved emails can access the app
- **Database Schema**: `user_email` column removed from `video_notes` table
- **API Signature Changes**: CRUD functions no longer accept `user_email` parameter

---

## [1.1.0] - Previous Release

### Added

- Task 2: Web application with note-taking functionality
- FastAPI backend with REST API
- Next.js frontend with TipTap editor
- Video information fetching and display
- Note creation and persistence

## [1.0.0] - Initial Release

### Added

- Task 1: YouTube API integration
- Database schema for video storage
- CRUD operations for video data
- Batch processing for multiple videos
- Command-line interface
