/**
 * Centralized API client for the frontend.
 *
 * All requests are made to relative /api/... paths, which are handled by
 * Next.js proxy routes. This keeps the backend URL server-side only and
 * ensures a single place for auth header injection.
 *
 * Usage:
 *   const response = await apiFetch('/api/video/123', token);
 *   const response = await apiFetch('/api/note', token, {
 *     method: 'POST',
 *     body: JSON.stringify({ video_id, note_content }),
 *   });
 */
export function apiFetch(
  path: string,
  token: string | null,
  options: RequestInit = {}
): Promise<Response> {
  const { headers: extraHeaders, ...rest } = options;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(extraHeaders as Record<string, string> | undefined),
  };
  return fetch(path, { ...rest, headers });
}
