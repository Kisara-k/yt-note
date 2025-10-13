'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { ChunkViewer } from '@/components/chunk-viewer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Save, BookOpen, Loader2, LogOut, Upload, User } from 'lucide-react';
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
  const [bookTitle, setBookTitle] = useState('');
  const [bookAuthor, setBookAuthor] = useState('');
  const [bookDescription, setBookDescription] = useState('');
  const [bookJson, setBookJson] = useState('');
  const [bookInfo, setBookInfo] = useState<BookInfo | null>(null);
  const [noteContent, setNoteContent] = useState('');
  const [initialLoadedContent, setInitialLoadedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const chunkViewerKey = useRef(0);
  const hasLoadedInitial = useRef(false);
  const { user, signOut, getAccessToken } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Load book from URL parameter or localStorage on mount
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Save book to localStorage when it changes
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

  const loadBookById = async (book_id: string) => {
    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        setLoading(false);
        return;
      }

      // Fetch book metadata
      const bookResponse = await fetch(
        `http://localhost:8000/api/book/${book_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!bookResponse.ok) {
        throw new Error('Failed to load book');
      }

      const bookData: BookInfo = await bookResponse.json();

      // Load note
      const noteResponse = await fetch(
        `http://localhost:8000/api/book/${book_id}/note`,
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
      setBookInfo(bookData);
      setBookId(book_id);

      // Force ChunkViewer to refresh for new book
      chunkViewerKey.current += 1;

      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error loading book:', error);
      localStorage.removeItem('currentBookId');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadBook = async () => {
    if (!bookId.trim() || !bookTitle.trim() || !bookJson.trim()) {
      return;
    }

    setUploading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        setUploading(false);
        return;
      }

      // Parse JSON to extract chapters
      let chaptersData;
      try {
        chaptersData = JSON.parse(bookJson);
        if (!Array.isArray(chaptersData)) {
          throw new Error('JSON must be an array of chapters');
        }
      } catch {
        throw new Error(
          'Invalid JSON format. Expected array of {chapter_title, chapter_text}'
        );
      }

      // Upload book
      const response = await fetch('http://localhost:8000/api/book', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          book_id: bookId,
          title: bookTitle,
          author: bookAuthor || null,
          description: bookDescription || null,
          chapters: chaptersData,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        const errorMessage =
          typeof error.detail === 'string'
            ? error.detail
            : error.error || error.message || 'Failed to upload book';
        throw new Error(errorMessage);
      }

      await response.json();

      // Load the newly created book
      await loadBookById(bookId);

      // Update URL
      router.push(`/books?b=${bookId}`, { scroll: false });

      // Clear form
      setBookJson('');
      setBookTitle('');
      setBookAuthor('');
      setBookDescription('');
    } catch (error) {
      console.error('Error uploading book:', error);
      alert(error instanceof Error ? error.message : 'Failed to upload book');
    } finally {
      setUploading(false);
    }
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
      {/* Header */}
      <div className='border-b bg-card'>
        <div className='container mx-auto px-6 py-4'>
          <div className='flex justify-between items-center'>
            <div className='flex items-center gap-3'>
              <BookOpen className='h-6 w-6' />
              <h1 className='text-2xl font-bold'>Book Notes</h1>
            </div>
            <div className='flex items-center gap-4'>
              <div className='flex items-center gap-2 text-sm'>
                <User className='h-4 w-4' />
                <span className='text-muted-foreground'>{user?.email}</span>
              </div>
              <Button onClick={handleSignOut} variant='outline' size='sm'>
                <LogOut className='mr-2 h-4 w-4' />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className='container mx-auto px-6 py-6'>
        {/* Upload Book Section */}
        <div className='bg-card border rounded-lg p-6 mb-6'>
          <h2 className='text-lg font-semibold mb-4'>Upload New Book</h2>
          <div className='space-y-4'>
            <div className='grid grid-cols-2 gap-4'>
              <div>
                <Label htmlFor='book-id'>Book ID (short string)</Label>
                <Input
                  id='book-id'
                  type='text'
                  placeholder='e.g., the_subtle_art'
                  value={bookId}
                  onChange={(e) => setBookId(e.target.value)}
                  disabled={uploading || loading}
                />
              </div>
              <div>
                <Label htmlFor='book-title'>Title</Label>
                <Input
                  id='book-title'
                  type='text'
                  placeholder='Book title'
                  value={bookTitle}
                  onChange={(e) => setBookTitle(e.target.value)}
                  disabled={uploading || loading}
                />
              </div>
            </div>
            <div className='grid grid-cols-2 gap-4'>
              <div>
                <Label htmlFor='book-author'>Author</Label>
                <Input
                  id='book-author'
                  type='text'
                  placeholder='Author name'
                  value={bookAuthor}
                  onChange={(e) => setBookAuthor(e.target.value)}
                  disabled={uploading || loading}
                />
              </div>
              <div>
                <Label htmlFor='book-description'>Description</Label>
                <Input
                  id='book-description'
                  type='text'
                  placeholder='Brief description'
                  value={bookDescription}
                  onChange={(e) => setBookDescription(e.target.value)}
                  disabled={uploading || loading}
                />
              </div>
            </div>
            <div>
              <Label htmlFor='book-json'>Chapters JSON</Label>
              <Textarea
                id='book-json'
                placeholder='[{"chapter_title": "Chapter 1", "chapter_text": "..."}, ...]'
                value={bookJson}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setBookJson(e.target.value)
                }
                disabled={uploading || loading}
                className='min-h-[120px] font-mono text-sm'
              />
              <p className='text-xs text-muted-foreground mt-1'>
                JSON array: [{'{'}chapter_title, chapter_text{'}'}]
              </p>
            </div>
            <Button
              onClick={handleUploadBook}
              disabled={
                uploading ||
                loading ||
                !bookId.trim() ||
                !bookTitle.trim() ||
                !bookJson.trim()
              }
            >
              {uploading ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className='mr-2 h-4 w-4' />
                  Upload Book
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Book Info Display */}
        {bookInfo && (
          <div className='space-y-3 mb-6'>
            <div className='bg-card border rounded-lg p-4'>
              <div className='space-y-2'>
                <h2 className='text-xl font-semibold'>{bookInfo.title}</h2>
                <div className='flex gap-4 text-sm text-muted-foreground'>
                  {bookInfo.author && <span>by {bookInfo.author}</span>}
                  {bookInfo.publication_year && (
                    <span>{bookInfo.publication_year}</span>
                  )}
                </div>
                {bookInfo.description && (
                  <p className='text-sm text-muted-foreground'>
                    {bookInfo.description}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Editor Section */}
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

        {/* Chapters Section */}
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

        {/* Empty State */}
        {!bookInfo && !loading && (
          <div className='text-center py-12 text-muted-foreground'>
            <BookOpen className='h-16 w-16 mx-auto mb-4 opacity-20' />
            <p className='text-lg'>Upload a book above to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}
