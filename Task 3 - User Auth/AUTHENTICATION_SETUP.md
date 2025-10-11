# Authentication Setup Guide

## Overview

The application now requires authentication via Supabase. Only verified emails (hardcoded in the backend configuration) can access the application.

## Key Changes

- **Email Verification**: Users must have their email address in the verified list (`backend/config.py`)
- **Secure Authentication**: JWT-based authentication using Supabase Auth
- **No Email Storage**: User emails are NOT stored in the `video_notes` table
- **Session Management**: Frontend maintains authentication state using React Context

## Setup Instructions

### 1. Backend Setup

#### Update Environment Variables

Navigate to `backend/db/.env` and add:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_service_role_key_here
SUPABASE_JWT_SECRET=your_supabase_jwt_secret_here
```

**Where to find these values:**

- Go to your Supabase project dashboard
- Navigate to Settings > API
- `SUPABASE_URL`: Project URL
- `SUPABASE_KEY`: `service_role` key (under Project API keys)
- `SUPABASE_JWT_SECRET`: JWT Secret (under JWT Settings)

#### Install Required Dependencies

```bash
cd backend
pip install pyjwt==2.9.0
```

#### Update Database Schema

Run the SQL migration to remove `user_email` column:

```sql
-- In Supabase SQL Editor, run:
ALTER TABLE video_notes DROP COLUMN IF EXISTS user_email;
DROP INDEX IF EXISTS idx_video_notes_user_email;
```

Or use the provided migration file:

```bash
# Execute backend/db/update_schema.sql in Supabase SQL Editor
```

#### Configure Verified Emails

Edit `backend/config.py` to add/remove authorized emails:

```python
VERIFIED_EMAILS = [
    "admin@example.com",
    "user1@example.com",
    # Add your email here
]
```

### 2. Frontend Setup

#### Update Environment Variables

Create `frontend/.env.local` with:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

**Where to find these values:**

- Go to your Supabase project dashboard
- Navigate to Settings > API
- `NEXT_PUBLIC_SUPABASE_URL`: Project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: `anon` `public` key (under Project API keys)

#### Install Dependencies

```bash
cd frontend
pnpm install
```

This will install the new dependency: `@supabase/supabase-js`

### 3. Enable Supabase Email Authentication

1. Go to your Supabase project dashboard
2. Navigate to **Authentication** > **Providers**
3. Enable **Email** provider
4. Configure email templates (optional):
   - Go to **Authentication** > **Email Templates**
   - Customize confirmation email, password reset, etc.

### 4. Create User Accounts

Users must be created in Supabase with verified emails:

**Option A: Via Supabase Dashboard**

1. Go to **Authentication** > **Users**
2. Click **Add User**
3. Enter email and password
4. Check "Auto Confirm User" to skip email verification

**Option B: Via Application**

1. Users can sign up through the app
2. They will receive a confirmation email
3. After confirming, they can sign in (if their email is in the verified list)

## Testing the Authentication

### 1. Start Backend Server

```bash
cd backend
python main.py
```

Server should start at `http://localhost:8000`

### 2. Start Frontend Server

```bash
cd frontend
pnpm dev
```

Frontend should start at `http://localhost:3000`

### 3. Test Login Flow

1. Navigate to `http://localhost:3000`
2. You should see the login page
3. Try signing in with a verified email
4. If email is not in the verified list, you'll get an error
5. Upon successful login, you'll see the video notes editor

## API Changes

### Protected Endpoints

All main endpoints now require authentication:

- `POST /api/video` - Requires `Authorization: Bearer <token>` header
- `GET /api/note/{video_id}` - Requires authentication
- `POST /api/note` - Requires authentication
- `GET /api/notes` - Requires authentication

### New Endpoints

- `POST /api/auth/verify-email` - Check if email is in verified list
  ```json
  Request: { "email": "user@example.com" }
  Response: { "is_verified": true, "message": "..." }
  ```

### Request Example

```javascript
const token = await getAccessToken(); // From auth context

const response = await fetch('/api/video', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({ video_url: 'https://...' }),
});
```

## Security Notes

1. **Verified Email List**: Only emails in `backend/config.py` can access the app
2. **JWT Validation**: Backend validates tokens on every request
3. **No Email in Database**: User emails are not stored in `video_notes` table
4. **Secure Keys**: Keep `SUPABASE_JWT_SECRET` and service role keys private
5. **Environment Files**: Never commit `.env` or `.env.local` files to git

## Troubleshooting

### "Email is not authorized"

- Check if your email is in `backend/config.py` VERIFIED_EMAILS list
- Email comparison is case-insensitive

### "Invalid or expired token"

- Sign out and sign in again
- Check if JWT_SECRET is correctly set in backend

### "Authentication failed"

- Verify Supabase environment variables are correct
- Check if Supabase project is active
- Ensure email provider is enabled in Supabase

### Frontend can't connect to backend

- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in `backend/api.py`
- Verify frontend is using correct API URL

## File Structure

```
backend/
├── config.py              # Verified emails list
├── auth.py                # Authentication middleware
├── api.py                 # Updated with auth requirements
└── db/
    ├── video_notes_crud.py  # Updated (removed user_email)
    ├── update_schema.sql    # Database migration
    └── .env                 # Backend environment variables

frontend/
├── lib/
│   └── auth-context.tsx   # Authentication context
├── components/
│   ├── login-form.tsx     # Login/signup form
│   └── video-notes-editor.tsx  # Updated with auth
├── app/
│   ├── page.tsx           # Auth-protected main page
│   └── layout.tsx         # Wrapped with AuthProvider
└── .env.local             # Frontend environment variables
```

## Migration Checklist

- [ ] Backend: Add Supabase credentials to `.env`
- [ ] Backend: Install `pyjwt` package
- [ ] Backend: Run database migration (remove `user_email` column)
- [ ] Backend: Configure verified emails in `config.py`
- [ ] Frontend: Add Supabase credentials to `.env.local`
- [ ] Frontend: Run `pnpm install`
- [ ] Supabase: Enable Email authentication
- [ ] Supabase: Create user accounts for verified emails
- [ ] Test: Sign in with verified email
- [ ] Test: Try accessing with non-verified email (should fail)
- [ ] Test: Save and load notes while authenticated
