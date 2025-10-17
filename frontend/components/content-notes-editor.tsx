'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { ChunkViewer } from '@/components/chunk-viewer';
import { ChunkTextToggle } from '@/components/chunk-text-toggle';
import { NoteEditor } from '@/components/note-editor';
import { Button } from '@/components/ui/button';
import { ActionButton } from '@/components/ui/action-button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Save,
  Video,
  BookOpen,
  LogOut,
  PlayCircle,
  Filter,
  User,
  ThumbsUp,
  Plus,
  Sparkles,
  Edit3,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter, useSearchParams } from 'next/navigation';
import { CustomTooltip } from '@/components/custom-tooltip';

type ContentType = 'video' | 'book';

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

interface BookInfo {
  id: string;
  title: string;
  author?: string;
  publisher?: string;
  publication_year?: number;
  isbn?: string;
  description?: string;
  tags?: string[];
  type?: string;
  created_at?: string;
}

interface NoteData {
  video_id?: string;
  book_id?: string;
  note_content: string | null;
  created_at?: string;
  updated_at?: string;
}

interface ContentNotesEditorProps {
  contentType: ContentType;
}

export function ContentNotesEditor({ contentType }: ContentNotesEditorProps) {
  const isVideo = contentType === 'video';
  const [inputValue, setInputValue] = useState('');
  const [contentInfo, setContentInfo] = useState<VideoInfo | BookInfo | null>(
    null
  );
  const [noteContent, setNoteContent] = useState('');
  const [initialLoadedContent, setInitialLoadedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [processingSubtitles, setProcessingSubtitles] = useState(false);
  const [processingAI, setProcessingAI] = useState(false);
  const [hasSubtitles, setHasSubtitles] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const chunkViewerKey = useRef(0);
  const [refreshAIFields, setRefreshAIFields] = useState(0);
  const hasLoadedInitial = useRef(false);
  const { user, signOut, getAccessToken } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Load content from URL parameter or localStorage on mount
  useEffect(() => {
    if (hasLoadedInitial.current) return;
    hasLoadedInitial.current = true;

    const paramKey = isVideo ? 'v' : 'b';
    const contentParam = searchParams.get(paramKey);
    if (contentParam) {
      loadContentById(contentParam);
    } else {
      const storageKey = isVideo ? 'currentVideoId' : 'currentBookId';
      const savedId = localStorage.getItem(storageKey);
      if (savedId) {
        loadContentById(savedId);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Save content to localStorage when it changes
  useEffect(() => {
    if (contentInfo) {
      const storageKey = isVideo ? 'currentVideoId' : 'currentBookId';
      const id = isVideo
        ? (contentInfo as VideoInfo).video_id
        : (contentInfo as BookInfo).id;
      localStorage.setItem(storageKey, id);
    }
  }, [contentInfo, isVideo]);

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Failed to sign out:', error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      if (isVideo) {
        handleFetchVideo();
      } else {
        handleLoadBook();
      }
    }
  };

  const loadContentById = async (id: string) => {
    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        setLoading(false);
        return;
      }

      const endpoint = isVideo
        ? `http://localhost:8000/api/video/${id}`
        : `http://localhost:8000/api/book/${id}`;

      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`${isVideo ? 'Video' : 'Book'} not found`);
      }

      const data: VideoInfo | BookInfo = await response.json();

      const noteEndpoint = isVideo
        ? `http://localhost:8000/api/note/${id}`
        : `http://localhost:8000/api/book/${id}/note`;

      const notePromise = fetch(noteEndpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
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
      setContentInfo(data);

      const routePath = isVideo ? '/video' : '/book';
      const paramKey = isVideo ? 'v' : 'b';
      const paramValue = isVideo
        ? (data as VideoInfo).video_id
        : (data as BookInfo).id;
      router.push(`${routePath}?${paramKey}=${paramValue}`, { scroll: false });

      if (isVideo) {
        await checkSubtitles((data as VideoInfo).video_id);
      }

      chunkViewerKey.current += 1;
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error(`Error loading ${isVideo ? 'video' : 'book'}:`, error);
      const storageKey = isVideo ? 'currentVideoId' : 'currentBookId';
      localStorage.removeItem(storageKey);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchVideo = async () => {
    if (!inputValue.trim()) return;

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
        body: JSON.stringify({ video_url: inputValue }),
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
      setContentInfo(videoData);

      router.push(`/video?v=${videoData.video_id}`, { scroll: false });

      await checkSubtitles(videoData.video_id);
      chunkViewerKey.current += 1;
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error fetching video:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadBook = async () => {
    if (!inputValue.trim()) return;
    await loadContentById(inputValue.trim());
  };

  const handleSaveNote = async () => {
    if (!contentInfo) return;

    setSaving(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        setSaving(false);
        return;
      }

      const id = isVideo
        ? (contentInfo as VideoInfo).video_id
        : (contentInfo as BookInfo).id;

      const endpoint = isVideo
        ? 'http://localhost:8000/api/note'
        : 'http://localhost:8000/api/book/note';

      const body = isVideo
        ? {
            video_id: id,
            note_content: noteContent,
          }
        : {
            book_id: id,
            note_content: noteContent,
          };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const error = await response.json();
        const errorMessage =
          typeof error.detail === 'string'
            ? error.detail
            : error.error || error.message || 'Failed to save note';
        throw new Error(errorMessage);
      }

      setHasUnsavedChanges(false);
      setInitialLoadedContent(noteContent);
    } catch (error) {
      console.error('Error saving note:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleEditorChange = useCallback(
    (markdown: string) => {
      setNoteContent(markdown);
      if (contentInfo) {
        setHasUnsavedChanges(markdown !== initialLoadedContent);
      }
    },
    [contentInfo, initialLoadedContent]
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

  const loadAllChunksAIFields = async (id: string) => {
    try {
      const token = await getAccessToken();
      if (!token) return null;

      // Use lightweight AI status endpoint for polling
      const endpoint = isVideo
        ? `http://localhost:8000/api/chunks/${id}/ai-status`
        : `http://localhost:8000/api/book/${id}/chapters/ai-status`;

      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const items = isVideo ? data.chunks : data.chapters;
        if (items && items.length > 0) {
          return items.map((item: any) =>
            isVideo
              ? {
                  chunk_id: item.chunk_id,
                  short_title: item.short_title || '',
                  ai_field_1: item.ai_field_1 || '',
                }
              : {
                  chapter_id: item.chapter_id,
                  chapter_title: item.chapter_title || '',
                  ai_field_1: item.ai_field_1 || '',
                }
          );
        }
      }
      return null;
    } catch (error) {
      console.error('Error loading AI fields:', error);
      return null;
    }
  };

  const checkAIEnrichment = async (
    id: string,
    previousData?: Array<{
      chunk_id?: number;
      chapter_id?: number;
      short_title?: string;
      chapter_title?: string;
      ai_field_1: string;
    }>
  ) => {
    const currentData = await loadAllChunksAIFields(id);
    if (!currentData || currentData.length === 0) return false;

    if (!previousData) {
      return currentData.some((item: any) =>
        isVideo
          ? item.short_title || item.ai_field_1
          : item.chapter_title || item.ai_field_1
      );
    }

    const hasNewData = currentData.some((current: any) => {
      const idKey = isVideo ? 'chunk_id' : 'chapter_id';
      const titleKey = isVideo ? 'short_title' : 'chapter_title';
      const previous = previousData.find((p) => p[idKey] === current[idKey]);
      if (!previous) return false;
      return (
        current[titleKey] !== previous[titleKey] ||
        current.ai_field_1 !== previous.ai_field_1
      );
    });

    return hasNewData;
  };

  const handleProcessSubtitles = async () => {
    if (!contentInfo || !isVideo) return;

    setProcessingSubtitles(true);
    setHasSubtitles(false);
    try {
      const token = await getAccessToken();
      if (!token) return;

      const videoId = (contentInfo as VideoInfo).video_id;
      const response = await fetch(
        'http://localhost:8000/api/jobs/process-subtitles',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ video_url: videoId }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to start subtitle processing');
      }

      const result = await response.json();
      console.log('Subtitle processing started:', result);

      let pollCount = 0;
      const maxPolls = 40;

      const pollInterval = setInterval(async () => {
        pollCount++;
        const result = await checkSubtitles(videoId);

        if (result.hasChunks && result.count > 0) {
          clearInterval(pollInterval);
          setProcessingSubtitles(false);
          console.log(
            `Subtitles processed successfully! ${result.count} chunks created.`
          );
          chunkViewerKey.current += 1;
        } else if (pollCount >= maxPolls) {
          clearInterval(pollInterval);
          setProcessingSubtitles(false);
          console.log('Subtitle processing timeout');
        }
      }, 3000);
    } catch (error) {
      console.error('Subtitle processing error:', error);
      setProcessingSubtitles(false);
    }
  };

  const handleProcessAI = async () => {
    if (!contentInfo) return;

    setProcessingAI(true);
    try {
      const token = await getAccessToken();
      if (!token) return;

      const id = isVideo
        ? (contentInfo as VideoInfo).video_id
        : (contentInfo as BookInfo).id;

      const endpoint = isVideo
        ? 'http://localhost:8000/api/jobs/process-video-all-chunks-ai'
        : 'http://localhost:8000/api/jobs/process-book-all-chapters-ai';

      const body = isVideo ? { video_id: id } : { book_id: id };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start AI enrichment');
      }

      const result = await response.json();
      console.log('AI enrichment started:', result);

      const currentAIState = await loadAllChunksAIFields(id);

      let pollCount = 0;
      const maxPolls = 180;
      let enrichmentComplete = false; // Flag to prevent duplicate processing
      const pollInterval = setInterval(async () => {
        if (enrichmentComplete) return; // Skip if already completed

        pollCount++;
        const hasAIEnrichment = await checkAIEnrichment(
          id,
          currentAIState || undefined
        );

        // Check flag again after async operation completes (prevent race condition)
        if (enrichmentComplete) return;

        if (hasAIEnrichment) {
          enrichmentComplete = true; // Set flag immediately
          clearInterval(pollInterval);
          setProcessingAI(false);
          setRefreshAIFields((prev) => prev + 1);
          console.log('AI enrichment complete!');
        } else if (pollCount >= maxPolls) {
          clearInterval(pollInterval);
          setProcessingAI(false);
          console.log(
            'AI enrichment timeout - manually refresh to see updates'
          );
        }
      }, 1000);
    } catch (error) {
      console.error('AI enrichment error:', error);
      setProcessingAI(false);
    }
  };

  const handlePaste = async (e: React.ClipboardEvent<HTMLInputElement>) => {
    if (!isVideo) return;

    const pastedText = e.clipboardData.getData('text');
    const extractVideoId = (input: string): string | null => {
      if (/^[a-zA-Z0-9_-]{11}$/.test(input.trim())) {
        return input.trim();
      }
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

    const videoId = extractVideoId(pastedText);
    if (videoId) {
      e.preventDefault();
      setInputValue(pastedText);
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

          if (videoResponse.ok) {
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
            setContentInfo(videoData);
            setInputValue(pastedText);

            router.push(`/video?v=${videoData.video_id}`, { scroll: false });

            await checkSubtitles(videoData.video_id);
            chunkViewerKey.current += 1;
            setHasUnsavedChanges(false);
          }
        } catch (error) {
          console.error('Error auto-loading video:', error);
        } finally {
          setLoading(false);
        }
      }, 100);
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto py-8 px-4'>
        <div className='mb-8'>
          <div className='flex justify-between items-center mb-4'>
            <div className='flex items-center gap-4'>
              <p className='text-muted-foreground'>
                {isVideo
                  ? 'Enter a YouTube video URL or ID to create notes'
                  : 'Enter a Book ID to create notes'}
              </p>
            </div>

            <div className='flex items-center gap-2'>
              <ChunkTextToggle />
              <Button
                variant='outline'
                size='sm'
                onClick={() =>
                  router.push(isVideo ? '/video/filter' : '/book/filter')
                }
              >
                <Filter className='mr-2 h-4 w-4' />
                All {isVideo ? 'Videos' : 'Books'}
              </Button>
              {isVideo && (
                <Button
                  variant='outline'
                  size='sm'
                  onClick={() => router.push('/video/creator-notes')}
                >
                  <User className='mr-2 h-4 w-4' />
                  Creators
                </Button>
              )}
              {!isVideo && (
                <>
                  <Button
                    variant='outline'
                    size='sm'
                    onClick={() => router.push('/book/add')}
                  >
                    <Plus className='mr-2 h-4 w-4' />
                    Add Book
                  </Button>
                  <Button
                    variant='outline'
                    size='sm'
                    onClick={() => {
                      if (contentInfo) {
                        router.push(
                          `/book/chunks?b=${(contentInfo as BookInfo).id}`
                        );
                      }
                    }}
                    disabled={!contentInfo}
                  >
                    <Edit3 className='mr-2 h-4 w-4' />
                    Edit Chunks
                  </Button>
                </>
              )}
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

        {/* Input */}
        <div className='mb-6 space-y-4'>
          <div className='flex gap-2'>
            <div className='flex-1'>
              <Label htmlFor='content-input' className='sr-only'>
                {isVideo ? 'Video URL or ID' : 'Book ID'}
              </Label>
              <Input
                id='content-input'
                type='text'
                placeholder={
                  isVideo
                    ? 'Enter YouTube URL or Video ID (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)'
                    : 'Enter Book ID (e.g., practical_guide_123)'
                }
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onPaste={handlePaste}
                disabled={loading}
                className='text-base'
              />
            </div>
            <ActionButton
              onClick={isVideo ? handleFetchVideo : handleLoadBook}
              disabled={loading || !inputValue.trim()}
              loading={loading}
              loadingText='Loading...'
              icon={isVideo ? Video : BookOpen}
            >
              Load {isVideo ? 'YT' : 'Book'}
            </ActionButton>
          </div>

          {/* Content Info Display */}
          {contentInfo && (
            <div className='space-y-3'>
              <div className='flex gap-3'>
                <div className='bg-card border rounded-lg p-4 flex-1'>
                  <div className='space-y-2'>
                    <h2 className='text-xl font-semibold'>
                      {isVideo
                        ? (contentInfo as VideoInfo).title
                        : (contentInfo as BookInfo).title}
                    </h2>
                    <div className='flex gap-4 text-sm text-muted-foreground'>
                      {isVideo ? (
                        <>
                          <span>
                            {(contentInfo as VideoInfo).channel_title}
                          </span>
                          {(contentInfo as VideoInfo).duration && (
                            <span>
                              {(() => {
                                const match = (
                                  contentInfo as VideoInfo
                                ).duration!.match(
                                  /PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/
                                );
                                if (!match)
                                  return (contentInfo as VideoInfo).duration;

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
                          {(contentInfo as VideoInfo).view_count && (
                            <span>
                              {(
                                contentInfo as VideoInfo
                              ).view_count!.toLocaleString()}
                            </span>
                          )}
                          {(contentInfo as VideoInfo).like_count && (
                            <span className='flex items-center gap-1'>
                              <ThumbsUp className='h-3 w-3' />
                              {(
                                contentInfo as VideoInfo
                              ).like_count!.toLocaleString()}
                            </span>
                          )}
                        </>
                      ) : (
                        <>
                          {(contentInfo as BookInfo).type && (
                            <span
                              className={`text-xs px-2 py-1 rounded-full ${
                                (contentInfo as BookInfo).type === 'lecture'
                                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                                  : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                              }`}
                            >
                              {(contentInfo as BookInfo).type === 'lecture'
                                ? '📚 Lecture'
                                : '📖 Book'}
                            </span>
                          )}
                          {(contentInfo as BookInfo).author && (
                            <span>by {(contentInfo as BookInfo).author}</span>
                          )}
                          {(contentInfo as BookInfo).publisher && (
                            <span>{(contentInfo as BookInfo).publisher}</span>
                          )}
                          {(contentInfo as BookInfo).publication_year && (
                            <span>
                              {(contentInfo as BookInfo).publication_year}
                            </span>
                          )}
                        </>
                      )}
                    </div>
                    {!isVideo && (contentInfo as BookInfo).description && (
                      <p className='text-sm text-muted-foreground mt-2'>
                        {(contentInfo as BookInfo).description}
                      </p>
                    )}
                    {!isVideo &&
                      (contentInfo as BookInfo).tags &&
                      (contentInfo as BookInfo).tags!.length > 0 && (
                        <div className='flex gap-2 mt-2 flex-wrap'>
                          {(contentInfo as BookInfo).tags!.map((tag, i) => (
                            <span
                              key={i}
                              className='text-xs bg-secondary px-2 py-1 rounded'
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                  </div>
                </div>

                <div className='flex flex-col gap-2'>
                  {isVideo && (
                    <CustomTooltip content='Download and process video subtitles into chunks'>
                      <ActionButton
                        onClick={handleProcessSubtitles}
                        disabled={processingSubtitles}
                        loading={processingSubtitles}
                        icon={PlayCircle}
                      >
                        Subtitles
                      </ActionButton>
                    </CustomTooltip>
                  )}
                  <CustomTooltip
                    content={`Generate AI enrichment for all ${
                      isVideo ? 'video chunks' : 'book chapters'
                    }`}
                  >
                    <ActionButton
                      onClick={handleProcessAI}
                      disabled={(isVideo && !hasSubtitles) || processingAI}
                      loading={processingAI}
                      icon={Sparkles}
                    >
                      AI
                    </ActionButton>
                  </CustomTooltip>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Editor Section */}
        {contentInfo && (
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

        {contentInfo && <Separator className='my-6' />}

        {/* Chunks/Chapters Section */}
        {contentInfo && (
          <div className='mb-6'>
            <div className='flex justify-between items-center mb-4'>
              <h3 className='text-lg font-semibold'>
                {isVideo ? 'Video Chunks' : 'Book Chapters'}
              </h3>
            </div>
            <ChunkViewer
              key={chunkViewerKey.current}
              videoId={
                isVideo ? (contentInfo as VideoInfo).video_id : undefined
              }
              bookId={isVideo ? undefined : (contentInfo as BookInfo).id}
              isBook={!isVideo}
              refreshAIFields={refreshAIFields}
            />
          </div>
        )}

        {/* Empty State */}
        {!contentInfo && !loading && (
          <div className='text-center py-12 text-muted-foreground'>
            {isVideo ? (
              <>
                <Video className='h-16 w-16 mx-auto mb-4 opacity-20' />
                <p className='text-lg'>
                  Enter a video URL above to get started
                </p>
              </>
            ) : (
              <>
                <BookOpen className='h-16 w-16 mx-auto mb-4 opacity-20' />
                <p className='text-lg'>Enter a book ID above to get started</p>
                <p className='text-sm mt-2'>
                  or{' '}
                  <Button
                    variant='link'
                    className='p-0 h-auto'
                    onClick={() => router.push('/book/add')}
                  >
                    add a new book
                  </Button>
                </p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
