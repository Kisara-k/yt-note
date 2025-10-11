'use client';

import { useState, useEffect } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Save, Video, Loader2, LogOut } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

interface VideoInfo {
  video_id: string;
  title: string;
  channel_title: string;
  channel_id: string;
  published_at?: string;
  description?: string;
  duration?: string;
  view_count?: number;
  like_count?: number;
}

interface NoteData {
  video_id: string;
  note_content: string | null;
  created_at?: string;
  updated_at?: string;
}

export function VideoNotesEditor() {
  const [videoUrl, setVideoUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [noteContent, setNoteContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const { user, signOut, getAccessToken } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
      toast.success('Signed out successfully');
    } catch (error) {
      toast.error('Failed to sign out');
    }
  };

  const handleFetchVideo = async () => {
    if (!videoUrl.trim()) {
      toast.error('Please enter a video URL or ID');
      return;
    }

    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        setLoading(false);
        return;
      }

      // Fetch video info from backend
      const videoResponse = await fetch('http://localhost:8000/api/video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ video_url: videoUrl }),
      });

      if (!videoResponse.ok) {
        const error = await videoResponse.json();
        const errorMessage =
          typeof error.detail === 'string'
            ? error.detail
            : error.error || error.message || 'Failed to fetch video';
        throw new Error(errorMessage);
      }

      const videoData: VideoInfo = await videoResponse.json();

      // Start note fetch immediately after getting video_id (parallel processing)
      const notePromise = fetch(
        `http://localhost:8000/api/note/${videoData.video_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
        .then(async (response) => {
          if (response.ok) {
            const noteData: NoteData = await response.json();
            return noteData.note_content || '';
          }
          return '';
        })
        .catch(() => '');

      // Set video info immediately (don't wait for note)
      setVideoInfo(videoData);
      toast.success(`Loaded: ${videoData.title}`);

      // Wait for note to complete and update
      const loadedNote = await notePromise;
      setNoteContent(loadedNote);

      if (loadedNote) {
        toast.info('Existing note loaded');
      }

      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error fetching video:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to fetch video'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNote = async () => {
    if (!videoInfo) {
      toast.error('Please load a video first');
      return;
    }

    setSaving(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        setSaving(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/note', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          video_id: videoInfo.video_id,
          note_content: noteContent,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        const errorMessage =
          typeof error.detail === 'string'
            ? error.detail
            : error.error || error.message || 'Failed to save note';
        throw new Error(errorMessage);
      }

      const savedNote: NoteData = await response.json();
      toast.success('Note saved successfully');
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error saving note:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to save note'
      );
    } finally {
      setSaving(false);
    }
  };

  const handleEditorChange = (markdown: string) => {
    // Content is already in markdown format from TiptapMarkdownEditor
    setNoteContent(markdown);
    if (videoInfo) {
      setHasUnsavedChanges(true);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleFetchVideo();
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto p-6 max-w-6xl'>
        <div className='mb-8 flex justify-between items-center'>
          <div>
            <h1 className='text-3xl font-bold mb-2'>YouTube Notes</h1>
            <p className='text-muted-foreground'>
              Enter a YouTube video URL or ID to create notes
            </p>
          </div>
          <div className='flex items-center gap-4'>
            <div className='text-sm text-muted-foreground'>
              Signed in as <strong>{user?.email}</strong>
            </div>
            <Button variant='outline' size='sm' onClick={handleSignOut}>
              <LogOut className='mr-2 h-4 w-4' />
              Sign Out
            </Button>
          </div>
        </div>

        {/* Video URL Input */}
        <div className='mb-6 space-y-4'>
          <div className='flex gap-2'>
            <div className='flex-1'>
              <Label htmlFor='video-url' className='sr-only'>
                Video URL or ID
              </Label>
              <Input
                id='video-url'
                type='text'
                placeholder='Enter YouTube URL or Video ID (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)'
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                className='text-base'
              />
            </div>
            <Button
              onClick={handleFetchVideo}
              disabled={loading || !videoUrl.trim()}
              className='min-w-[120px]'
            >
              {loading ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Loading...
                </>
              ) : (
                <>
                  <Video className='mr-2 h-4 w-4' />
                  Load Video
                </>
              )}
            </Button>
          </div>

          {/* Video Info Display */}
          {videoInfo && (
            <div className='bg-card border rounded-lg p-4 space-y-2'>
              <h2 className='text-xl font-semibold'>{videoInfo.title}</h2>
              <div className='flex gap-4 text-sm text-muted-foreground'>
                <span>Channel: {videoInfo.channel_title}</span>
                {videoInfo.view_count && (
                  <span>Views: {videoInfo.view_count.toLocaleString()}</span>
                )}
                {videoInfo.like_count && (
                  <span>Likes: {videoInfo.like_count.toLocaleString()}</span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Editor Section */}
        {videoInfo && (
          <div className='space-y-4'>
            <div className='flex justify-between items-center'>
              <Label className='text-lg font-semibold'>
                Note{' '}
                {hasUnsavedChanges && <span className='text-amber-500'>*</span>}
              </Label>
              <Button
                onClick={handleSaveNote}
                disabled={saving || !hasUnsavedChanges}
                variant='default'
              >
                {saving ? (
                  <>
                    <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className='mr-2 h-4 w-4' />
                    Save Note
                  </>
                )}
              </Button>
            </div>

            <div className='border rounded-lg overflow-hidden bg-background'>
              <TiptapMarkdownEditor
                value={noteContent}
                onChange={handleEditorChange}
                className='min-h-[500px]'
                placeholder='Start writing your notes here...'
              />
            </div>

            {hasUnsavedChanges && (
              <p className='text-sm text-muted-foreground'>
                You have unsaved changes. Click "Save Note" to save your work.
              </p>
            )}
          </div>
        )}

        {/* Empty State */}
        {!videoInfo && !loading && (
          <div className='text-center py-12 text-muted-foreground'>
            <Video className='h-16 w-16 mx-auto mb-4 opacity-20' />
            <p className='text-lg'>Enter a video URL above to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}
