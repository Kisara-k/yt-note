'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { ChunkViewer } from '@/components/chunk-viewer';
import { NoteEditor } from '@/components/note-editor';
import { Button } from '@/components/ui/button';
import { ActionButton } from '@/components/ui/action-button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Save,
  BookOpen,
  Loader2,
  LogOut,
  Filter,
  User,
  Plus,
  Edit3,
  Sparkles,
  PlayCircle,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter, useSearchParams } from 'next/navigation';
import { CustomTooltip } from '@/components/custom-tooltip';

interface BookInfo {
  id: string;
  title: string;
  author?: string;
  publisher?: string;
  publication_year?: number;
  isbn?: string;
  description?: string;
  tags?: string[];
  created_at?: string;
}

interface NoteData {
  book_id: string;
  note_content: string | null;
  created_at?: string;
  updated_at?: string;
}

export function BookNotesEditor() {
  const [bookId, setBookId] = useState('');
  const [bookInfo, setBookInfo] = useState<BookInfo | null>(null);
  const [noteContent, setNoteContent] = useState('');
  const [initialLoadedContent, setInitialLoadedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [processingAllChapters, setProcessingAllChapters] = useState(false);
  const chunkViewerKey = useRef(0);
  const hasLoadedInitial = useRef(false);
  const { user, signOut, getAccessToken } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (hasLoadedInitial.current) return;
    hasLoadedInitial.current = true;

    const bookParam = searchParams.get('b');
    if (bookParam) {
      loadBookById(bookParam);
    } else {
      const savedBookId = localStorage.getItem('currentBookId');
      if (savedBookId) {
        loadBookById(savedBookId);
      }
    }
  }, []);

  useEffect(() => {
    if (bookInfo) {
      localStorage.setItem('currentBookId', bookInfo.id);
    }
  }, [bookInfo]);

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Failed to sign out:', error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && bookId.trim()) {
      e.preventDefault();
      handleLoadBook();
    }
  };

  const loadBookById = async (book_id: string) => {
    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        setLoading(false);
        return;
      }

      const bookResponse = await fetch(
        `http://localhost:8000/api/book/${book_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!bookResponse.ok) {
        throw new Error('Book not found');
      }

      const bookData: BookInfo = await bookResponse.json();

      const notePromise = fetch(
        `http://localhost:8000/api/book/${book_id}/note`,
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
      setBookInfo(bookData);

      router.push(`/book?b=${bookData.id}`, { scroll: false });

      chunkViewerKey.current += 1;

      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error loading book:', error);
      localStorage.removeItem('currentBookId');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadBook = async () => {
    if (!bookId.trim()) return;
    await loadBookById(bookId.trim());
  };

  const handleSaveNote = async () => {
    if (!bookInfo) {
      return;
    }

    setSaving(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        setSaving(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/book/note', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          book_id: bookInfo.id,
          note: noteContent,
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
      if (bookInfo) {
        setHasUnsavedChanges(markdown !== initialLoadedContent);
      }
    },
    [bookInfo, initialLoadedContent]
  );

  const handleInitialLoad = useCallback(() => {
    setHasUnsavedChanges(false);
  }, []);

  const handleProcessAllChapters = async () => {
    if (!bookInfo) return;

    setProcessingAllChapters(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        return;
      }

      const response = await fetch(
        'http://localhost:8000/api/jobs/process-book-all-chapters-ai',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ book_id: bookInfo.id }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start AI enrichment');
      }

      const result = await response.json();
      console.log('AI enrichment started for all chapters:', result);

      // Poll to check if AI enrichment is complete
      let pollCount = 0;
      const maxPolls = 60; // 3 minutes (60 * 3 seconds)
      const pollInterval = setInterval(async () => {
        pollCount++;

        // Refresh the chapter viewer to check for updates
        chunkViewerKey.current += 1;

        if (pollCount >= maxPolls) {
          clearInterval(pollInterval);
          setProcessingAllChapters(false);
          console.log(
            'AI enrichment timeout - manually refresh to see updates'
          );
        }
      }, 3000);

      // Stop processing state after initial call
      setTimeout(() => {
        setProcessingAllChapters(false);
      }, 5000);
    } catch (error) {
      console.error('AI enrichment error:', error);
      setProcessingAllChapters(false);
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto p-6 max-w-7xl'>
        <div className='mb-8'>
          <div className='flex justify-between items-center mb-4'>
            <div className='flex items-center gap-4'>
              <p className='text-muted-foreground'>
                Enter a book ID to create notes
              </p>
            </div>

            {/* Navigation Buttons - Centered */}
            <div className='flex items-center gap-2'>
              <Button
                variant='outline'
                size='sm'
                onClick={() => router.push('/book/filter')}
              >
                <Filter className='mr-2 h-4 w-4' />
                All Books
              </Button>
              <Button
                variant='outline'
                size='sm'
                onClick={() => router.push('/book/add')}
              >
                <Plus className='mr-2 h-4 w-4' />
                Add Book
              </Button>
              {bookInfo && (
                <Button
                  variant='outline'
                  size='sm'
                  onClick={() => router.push(`/book/chunks?b=${bookInfo.id}`)}
                >
                  <Edit3 className='mr-2 h-4 w-4' />
                  Edit Chunks
                </Button>
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

        {/* Book ID Input */}
        <div className='mb-8 space-y-4'>
          <div className='flex gap-3'>
            <div className='flex-1'>
              <Label htmlFor='book-id' className='sr-only'>
                Book ID
              </Label>
              <Input
                id='book-id'
                type='text'
                placeholder='Enter Book ID (e.g., practical_guide_123)'
                value={bookId}
                onChange={(e) => setBookId(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                className='text-base'
              />
            </div>
            <ActionButton
              onClick={handleLoadBook}
              disabled={loading || !bookId.trim()}
              loading={loading}
              loadingText='Loading...'
              icon={BookOpen}
            >
              Load Book
            </ActionButton>
          </div>

          {bookInfo && (
            <div className='space-y-3'>
              <div className='flex gap-3'>
                <div className='bg-card border rounded-lg p-4 flex-1'>
                  <div className='space-y-2'>
                    <h2 className='text-xl font-semibold'>{bookInfo.title}</h2>
                    <div className='flex gap-4 text-sm text-muted-foreground'>
                      {bookInfo.author && <span>by {bookInfo.author}</span>}
                      {bookInfo.publisher && <span>{bookInfo.publisher}</span>}
                      {bookInfo.publication_year && (
                        <span>{bookInfo.publication_year}</span>
                      )}
                    </div>
                    {bookInfo.description && (
                      <p className='text-sm text-muted-foreground mt-2'>
                        {bookInfo.description}
                      </p>
                    )}
                    {bookInfo.tags && bookInfo.tags.length > 0 && (
                      <div className='flex gap-2 mt-2 flex-wrap'>
                        {bookInfo.tags.map((tag, i) => (
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
                  <CustomTooltip content='Generate AI enrichment for all book chapters'>
                    <Button
                      onClick={handleProcessAllChapters}
                      disabled={processingAllChapters}
                      size='sm'
                      variant='default'
                      className='w-[110px] justify-start'
                    >
                      {processingAllChapters ? (
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

        {bookInfo && (
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

        {bookInfo && <Separator className='my-6' />}

        {bookInfo && (
          <div className='mb-6'>
            <div className='mb-4'>
              <h3 className='text-lg font-semibold'>Book Chapters</h3>
            </div>
            <ChunkViewer
              key={chunkViewerKey.current}
              bookId={bookInfo.id}
              isBook={true}
            />
          </div>
        )}

        {!bookInfo && !loading && (
          <div className='text-center py-12 text-muted-foreground'>
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
          </div>
        )}
      </div>
    </div>
  );
}
