'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useSettings } from '@/lib/settings-context';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { ChunkTextToggle } from '@/components/chunk-text-toggle';

interface Chapter {
  chapter_id: number;
  chapter_title: string;
  chapter_text?: string;
  chapter_text_path?: string;
  created_at?: string;
  updated_at?: string;
}

interface BookChunkEditorProps {
  bookId: string | null;
}

export function BookChunkEditor({
  bookId: initialBookId,
}: BookChunkEditorProps) {
  const [bookId, setBookId] = useState(initialBookId || '');
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState<Record<number, boolean>>({});
  const [selectedChapterId, setSelectedChapterId] = useState<number | null>(
    null
  );
  const [editingChapter, setEditingChapter] = useState<Chapter | null>(null);
  const [saving, setSaving] = useState(false);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const { getAccessToken } = useAuth();
  const { showChunkText } = useSettings();
  const router = useRouter();

  useEffect(() => {
    if (initialBookId) {
      setBookId(initialBookId);
      loadChapters(initialBookId);
    }
  }, [initialBookId]);

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
        `http://localhost:8000/api/book/${book_id}/chapters`,
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
          `http://localhost:8000/api/book/${bookId}/chapter/${chapter.chapter_id}?include_text=true`,
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
    setEditingChapter({ ...chapter, chapter_text: chapter.chapter_text || '' });

    // Then fetch the text if needed
    const text = await loadChapterText(chapter);
    setEditingChapter({ ...chapter, chapter_text: text });
  };

  const handleSaveChapter = async () => {
    if (!editingChapter || !bookId) return;

    setSaving(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        `http://localhost:8000/api/book/${bookId}/chapter/${editingChapter.chapter_id}/text`,
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

      if (!response.ok) {
        throw new Error('Failed to save chapter');
      }

      toast.success('Chapter saved successfully');

      // Update chapters list
      setChapters((prev) =>
        prev.map((ch) =>
          ch.chapter_id === editingChapter.chapter_id
            ? { ...ch, chapter_text: editingChapter.chapter_text }
            : ch
        )
      );

      // Keep editing the same chapter (don't close editor)
    } catch (error) {
      console.error('Error saving chapter:', error);
      toast.error('Failed to save chapter');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteChapter = async (chapterId: number) => {
    if (!confirm('Are you sure you want to delete this chapter?')) return;

    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        `http://localhost:8000/api/book/${bookId}/chapter/${chapterId}`,
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
    } catch (error) {
      console.error('Error deleting chapter:', error);
      toast.error('Failed to delete chapter');
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
        `http://localhost:8000/api/book/${bookId}/chapters/reorder`,
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
        `http://localhost:8000/api/book/${bookId}/chapters/reorder`,
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
        loadChapters(bookId);
      }
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
                  <Button size='sm' onClick={handleAddChapter}>
                    <Plus className='h-4 w-4 mr-2' />
                    Add Chapter
                  </Button>
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
                            {chapter.chapter_id}. {chapter.chapter_title}
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
                              handleDeleteChapter(chapter.chapter_id);
                            }}
                          >
                            <Trash2 className='h-4 w-4 text-destructive' />
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
                      <Label htmlFor='chapter-title'>Chapter Title</Label>
                      <Input
                        id='chapter-title'
                        value={editingChapter.chapter_title}
                        onChange={(e) =>
                          setEditingChapter({
                            ...editingChapter,
                            chapter_title: e.target.value,
                          })
                        }
                      />
                    </div>

                    {showChunkText && (
                      <div>
                        <Label htmlFor='chapter-text'>Chapter Text</Label>
                        <Textarea
                          id='chapter-text'
                          className='min-h-[400px] text-sm'
                          value={
                            loadingText[editingChapter.chapter_id]
                              ? 'Loading chapter text...'
                              : editingChapter.chapter_text || ''
                          }
                          onChange={(e) =>
                            setEditingChapter({
                              ...editingChapter,
                              chapter_text: e.target.value,
                            })
                          }
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
                      <Button onClick={handleSaveChapter} disabled={saving}>
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
    </div>
  );
}
