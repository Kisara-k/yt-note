/**
 * API Configuration
 *
 * The backend URL is configured via the BACKEND_URL environment variable.
 * This is a server-side-only variable (no NEXT_PUBLIC_ prefix), so it is
 * never exposed to the browser.
 *
 * All frontend API calls go through Next.js proxy routes at /api/...
 * which forward requests to the backend using BACKEND_URL.
 *
 * Set in .env.local for development:
 *   BACKEND_URL=http://localhost:8000
 *
 * Set in Vercel / Railway for production:
 *   BACKEND_URL=https://your-backend.railway.app
 */
