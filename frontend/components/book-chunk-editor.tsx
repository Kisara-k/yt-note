'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Loader2,
  BookOpen,
  Plus,
  Trash2,
  Save,
  ArrowUp,
  ArrowDown,
  Edit,
  X,
  GripVertical,
  Upload,
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useAuth } from '@/lib/auth-context';
import { API_BASE_URL } from '@/lib/config';
import { useSettings } from '@/lib/settings-context';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { ChunkTextToggle } from '@/components/chunk-text-toggle';
import { parseAndNormalizeChapters } from '@/lib/book-json-parser';
import { validateAndNormalizeBookId } from '@/lib/book-id-validation';

interface Chapter {
  chapter_id: number;
  chapter_title: string;
  chapter_text?: string;
  chapter_text_path?: string;
  created_at?: string;
  updated_at?: string;
}

interface BookMetadata {
  id: string;
  title: string;
  author: string | null;
  publisher: string | null;
  publication_year: number | null;
  isbn: string | null;
  description: string | null;
  tags: string[];
  type: string;
}

interface BookChunkEditorProps {
  bookId: string | null;
}

export function BookChunkEditor({
  bookId: initialBookId,
}: BookChunkEditorProps) {
  const [bookId, setBookId] = useState(initialBookId || '');
  const [bookMetadata, setBookMetadata] = useState<BookMetadata | null>(null);
  const [savingBookMetadata, setSavingBookMetadata] = useState(false);
  const [bookIdError, setBookIdError] = useState('');
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState<Record<number, boolean>>({});
  const [selectedChapterId, setSelectedChapterId] = useState<number | null>(
    null
  );
  const [editingChapter, setEditingChapter] = useState<Chapter | null>(null);
  const [originalChapter, setOriginalChapter] = useState<Chapter | null>(null);
  const [titleChanged, setTitleChanged] = useState(false);
  const [textChanged, setTextChanged] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [chapterToDelete, setChapterToDelete] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [chaptersJson, setChaptersJson] = useState('');
  const [importing, setImporting] = useState(false);
  const { getAccessToken } = useAuth();
  const { showChunkText } = useSettings();
  const router = useRouter();

  useEffect(() => {
    if (initialBookId) {
      setBookId(initialBookId);
      loadBook(initialBookId);
    }
  }, [initialBookId]);

  // Ctrl+S to save
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (editingChapter && (titleChanged || textChanged)) {
          handleSaveChapter();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [editingChapter, titleChanged, textChanged]);

  const loadBook = async (book_id: string) => {
    await Promise.all([loadBookMetadata(book_id), loadChapters(book_id)]);
  };

  const loadBookMetadata = async (book_id: string) => {
    if (!book_id.trim()) return;

    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/book/${book_id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load book metadata');
      }

      const data = await response.json();
      setBookMetadata(data);
    } catch (error) {
      console.error('Error loading book metadata:', error);
      toast.error('Failed to load book metadata');
    }
  };

  const loadChapters = async (book_id: string) => {
    if (!book_id.trim()) return;

    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        `${API_BASE_URL}/api/book/${book_id}/chapters`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load chapters');
      }

      const data = await response.json();
      setChapters(data.chapters || []);
    } catch (error) {
      console.error('Error loading chapters:', error);
      toast.error('Failed to load chapters');
    } finally {
      setLoading(false);
    }
  };

  const loadChapterText = async (chapter: Chapter) => {
    // If showChunkText is false, don't load the text
    if (!showChunkText) {
      return '';
    }

    if (!chapter.chapter_text && chapter.chapter_text_path) {
      setLoadingText((prev) => ({ ...prev, [chapter.chapter_id]: true }));
      try {
        const token = await getAccessToken();
        if (!token) return '';

        const response = await fetch(
          `${API_BASE_URL}/api/book/${bookId}/chapter/${chapter.chapter_id}?include_text=true`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to load chapter text');
        }

        const data = await response.json();
        return data.chapter_text || '';
      } catch (error) {
        console.error('Error loading chapter text:', error);
        toast.error('Failed to load chapter text');
        return '';
      } finally {
        setLoadingText((prev) => ({ ...prev, [chapter.chapter_id]: false }));
      }
    }
    return chapter.chapter_text || '';
  };

  const handleEditChapter = async (chapter: Chapter) => {
    // Immediately show the chapter in the editor (responsive UI)
    setSelectedChapterId(chapter.chapter_id);
    const initialChapter = {
      ...chapter,
      chapter_text: chapter.chapter_text || '',
    };
    setEditingChapter(initialChapter);
    setOriginalChapter(initialChapter);
    setTitleChanged(false);
    setTextChanged(false);

    // Then fetch the text if needed
    const text = await loadChapterText(chapter);
    const fullChapter = { ...chapter, chapter_text: text };
    setEditingChapter(fullChapter);
    setOriginalChapter(fullChapter);
  };

  const handleSaveChapter = async () => {
    if (!editingChapter || !bookId) return;
    if (!titleChanged && !textChanged) return; // No changes to save

    setSaving(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      // Check if this is a new chapter (not yet in the chapters list)
      const isNewChapter = !chapters.some(
        (ch) => ch.chapter_id === editingChapter.chapter_id
      );

      let response;

      if (isNewChapter) {
        // Create new chapter using POST
        response = await fetch(
          `${API_BASE_URL}/api/book/${bookId}/chapter/${editingChapter.chapter_id}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              chapter_title: editingChapter.chapter_title,
              chapter_text: editingChapter.chapter_text || '',
            }),
          }
        );
      } else {
        // Update existing chapter - update title and/or text
        if (titleChanged && textChanged) {
          // Both changed - update title first, then text
          const titleResponse = await fetch(
            `${API_BASE_URL}/api/book/${bookId}/chapter/${editingChapter.chapter_id}/title`,
            {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                chapter_title: editingChapter.chapter_title,
              }),
            }
          );
          if (!titleResponse.ok) {
            throw new Error('Failed to update chapter title');
          }

          response = await fetch(
            `${API_BASE_URL}/api/book/${bookId}/chapter/${editingChapter.chapter_id}/text`,
            {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                chapter_text: editingChapter.chapter_text,
              }),
            }
          );
        } else if (titleChanged) {
          // Only title changed
          response = await fetch(
            `${API_BASE_URL}/api/book/${bookId}/chapter/${editingChapter.chapter_id}/title`,
            {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                chapter_title: editingChapter.chapter_title,
              }),
            }
          );
        } else if (textChanged) {
          // Only text changed
          response = await fetch(
            `${API_BASE_URL}/api/book/${bookId}/chapter/${editingChapter.chapter_id}/text`,
            {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                chapter_text: editingChapter.chapter_text,
              }),
            }
          );
        }
      }

      if (!response || !response.ok) {
        throw new Error('Failed to save chapter');
      }

      const savedChapter = await response.json();

      toast.success(
        isNewChapter
          ? 'Chapter created successfully'
          : 'Chapter saved successfully'
      );

      if (isNewChapter) {
        // Add new chapter to the list
        setChapters((prev) => [...prev, savedChapter]);
      } else {
        // Update existing chapter in the list
        setChapters((prev) =>
          prev.map((ch) =>
            ch.chapter_id === editingChapter.chapter_id
              ? {
                  ...ch,
                  chapter_title: editingChapter.chapter_title,
                  chapter_text: editingChapter.chapter_text,
                }
              : ch
          )
        );
      }

      // Reset change tracking flags
      setTitleChanged(false);
      setTextChanged(false);
      // Update original chapter to current state
      setOriginalChapter(editingChapter);

      // Keep editing the same chapter (don't close editor)
    } catch (error) {
      console.error('Error saving chapter:', error);
      toast.error('Failed to save chapter');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteChapter = async (chapterId: number) => {
    setDeleting(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        `${API_BASE_URL}/api/book/${bookId}/chapter/${chapterId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete chapter');
      }

      toast.success('Chapter deleted successfully');
      setChapters((prev) => prev.filter((ch) => ch.chapter_id !== chapterId));

      if (editingChapter?.chapter_id === chapterId) {
        setEditingChapter(null);
        setSelectedChapterId(null);
      }

      // Close dialog
      setDeleteDialogOpen(false);
      setChapterToDelete(null);
    } catch (error) {
      console.error('Error deleting chapter:', error);
      toast.error('Failed to delete chapter');
    } finally {
      setDeleting(false);
    }
  };

  const openDeleteDialog = (chapterId: number) => {
    setChapterToDelete(chapterId);
    setDeleteDialogOpen(true);
  };

  const closeDeleteDialog = () => {
    if (!deleting) {
      setDeleteDialogOpen(false);
      setChapterToDelete(null);
    }
  };

  const handleMoveChapter = async (index: number, direction: 'up' | 'down') => {
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= chapters.length) return;

    const newChapters = [...chapters];
    [newChapters[index], newChapters[newIndex]] = [
      newChapters[newIndex],
      newChapters[index],
    ];

    // Optimistic update
    setChapters(newChapters);

    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        // Revert on error
        setChapters(chapters);
        return;
      }

      const chapterOrder = newChapters.map((ch) => ch.chapter_id);

      const response = await fetch(
        `${API_BASE_URL}/api/book/${bookId}/chapters/reorder`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ chapter_order: chapterOrder }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to reorder chapters');
      }

      toast.success('Chapters reordered successfully');
      // No need to reload - optimistic update already handled UI
    } catch (error) {
      console.error('Error reordering chapters:', error);
      toast.error('Failed to reorder chapters');
      // Revert on error
      setChapters(chapters);
    }
  };

  const handleAddChapter = () => {
    const newChapterId =
      chapters.length > 0
        ? Math.max(...chapters.map((ch) => ch.chapter_id)) + 1
        : 1;

    setEditingChapter({
      chapter_id: newChapterId,
      chapter_title: `Chapter ${newChapterId}`,
      chapter_text: '',
    });
    setSelectedChapterId(newChapterId);
  };

  const openImportDialog = () => {
    setImportDialogOpen(true);
    setChaptersJson('');
  };

  const closeImportDialog = () => {
    setImportDialogOpen(false);
    setChaptersJson('');
  };

  const handleImportChapters = async () => {
    if (!chaptersJson.trim()) {
      toast.error('Please enter chapters JSON');
      return;
    }

    setImporting(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      // Use the shared parser and normalizer
      const normalizedChapters = parseAndNormalizeChapters(chaptersJson);

      // Determine the next chapter ID
      const nextChapterId =
        chapters.length > 0
          ? Math.max(...chapters.map((ch) => ch.chapter_id)) + 1
          : 1;

      // Import chapters sequentially
      let successCount = 0;
      const newChapters: Chapter[] = [];

      for (let i = 0; i < normalizedChapters.length; i++) {
        const chapter = normalizedChapters[i];
        const chapterId = nextChapterId + i;

        const response = await fetch(
          `${API_BASE_URL}/api/book/${bookId}/chapter/${chapterId}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              chapter_title: chapter.title,
              chapter_text: chapter.content,
            }),
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to import chapter ${i + 1}: ${chapter.title}`
          );
        }

        const data = await response.json();
        newChapters.push(data);
        successCount++;
      }

      // Reload chapters to reflect the new state
      await loadChapters(bookId);

      toast.success(
        `Successfully imported ${successCount} chapter${
          successCount > 1 ? 's' : ''
        }`
      );
      closeImportDialog();
    } catch (error) {
      console.error('Error importing chapters:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to import chapters'
      );
    } finally {
      setImporting(false);
    }
  };

  // Drag-and-drop handlers
  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();

    if (draggedIndex === null || draggedIndex === index) return;

    // Reorder array in real-time for smooth animation
    const newChapters = [...chapters];
    const [draggedChapter] = newChapters.splice(draggedIndex, 1);
    newChapters.splice(index, 0, draggedChapter);

    setChapters(newChapters);
    setDraggedIndex(index); // Update to new position
    setDragOverIndex(index);
  };

  const handleDrop = async (index: number) => {
    if (draggedIndex === null) {
      setDraggedIndex(null);
      setDragOverIndex(null);
      return;
    }

    // Array is already reordered from dragover events
    // Clean up drag state
    setDraggedIndex(null);
    setDragOverIndex(null);

    // Persist to database
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const chapterOrder = chapters.map((ch) => ch.chapter_id);

      const response = await fetch(
        `${API_BASE_URL}/api/book/${bookId}/chapters/reorder`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ chapter_order: chapterOrder }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to reorder chapters');
      }

      toast.success('Chapters reordered successfully');
    } catch (error) {
      console.error('Error reordering chapters:', error);
      toast.error('Failed to reorder chapters');
    }
  };

  const handleDragEnd = () => {
    // Clean up drag state
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const handleChapterClick = (chapter: Chapter) => {
    handleEditChapter(chapter);
  };

  const handleLoadBook = () => {
    if (bookId.trim()) {
      // Only reload if we're changing to a different book
      if (bookId !== initialBookId) {
        router.push(`/book/chunks?b=${bookId}`);
        loadBook(bookId);
      }
    }
  };

  const handleSaveBookMetadata = async () => {
    if (!bookMetadata) return;

    setSavingBookMetadata(true);
    setBookIdError('');
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      // Validate new book ID if it changed
      let newBookId = bookMetadata.id;
      if (newBookId !== bookId) {
        const { isValid, normalized, error } =
          validateAndNormalizeBookId(newBookId);
        if (!isValid) {
          setBookIdError(error || 'Invalid book ID');
          toast.error(error || 'Invalid book ID');
          return;
        }
        newBookId = normalized;
      }

      const response = await fetch(`${API_BASE_URL}/api/book/${bookId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          new_book_id: newBookId !== bookId ? newBookId : undefined,
          title: bookMetadata.title,
          author: bookMetadata.author,
          publisher: bookMetadata.publisher,
          publication_year: bookMetadata.publication_year,
          isbn: bookMetadata.isbn,
          description: bookMetadata.description,
          tags: bookMetadata.tags,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        const errorMessage =
          typeof error.detail === 'string'
            ? error.detail
            : error.error || error.message || 'Failed to update book';

        // Handle duplicate book ID error specifically
        if (
          response.status === 409 ||
          errorMessage.includes('already exists')
        ) {
          setBookIdError(errorMessage);
        }

        throw new Error(errorMessage);
      }

      const updatedBook = await response.json();
      setBookMetadata(updatedBook);
      toast.success('Book metadata updated successfully');

      // If book ID changed, update URL and state without reloading
      if (newBookId !== bookId) {
        setBookId(newBookId);
        // Update URL without navigation/reload
        window.history.replaceState(null, '', `/book/chunks?b=${newBookId}`);
      }
    } catch (error) {
      console.error('Error updating book metadata:', error);
      toast.error(
        error instanceof Error
          ? error.message
          : 'Failed to update book metadata'
      );
    } finally {
      setSavingBookMetadata(false);
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto p-6 max-w-7xl'>
        <div className='mb-8'>
          <div className='flex justify-between items-center mb-4'>
            <div className='flex items-center gap-4'>
              <h1 className='text-3xl font-bold'>Book Chunk Editor</h1>
              <ChunkTextToggle />
            </div>
            <div className='flex items-center gap-2'>
              <Button
                variant='outline'
                size='sm'
                onClick={() => router.push('/book')}
              >
                <BookOpen className='mr-2 h-4 w-4' />
                Back to Books
              </Button>
            </div>
          </div>
        </div>

        {/* Book ID Input */}
        {!initialBookId && (
          <Card className='mb-6'>
            <CardContent className='pt-6'>
              <div className='flex gap-2'>
                <div className='flex-1'>
                  <Label htmlFor='book-id' className='sr-only'>
                    Book ID
                  </Label>
                  <Input
                    id='book-id'
                    placeholder='Enter book ID'
                    value={bookId}
                    onChange={(e) => setBookId(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleLoadBook()}
                  />
                </div>
                <Button onClick={handleLoadBook} disabled={!bookId.trim()}>
                  Load Book
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Book Metadata Editor */}
        {bookMetadata && !loading && (
          <Card className='mb-6'>
            <CardHeader>
              <div className='flex items-center justify-between'>
                <CardTitle>Book Metadata</CardTitle>
                <Button
                  size='sm'
                  onClick={handleSaveBookMetadata}
                  disabled={savingBookMetadata}
                >
                  {savingBookMetadata ? (
                    <>
                      <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className='mr-2 h-4 w-4' />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                {/* First Row: Book ID, Title, Author, Type */}
                <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
                  <div>
                    <Label htmlFor='edit-book-id'>
                      Book ID *{' '}
                      <span className='text-xs text-muted-foreground'>
                        (lowercase, underscores)
                      </span>
                    </Label>
                    <Input
                      id='edit-book-id'
                      value={bookMetadata.id}
                      onChange={(e) =>
                        setBookMetadata({
                          ...bookMetadata,
                          id: e.target.value,
                        })
                      }
                      disabled={savingBookMetadata}
                      className={bookIdError ? 'border-red-500' : ''}
                    />
                    {bookIdError && (
                      <p className='text-sm text-red-500 mt-1'>{bookIdError}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor='edit-title'>Title *</Label>
                    <Input
                      id='edit-title'
                      value={bookMetadata.title}
                      onChange={(e) =>
                        setBookMetadata({
                          ...bookMetadata,
                          title: e.target.value,
                        })
                      }
                      disabled={savingBookMetadata}
                    />
                  </div>
                  <div>
                    <Label htmlFor='edit-author'>Author</Label>
                    <Input
                      id='edit-author'
                      value={bookMetadata.author || ''}
                      onChange={(e) =>
                        setBookMetadata({
                          ...bookMetadata,
                          author: e.target.value || null,
                        })
                      }
                      disabled={savingBookMetadata}
                    />
                  </div>
                  <div>
                    <Label htmlFor='edit-type'>Type</Label>
                    <Select
                      value={bookMetadata.type}
                      onValueChange={(value) =>
                        setBookMetadata({
                          ...bookMetadata,
                          type: value,
                        })
                      }
                      disabled={savingBookMetadata}
                    >
                      <SelectTrigger id='edit-type'>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value='book'>Book</SelectItem>
                        <SelectItem value='lecture'>Lecture</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Second Row: Publisher, Year, ISBN, Tags */}
                <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
                  <div>
                    <Label htmlFor='edit-publisher'>Publisher</Label>
                    <Input
                      id='edit-publisher'
                      value={bookMetadata.publisher || ''}
                      onChange={(e) =>
                        setBookMetadata({
                          ...bookMetadata,
                          publisher: e.target.value || null,
                        })
                      }
                      disabled={savingBookMetadata}
                    />
                  </div>
                  <div>
                    <Label htmlFor='edit-year'>Publication Year</Label>
                    <Input
                      id='edit-year'
                      type='number'
                      value={bookMetadata.publication_year || ''}
                      onChange={(e) =>
                        setBookMetadata({
                          ...bookMetadata,
                          publication_year: e.target.value
                            ? parseInt(e.target.value)
                            : null,
                        })
                      }
                      disabled={savingBookMetadata}
                    />
                  </div>
                  <div>
                    <Label htmlFor='edit-isbn'>ISBN</Label>
                    <Input
                      id='edit-isbn'
                      value={bookMetadata.isbn || ''}
                      onChange={(e) =>
                        setBookMetadata({
                          ...bookMetadata,
                          isbn: e.target.value || null,
                        })
                      }
                      disabled={savingBookMetadata}
                    />
                  </div>
                  <div>
                    <Label htmlFor='edit-tags'>
                      Tags{' '}
                      <span className='text-xs text-muted-foreground'>
                        (comma-separated)
                      </span>
                    </Label>
                    <Input
                      id='edit-tags'
                      value={bookMetadata.tags?.join(', ') || ''}
                      onChange={(e) =>
                        setBookMetadata({
                          ...bookMetadata,
                          tags: e.target.value
                            ? e.target.value.split(',').map((tag) => tag.trim())
                            : [],
                        })
                      }
                      disabled={savingBookMetadata}
                      placeholder='tag1, tag2, tag3'
                    />
                  </div>
                </div>

                {/* Third Row: Description (full width) */}
                <div>
                  <Label htmlFor='edit-description'>Description</Label>
                  <Textarea
                    id='edit-description'
                    value={bookMetadata.description || ''}
                    onChange={(e) =>
                      setBookMetadata({
                        ...bookMetadata,
                        description: e.target.value || null,
                      })
                    }
                    disabled={savingBookMetadata}
                    rows={3}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {loading ? (
          <div className='flex items-center justify-center p-12'>
            <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
          </div>
        ) : chapters.length > 0 ? (
          <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
            {/* Chapters List */}
            <Card>
              <CardHeader>
                <div className='flex items-center justify-between'>
                  <CardTitle>Chapters ({chapters.length})</CardTitle>
                  <div className='flex gap-2'>
                    <Button size='sm' onClick={handleAddChapter}>
                      <Plus className='h-4 w-4 mr-2' />
                      Add Chapter
                    </Button>
                    <Button
                      size='sm'
                      variant='outline'
                      onClick={openImportDialog}
                    >
                      <Upload className='h-4 w-4 mr-2' />
                      Import JSON
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div
                  className='space-y-2'
                  onDragOver={(e) => e.preventDefault()}
                >
                  {chapters.map((chapter, index) => {
                    const isDragging = draggedIndex === index;

                    return (
                      <div
                        key={chapter.chapter_id}
                        draggable
                        onDragStart={() => handleDragStart(index)}
                        onDragOver={(e) => handleDragOver(e, index)}
                        onDrop={() => handleDrop(index)}
                        onDragEnd={handleDragEnd}
                        onClick={() => handleChapterClick(chapter)}
                        className={`flex items-center gap-2 p-3 border rounded-lg cursor-pointer transition-all duration-200 ease-out ${
                          selectedChapterId === chapter.chapter_id
                            ? 'bg-secondary border-primary'
                            : 'hover:bg-secondary/50'
                        } ${isDragging ? 'opacity-40' : ''}`}
                      >
                        <GripVertical className='h-4 w-4 text-muted-foreground cursor-move' />
                        <div className='flex-1'>
                          <div className='font-medium'>
                            {chapter.chapter_title}
                          </div>
                        </div>

                        <div className='flex items-center gap-1'>
                          <Button
                            variant='ghost'
                            size='sm'
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMoveChapter(index, 'up');
                            }}
                            disabled={index === 0}
                          >
                            <ArrowUp className='h-4 w-4' />
                          </Button>
                          <Button
                            variant='ghost'
                            size='sm'
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMoveChapter(index, 'down');
                            }}
                            disabled={index === chapters.length - 1}
                          >
                            <ArrowDown className='h-4 w-4' />
                          </Button>
                          <Button
                            variant='ghost'
                            size='sm'
                            onClick={(e) => {
                              e.stopPropagation();
                              openDeleteDialog(chapter.chapter_id);
                            }}
                          >
                            <Trash2 className='h-4 w-4' />
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Chapter Editor */}
            <Card>
              <CardHeader>
                <div className='flex items-center justify-between'>
                  <CardTitle>
                    {editingChapter
                      ? `Edit: ${editingChapter.chapter_title}`
                      : 'Select a chapter to edit'}
                  </CardTitle>
                  {editingChapter && (
                    <Button
                      variant='ghost'
                      size='sm'
                      onClick={() => {
                        setEditingChapter(null);
                        setSelectedChapterId(null);
                      }}
                    >
                      <X className='h-4 w-4' />
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {editingChapter ? (
                  <div className='space-y-4'>
                    <div>
                      <Label htmlFor='chapter-title'>
                        Chapter Title{titleChanged && ' *'}
                      </Label>
                      <Input
                        id='chapter-title'
                        value={editingChapter.chapter_title}
                        onChange={(e) => {
                          const newTitle = e.target.value;
                          setEditingChapter({
                            ...editingChapter,
                            chapter_title: newTitle,
                          });
                          // Check if title has changed from original
                          setTitleChanged(
                            originalChapter?.chapter_title !== newTitle
                          );
                        }}
                      />
                    </div>

                    {showChunkText && (
                      <div>
                        <Label htmlFor='chapter-text'>
                          Chapter Text{textChanged && ' *'}
                        </Label>
                        <Textarea
                          id='chapter-text'
                          className='min-h-[400px] text-sm'
                          value={
                            loadingText[editingChapter.chapter_id]
                              ? 'Loading chapter text...'
                              : editingChapter.chapter_text || ''
                          }
                          onChange={(e) => {
                            const newText = e.target.value;
                            setEditingChapter({
                              ...editingChapter,
                              chapter_text: newText,
                            });
                            // Check if text has changed from original
                            setTextChanged(
                              originalChapter?.chapter_text !== newText
                            );
                          }}
                          placeholder='Enter chapter text...'
                          disabled={loadingText[editingChapter.chapter_id]}
                        />
                      </div>
                    )}

                    <div className='flex justify-end gap-2'>
                      <Button
                        variant='outline'
                        onClick={() => {
                          setEditingChapter(null);
                          setSelectedChapterId(null);
                        }}
                        disabled={saving}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleSaveChapter}
                        disabled={saving || (!titleChanged && !textChanged)}
                      >
                        {saving ? (
                          <>
                            <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Save className='mr-2 h-4 w-4' />
                            Save Chapter
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className='flex items-center justify-center h-[500px] text-muted-foreground'>
                    <p>Select a chapter from the list to edit its content</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ) : bookId ? (
          <Card>
            <CardContent className='p-12 text-center text-muted-foreground'>
              <BookOpen className='h-12 w-12 mx-auto mb-4 opacity-20' />
              <p>No chapters found for this book</p>
              <Button className='mt-4' onClick={handleAddChapter}>
                <Plus className='h-4 w-4 mr-2' />
                Add First Chapter
              </Button>
            </CardContent>
          </Card>
        ) : null}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={closeDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Chapter</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this chapter? This action cannot
              be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant='outline'
              onClick={closeDeleteDialog}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant='outline'
              onClick={() =>
                chapterToDelete && handleDeleteChapter(chapterToDelete)
              }
              disabled={deleting}
            >
              {deleting ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Chapters Dialog */}
      <Dialog open={importDialogOpen} onOpenChange={closeImportDialog}>
        <DialogContent className='max-w-3xl'>
          <DialogHeader>
            <DialogTitle>Import Chapters from JSON</DialogTitle>
            <DialogDescription>
              Add chapters from a JSON file. The chapters will be appended to
              the existing chapters.
            </DialogDescription>
          </DialogHeader>
          <div className='space-y-4 py-4'>
            <div className='space-y-2'>
              <Label htmlFor='import-chapters'>Chapters JSON</Label>
              <Textarea
                id='import-chapters'
                placeholder={
                  '[\n  {\n    "title": "Chapter Title",\n    "content": "Chapter content here..."\n  },\n  {\n    "title": "Another Chapter",\n    "content": "More content..."\n  }\n]'
                }
                value={chaptersJson}
                onChange={(e) => setChaptersJson(e.target.value)}
                disabled={importing}
                rows={15}
                className='font-mono text-sm'
              />
              <p className='text-sm text-muted-foreground'>
                JSON array with &quot;title&quot; and &quot;content&quot; for
                each chapter. Accepts multiple formats: array [{'{'}...{'}'}],
                comma-separated {'{'}...{'}'}, {'{'}...{'}'}, or line-separated{' '}
                {'{'}...{'}'}
                {'\n'}
                {'{'}...{'}'}.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant='outline'
              onClick={closeImportDialog}
              disabled={importing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleImportChapters}
              disabled={importing || !chaptersJson.trim()}
            >
              {importing ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Importing...
                </>
              ) : (
                <>
                  <Upload className='mr-2 h-4 w-4' />
                  Import Chapters
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
