'use client';

import { useState, useEffect, useRef } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { ChunkViewer } from '@/components/chunk-viewer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
// import { toast } from 'sonner';
import {
  Save,
  Video,
  Loader2,
  LogOut,
  PlayCircle,
  Filter,
  User,
  ThumbsUp,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';

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
  const [initialLoadedContent, setInitialLoadedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [processingSubtitles, setProcessingSubtitles] = useState(false);
  const [processingAI, setProcessingAI] = useState(false);
  const [hasSubtitles, setHasSubtitles] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const chunkViewerKey = useRef(0);
  const { user, signOut, getAccessToken } = useAuth();
  const router = useRouter();

  // Load video from localStorage on mount
  useEffect(() => {
    const savedVideoId = localStorage.getItem('currentVideoId');
    if (savedVideoId && !videoInfo) {
      // Auto-load the saved video
      loadVideoById(savedVideoId);
    }
  }, []);

  // Save video to localStorage when it changes
  useEffect(() => {
    if (videoInfo) {
      localStorage.setItem('currentVideoId', videoInfo.video_id);
    }
  }, [videoInfo]);

  const handleSignOut = async () => {
    try {
      await signOut();
      // toast.success('Signed out successfully');
    } catch (error) {
      // toast.error('Failed to sign out');
    }
  };

  const loadVideoById = async (video_id: string) => {
    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        // toast.error('Authentication required');
        setLoading(false);
        return;
      }

      // Fetch video metadata from database
      const videoResponse = await fetch(
        `http://localhost:8000/api/video/${video_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!videoResponse.ok) {
        throw new Error('Failed to load saved video');
      }

      const videoData: VideoInfo = await videoResponse.json();

      // Load note
      const noteResponse = await fetch(
        `http://localhost:8000/api/note/${video_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      let loadedNote = '';
      if (noteResponse.ok) {
        const noteData: NoteData = await noteResponse.json();
        loadedNote = noteData.note_content || '';
      }

      setNoteContent(loadedNote);
      setInitialLoadedContent(loadedNote);
      setVideoInfo(videoData);
      setVideoUrl(video_id);

      // Check if subtitles exist
      await checkSubtitles(video_id);

      // Force ChunkViewer to refresh for new video
      chunkViewerKey.current += 1;

      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error loading saved video:', error);
      // Clear saved video if it fails to load
      localStorage.removeItem('currentVideoId');
    } finally {
      setLoading(false);
    }
  };

  const handleFetchVideo = async () => {
    if (!videoUrl.trim()) {
      // toast.error('Please enter a video URL or ID');
      return;
    }

    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        // toast.error('Authentication required');
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

      // Wait for note to complete before showing UI
      const loadedNote = await notePromise;
      setNoteContent(loadedNote);
      setInitialLoadedContent(loadedNote);

      // Set video info after note is loaded
      setVideoInfo(videoData);
      // toast.success(`Loaded: ${videoData.title}`);

      if (loadedNote) {
        // toast.info('Existing note loaded');
      }

      // Check if subtitles exist
      await checkSubtitles(videoData.video_id);

      // Force ChunkViewer to refresh for new video
      chunkViewerKey.current += 1;

      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error fetching video:', error);
      // toast.error(
      //   error instanceof Error ? error.message : 'Failed to fetch video'
      // );
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNote = async () => {
    if (!videoInfo) {
      // toast.error('Please load a video first');
      return;
    }

    setSaving(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        // toast.error('Authentication required');
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
      // toast.success('Note saved successfully');
      setHasUnsavedChanges(false);
      setInitialLoadedContent(noteContent);
    } catch (error) {
      console.error('Error saving note:', error);
      // toast.error(
      //   error instanceof Error ? error.message : 'Failed to save note'
      // );
    } finally {
      setSaving(false);
    }
  };

  const handleEditorChange = (markdown: string) => {
    // Content is already in markdown format from TiptapMarkdownEditor
    setNoteContent(markdown);
    if (videoInfo) {
      // Compare with initial loaded content to determine if there are unsaved changes
      setHasUnsavedChanges(markdown !== initialLoadedContent);
    }
  };

  const checkSubtitles = async (video_id: string, expectedCount?: number) => {
    try {
      const token = await getAccessToken();
      if (!token) return { hasChunks: false, count: 0 };

      const response = await fetch(
        `http://localhost:8000/api/chunks/${video_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        const hasChunks = data.count > 0;

        // If expected count is provided, check if we have all chunks
        if (expectedCount !== undefined) {
          const isComplete = data.count >= expectedCount;
          setHasSubtitles(isComplete);
          return { hasChunks: isComplete, count: data.count };
        }

        setHasSubtitles(hasChunks);
        return { hasChunks, count: data.count };
      }
      return { hasChunks: false, count: 0 };
    } catch (error) {
      console.error('Error checking subtitles:', error);
      return { hasChunks: false, count: 0 };
    }
  };

  const checkAIEnrichment = async (video_id: string) => {
    try {
      const token = await getAccessToken();
      if (!token) return false;

      const response = await fetch(
        `http://localhost:8000/api/chunks/${video_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        // Check if at least one chunk has AI fields populated
        if (data.chunks && data.chunks.length > 0) {
          const hasAI = data.chunks.some(
            (chunk: any) => chunk.short_title || chunk.ai_field_1
          );
          return hasAI;
        }
      }
      return false;
    } catch (error) {
      console.error('Error checking AI enrichment:', error);
      return false;
    }
  };

  const handleProcessSubtitles = async () => {
    if (!videoInfo) return;

    setProcessingSubtitles(true);
    setHasSubtitles(false);
    try {
      const token = await getAccessToken();
      if (!token) {
        // toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        'http://localhost:8000/api/jobs/process-subtitles',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ video_url: videoInfo.video_id }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to start subtitle processing');
      }

      const result = await response.json();
      // toast.success(
      //   'Subtitle processing started! Check backend logs for progress.'
      // );
      console.log('Subtitle processing started:', result);

      // Poll for completion every 3 seconds
      // With bulk operations, all chunks appear atomically - no need for stability check
      let pollCount = 0;
      const maxPolls = 40; // 2 minutes

      const pollInterval = setInterval(async () => {
        pollCount++;
        const result = await checkSubtitles(videoInfo.video_id);

        if (result.hasChunks && result.count > 0) {
          // Chunks found! Since we use bulk insert, all chunks are present
          clearInterval(pollInterval);
          // toast.success(
          //   `Subtitles processed successfully! ${result.count} chunks created.`
          // );
          console.log(
            `Subtitles processed successfully! ${result.count} chunks created.`
          );
          chunkViewerKey.current += 1; // Force ChunkViewer to refresh
        } else if (pollCount >= maxPolls) {
          clearInterval(pollInterval);
          // toast.info(
          //   'Subtitle processing is taking longer than expected. Check backend logs.'
          // );
          console.log('Subtitle processing timeout');
        }
      }, 3000);
    } catch (error) {
      console.error('Subtitle processing error:', error);
      // toast.error('Failed to start subtitle processing');
    } finally {
      setProcessingSubtitles(false);
    }
  };

  const handleProcessAI = async () => {
    if (!videoInfo) return;

    setProcessingAI(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        // toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        'http://localhost:8000/api/jobs/process-ai-enrichment',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ video_url: videoInfo.video_id }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start AI enrichment');
      }

      const result = await response.json();
      // toast.success('AI enrichment started! Check backend logs for progress.');
      console.log('AI enrichment started:', result);

      // Poll to check if AI enrichment is complete
      let pollCount = 0;
      const maxPolls = 60; // 3 minutes (60 * 3 seconds)
      const pollInterval = setInterval(async () => {
        pollCount++;
        const hasAIEnrichment = await checkAIEnrichment(videoInfo.video_id);

        if (hasAIEnrichment) {
          clearInterval(pollInterval);
          setProcessingAI(false);
          chunkViewerKey.current += 1; // Force ChunkViewer to refresh
          // toast.success('AI enrichment complete! Chunks updated.');
          console.log('AI enrichment complete!');
        } else if (pollCount >= maxPolls) {
          clearInterval(pollInterval);
          setProcessingAI(false);
          // toast.info('AI enrichment is taking longer than expected. Manually refresh to see updates.');
          console.log(
            'AI enrichment timeout - manually refresh to see updates'
          );
        }
      }, 3000);
    } catch (error) {
      console.error('AI enrichment error:', error);
      // toast.error(error instanceof Error ? error.message : 'Failed to start AI enrichment');
      setProcessingAI(false);
    }
  };

  const handleProcessVideo = async () => {
    if (!videoInfo) return;

    setProcessingSubtitles(true);
    setProcessingAI(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        // toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        'http://localhost:8000/api/jobs/process-video',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ video_url: videoInfo.video_id }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to create processing job');
      }

      const result = await response.json();
      // toast.success('Video processing started! This may take several minutes.');
      console.log('Processing job created:', result);
    } catch (error) {
      console.error('Processing error:', error);
      // toast.error('Failed to start video processing');
    } finally {
      setProcessingSubtitles(false);
      setProcessingAI(false);
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
        <div className='mb-8'>
          <div className='flex justify-between items-center mb-4'>
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

          {/* Navigation Buttons */}
          <div className='flex gap-2'>
            <Button
              variant='outline'
              size='sm'
              onClick={() => router.push('/filter')}
            >
              <Filter className='mr-2 h-4 w-4' />
              Browse All Videos
            </Button>
            <Button
              variant='outline'
              size='sm'
              onClick={() => router.push('/creator-notes')}
            >
              <User className='mr-2 h-4 w-4' />
              Creator Notes
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
            <div className='bg-card border rounded-lg p-4 space-y-3'>
              <div className='flex justify-between items-start'>
                <div className='space-y-2 flex-1'>
                  <h2 className='text-xl font-semibold'>{videoInfo.title}</h2>
                  <div className='flex gap-4 text-sm text-muted-foreground'>
                    <span>{videoInfo.channel_title}</span>
                    {videoInfo.duration && (
                      <span>
                      {(() => {
                        // Convert ISO 8601 duration (PT1H2M3S) to HH:MM:SS or MM:SS
                        const match = videoInfo.duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
                        if (!match) return videoInfo.duration;
                        
                        const hours = parseInt(match[1] || '0', 10);
                        const minutes = parseInt(match[2] || '0', 10);
                        const seconds = parseInt(match[3] || '0', 10);
                        
                        if (hours > 0) {
                        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                        } else {
                        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
                        }
                      })()}
                      </span>
                    )}
                    {videoInfo.view_count && (
                      <span>
                      {videoInfo.view_count.toLocaleString()}
                      </span>
                    )}
                    {videoInfo.like_count && (
                      <span className="flex items-center gap-1">
                      <ThumbsUp className="h-3 w-3" />
                      {videoInfo.like_count.toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className='flex gap-2'>
                  <Button
                    onClick={handleProcessSubtitles}
                    disabled={processingSubtitles}
                    size='sm'
                    variant='outline'
                  >
                    {processingSubtitles ? (
                      <>
                        <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                        Processing...
                      </>
                    ) : (
                      <>
                        <PlayCircle className='mr-2 h-4 w-4' />
                        Process Subtitles
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={handleProcessAI}
                    disabled={!hasSubtitles || processingAI}
                    size='sm'
                    variant='default'
                  >
                    {processingAI ? (
                      <>
                        <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                        Processing...
                      </>
                    ) : (
                      <>
                        <PlayCircle className='mr-2 h-4 w-4' />
                        AI Enrichment
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Chunks Section */}
        {videoInfo && (
          <div className='mb-6'>
            <div className='flex justify-between items-center mb-4'>
              <h3 className='text-lg font-semibold'>Video Chunks</h3>
              {hasSubtitles && (
                <span className='text-sm text-green-600 font-medium'>
                  ✓ Subtitles available
                </span>
              )}
            </div>
            <ChunkViewer
              key={chunkViewerKey.current}
              videoId={videoInfo.video_id}
            />
          </div>
        )}

        {videoInfo && <Separator className='my-6' />}

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
                onInitialLoad={() => setHasUnsavedChanges(false)}
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
