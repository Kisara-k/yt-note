'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { ChunkViewer } from '@/components/chunk-viewer';
import { NoteEditor } from '@/components/note-editor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
import { useRouter, useSearchParams } from 'next/navigation';
import { CustomTooltip } from '@/components/custom-tooltip';

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
  const hasLoadedInitial = useRef(false);
  const { user, signOut, getAccessToken } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Load video from URL parameter or localStorage on mount
  useEffect(() => {
    // Only run once on mount
    if (hasLoadedInitial.current) return;
    hasLoadedInitial.current = true;

    // Check URL parameter first
    const videoParam = searchParams.get('v');
    if (videoParam) {
      // Load video from URL parameter
      loadVideoById(videoParam);
    } else {
      // Fall back to localStorage
      const savedVideoId = localStorage.getItem('currentVideoId');
      if (savedVideoId) {
        // Auto-load the saved video
        loadVideoById(savedVideoId);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

      // Update URL parameter with the video ID
      router.push(`/video?v=${videoData.video_id}`, { scroll: false });

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

  const handleEditorChange = useCallback(
    (markdown: string) => {
      // Content is already in markdown format from TiptapMarkdownEditor
      setNoteContent(markdown);
      if (videoInfo) {
        // Compare with initial loaded content to determine if there are unsaved changes
        setHasUnsavedChanges(markdown !== initialLoadedContent);
      }
    },
    [videoInfo, initialLoadedContent]
  );

  const handleInitialLoad = useCallback(() => {
    setHasUnsavedChanges(false);
  }, []);

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

  const extractVideoId = (input: string): string | null => {
    // If it's already just a video ID (11 characters, alphanumeric with hyphens and underscores)
    if (/^[a-zA-Z0-9_-]{11}$/.test(input.trim())) {
      return input.trim();
    }

    // Try to extract from various YouTube URL formats
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
      /youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/,
    ];

    for (const pattern of patterns) {
      const match = input.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }

    return null;
  };

  const handlePaste = async (e: React.ClipboardEvent<HTMLInputElement>) => {
    const pastedText = e.clipboardData.getData('text');
    const videoId = extractVideoId(pastedText);

    if (videoId) {
      // Valid video ID found, attempt to load it
      e.preventDefault(); // Prevent default paste
      setVideoUrl(pastedText); // Keep the pasted content in the box

      // Automatically fetch the video
      setTimeout(async () => {
        setLoading(true);
        try {
          const token = await getAccessToken();
          if (!token) {
            setLoading(false);
            return;
          }

          const videoResponse = await fetch('http://localhost:8000/api/video', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ video_url: pastedText }),
          });

          if (!videoResponse.ok) {
            // If failed, keep the pasted content but don't change the loaded video
            const error = await videoResponse.json();
            console.error('Failed to load video:', error);
            setLoading(false);
            return;
          }

          const videoData: VideoInfo = await videoResponse.json();

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

          const loadedNote = await notePromise;
          setNoteContent(loadedNote);
          setInitialLoadedContent(loadedNote);
          setVideoInfo(videoData);
          router.push(`/video?v=${videoData.video_id}`, { scroll: false });

          await checkSubtitles(videoData.video_id);
          chunkViewerKey.current += 1;
          setHasUnsavedChanges(false);
        } catch (error) {
          console.error('Error fetching video on paste:', error);
        } finally {
          setLoading(false);
        }
      }, 0);
    }
    // If not valid, let the default paste happen and keep content in box
  };

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto p-6 max-w-7xl'>
        <div className='mb-8'>
          <div className='flex justify-between items-center mb-4'>
            <div className='flex items-center gap-4'>
              <p className='text-muted-foreground'>
                Enter a YouTube video URL or ID to create notes
              </p>
            </div>

            {/* Navigation Buttons - Centered */}
            <div className='flex items-center gap-2'>
              <Button
                variant='outline'
                size='sm'
                onClick={() => router.push('/video/filter')}
              >
                <Filter className='mr-2 h-4 w-4' />
                All Videos
              </Button>
              <Button
                variant='outline'
                size='sm'
                onClick={() => router.push('/video/creator-notes')}
              >
                <User className='mr-2 h-4 w-4' />
                Creators
              </Button>
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
                onPaste={handlePaste}
                disabled={loading}
                className='text-base'
              />
            </div>
            <Button
              onClick={handleFetchVideo}
              disabled={loading || !videoUrl.trim()}
              className='w-[110px]'
            >
              {loading ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Loading...
                </>
              ) : (
                <>
                  <Video className='mr-2 h-4 w-4' />
                  Load YT
                </>
              )}
            </Button>
          </div>

          {/* Video Info Display */}
          {videoInfo && (
            <div className='space-y-3'>
              <div className='flex gap-3'>
                <div className='bg-card border rounded-lg p-4 flex-1'>
                  <div className='space-y-2'>
                    <h2 className='text-xl font-semibold'>{videoInfo.title}</h2>
                    <div className='flex gap-4 text-sm text-muted-foreground'>
                      <span>{videoInfo.channel_title}</span>
                      {videoInfo.duration && (
                        <span>
                          {(() => {
                            // Convert ISO 8601 duration (PT1H2M3S) to HH:MM:SS or MM:SS
                            const match = videoInfo.duration.match(
                              /PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/
                            );
                            if (!match) return videoInfo.duration;

                            const hours = parseInt(match[1] || '0', 10);
                            const minutes = parseInt(match[2] || '0', 10);
                            const seconds = parseInt(match[3] || '0', 10);

                            if (hours > 0) {
                              return `${hours}:${minutes
                                .toString()
                                .padStart(2, '0')}:${seconds
                                .toString()
                                .padStart(2, '0')}`;
                            } else {
                              return `${minutes}:${seconds
                                .toString()
                                .padStart(2, '0')}`;
                            }
                          })()}
                        </span>
                      )}
                      {videoInfo.view_count && (
                        <span>{videoInfo.view_count.toLocaleString()}</span>
                      )}
                      {videoInfo.like_count && (
                        <span className='flex items-center gap-1'>
                          <ThumbsUp className='h-3 w-3' />
                          {videoInfo.like_count.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className='flex flex-col gap-2'>
                  <CustomTooltip content='Download and process video subtitles into chunks'>
                    <Button
                      onClick={handleProcessSubtitles}
                      disabled={processingSubtitles}
                      size='sm'
                      variant='outline'
                      className='w-[110px] justify-start'
                    >
                      {processingSubtitles ? (
                        <>
                          <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                          Processing...
                        </>
                      ) : (
                        <>
                          <PlayCircle className='mr-2 h-4 w-4' />
                          Subtitles
                        </>
                      )}
                    </Button>
                  </CustomTooltip>
                  <CustomTooltip content='Generate AI enrichment for all video chunks'>
                    <Button
                      onClick={handleProcessAI}
                      disabled={!hasSubtitles || processingAI}
                      size='sm'
                      variant='default'
                      className='w-[110px] justify-start'
                    >
                      {processingAI ? (
                        <>
                          <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                          Processing...
                        </>
                      ) : (
                        <>
                          <PlayCircle className='mr-2 h-4 w-4' />
                          AI
                        </>
                      )}
                    </Button>
                  </CustomTooltip>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Editor Section */}
        {videoInfo && (
          <div className='mb-6'>
            <NoteEditor
              title='Note'
              value={noteContent}
              onChange={handleEditorChange}
              onSave={handleSaveNote}
              onInitialLoad={handleInitialLoad}
              isSaving={saving}
              hasUnsavedChanges={hasUnsavedChanges}
              placeholder='Start writing your notes here...'
            />
          </div>
        )}

        {videoInfo && <Separator className='my-6' />}

        {/* Chunks Section */}
        {videoInfo && (
          <div className='mb-6'>
            <div className='flex justify-between items-center mb-4'>
              <h3 className='text-lg font-semibold'>Video Chunks</h3>
              {/* {hasSubtitles && (
                <span className='text-sm text-green-600 font-medium'>
                  ✓ Subtitles available
                </span>
              )} */}
            </div>
            <ChunkViewer
              key={chunkViewerKey.current}
              videoId={videoInfo.video_id}
            />
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
