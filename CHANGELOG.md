# Changelog

All notable changes to the YouTube Notes application.

## [Unreleased] - 2025-10-13

### 🔄 Changed - Route Restructuring

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
