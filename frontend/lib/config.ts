/**
 * API Configuration
 * Central configuration for backend API URL
 *
 * Development: http://localhost:8000
 * Production: Set NEXT_PUBLIC_BACKEND_URL in Vercel environment variables
 *
 * 🔒 SECURITY NOTE:
 * This is the ONLY environment variable needed in the frontend!
 * All Supabase credentials are kept server-side only.
 * Authentication flows through the backend API.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
