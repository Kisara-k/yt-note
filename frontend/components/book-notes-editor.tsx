'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { ChunkViewer } from '@/components/chunk-viewer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import {
  Save,
  BookOpen,
  Loader2,
  LogOut,
  Filter,
  User,
  Plus,
  Edit3,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter, useSearchParams } from 'next/navigation';

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
            <Button
              onClick={handleLoadBook}
              disabled={loading || !bookId.trim()}
              className='w-[110px]'
            >
              {loading ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Loading...
                </>
              ) : (
                <>
                  <BookOpen className='mr-2 h-4 w-4' />
                  Load Book
                </>
              )}
            </Button>
          </div>

          {bookInfo && (
            <div className='space-y-3'>
              <div className='bg-card border rounded-lg p-4'>
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
            </div>
          )}
        </div>

        {bookInfo && (
          <div className='space-y-4 mb-6'>
            <div className='flex justify-between items-center'>
              <Label className='text-lg font-semibold'>
                Note{' '}
                {hasUnsavedChanges && <span className='text-amber-500'>*</span>}
              </Label>
              <Button
                onClick={handleSaveNote}
                disabled={saving || !hasUnsavedChanges}
                variant='default'
                size='sm'
                className='w-[110px]'
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
                className='min-h-[150px]'
                placeholder='Start writing your notes here...'
                onInitialLoad={handleInitialLoad}
              />
            </div>
          </div>
        )}

        {bookInfo && <Separator className='my-6' />}

        {bookInfo && (
          <div className='mb-6'>
            <div className='flex justify-between items-center mb-4'>
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
