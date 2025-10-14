'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Save } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/lib/auth-context';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { API_BASE_URL } from '@/lib/config';

interface ChunkIndex {
  chunk_id: number;
  short_title: string;
  chapter_id?: number;
  chapter_title?: string;
  ai_field_1?: string;
}

interface ChunkDetails {
  chunk_id: number;
  short_title: string;
  chunk_text: string;
  ai_field_1: string;
  ai_field_2: string;
  ai_field_3: string;
  note_content: string | null;
  chapter_id?: number;
  chapter_title?: string;
  chapter_text?: string;
}

interface ChunkViewerProps {
  videoId?: string;
  bookId?: string;
  isBook?: boolean;
}

export function ChunkViewer({
  videoId,
  bookId,
  isBook = false,
}: ChunkViewerProps) {
  const [chunkIndex, setChunkIndex] = useState<ChunkIndex[]>([]);
  const [selectedChunkId, setSelectedChunkId] = useState<number | null>(null);
  const [chunkDetails, setChunkDetails] = useState<ChunkDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingChunks, setLoadingChunks] = useState(true);
  const [noteContent, setNoteContent] = useState('');
  const [initialLoadedContent, setInitialLoadedContent] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSavingNote, setIsSavingNote] = useState(false);
  const { getAccessToken } = useAuth();

  const resourceId = isBook ? bookId : videoId;

  const loadChunkIndex = useCallback(async () => {
    if (!resourceId) return;

    setLoadingChunks(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        console.error('No access token available');
        setChunkIndex([]);
        setLoadingChunks(false);
        return;
      }

      const endpoint = isBook
        ? `${API_BASE_URL}/api/book/${resourceId}/chapters/index`
        : `${API_BASE_URL}/api/chunks/${resourceId}/index`;

      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404 || response.status === 500) {
          setChunkIndex([]);
          setLoadingChunks(false);
          return;
        }
        throw new Error('Failed to load chunk index');
      }

      const data = await response.json();
      const indexData = data.index || [];

      // Map book chapters to chunk format
      const mappedIndex = isBook
        ? indexData.map((chapter: any) => ({
            chunk_id: chapter.chapter_id,
            short_title: chapter.chapter_title,
            ai_field_1: chapter.ai_field_1,
          }))
        : indexData;

      setChunkIndex(mappedIndex);

      if (mappedIndex.length > 0) {
        setSelectedChunkId(mappedIndex[0].chunk_id);
      }
    } catch (error) {
      console.error('Error loading chunk index:', error);
      setChunkIndex([]);
    } finally {
      setLoadingChunks(false);
    }
  }, [resourceId, isBook, getAccessToken]);

  const loadChunkDetails = useCallback(
    async (chunkId: number) => {
      if (!resourceId) return;

      setLoading(true);
      try {
        const token = await getAccessToken();
        if (!token) {
          toast.error('Authentication required');
          setLoading(false);
          return;
        }

        const endpoint = isBook
          ? `${API_BASE_URL}/api/book/${resourceId}/chapter/${chunkId}`
          : `${API_BASE_URL}/api/chunks/${resourceId}/${chunkId}`;

        const response = await fetch(endpoint, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to load chunk details');
        }

        const data = await response.json();

        // Map book chapter to chunk format
        const mappedData = isBook
          ? {
              chunk_id: data.chapter_id,
              short_title: data.chapter_title,
              chunk_text: data.chapter_text,
              ai_field_1: data.ai_field_1 || '',
              ai_field_2: data.ai_field_2 || '',
              ai_field_3: data.ai_field_3 || '',
              note_content: data.note_content,
            }
          : data;

        setChunkDetails(mappedData);
        setNoteContent(mappedData.note_content || '');
        setInitialLoadedContent(mappedData.note_content || '');
        setHasUnsavedChanges(false);
      } catch (error) {
        console.error('Error loading chunk details:', error);
        toast.error('Failed to load chunk details');
      } finally {
        setLoading(false);
      }
    },
    [resourceId, isBook, getAccessToken]
  );

  useEffect(() => {
    if (resourceId) {
      loadChunkIndex();
    }
  }, [resourceId, loadChunkIndex]);

  useEffect(() => {
    if (selectedChunkId !== null) {
      loadChunkDetails(selectedChunkId);
    }
  }, [selectedChunkId, loadChunkDetails]);

  const saveChunkNote = async () => {
    if (!chunkDetails || !resourceId) return;

    setIsSavingNote(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        setIsSavingNote(false);
        return;
      }

      const endpoint = isBook
        ? `${API_BASE_URL}/api/book/${resourceId}/chapter/${chunkDetails.chunk_id}/note`
        : `${API_BASE_URL}/api/chunks/${resourceId}/${chunkDetails.chunk_id}/note`;

      const response = await fetch(endpoint, {
        method: isBook ? 'POST' : 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(
          isBook
            ? {
                book_id: resourceId,
                chapter_id: chunkDetails.chunk_id,
                note_content: noteContent,
              }
            : { note_content: noteContent }
        ),
      });

      if (!response.ok) {
        throw new Error('Failed to save chunk note');
      }

      toast.success('Chunk note saved!');
      setInitialLoadedContent(noteContent);
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error saving chunk note:', error);
      toast.error('Failed to save chunk note');
    } finally {
      setIsSavingNote(false);
    }
  };

  const handleEditorChange = useCallback(
    (markdown: string) => {
      setNoteContent(markdown);
      if (chunkDetails) {
        setHasUnsavedChanges(markdown !== initialLoadedContent);
      }
    },
    [chunkDetails, initialLoadedContent]
  );

  const handleInitialLoad = useCallback(() => {
    setHasUnsavedChanges(false);
  }, []);

  if (loadingChunks) {
    return (
      <div className='flex items-center justify-center p-8'>
        <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
      </div>
    );
  }

  if (chunkIndex.length === 0) {
    return (
      <Card>
        <CardContent className='p-6 text-center text-muted-foreground'>
          {isBook
            ? 'No chapters available for this book.'
            : 'No chunks available for this video. Process the video to generate chunks.'}
        </CardContent>
      </Card>
    );
  }

  return (
    <div className='space-y-4'>
      <div className='flex items-center gap-4'>
        <Select
          value={selectedChunkId?.toString()}
          onValueChange={(value) => setSelectedChunkId(parseInt(value))}
        >
          <SelectTrigger className='w-full'>
            <SelectValue placeholder='Select a chunk' />
          </SelectTrigger>
          <SelectContent>
            {chunkIndex.map((chunk) => (
              <SelectItem
                key={chunk.chunk_id}
                value={chunk.chunk_id.toString()}
              >
                {chunk.chunk_id}. {chunk.short_title || 'Untitled'}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className='flex items-center justify-center p-8'>
          <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
        </div>
      ) : chunkDetails ? (
        <div className='space-y-4'>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>Summary</CardTitle>
              </CardHeader>
              <CardContent className='max-h-64 overflow-y-auto text-sm'>
                {chunkDetails.ai_field_1 || 'Not available'}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>Key Points</CardTitle>
              </CardHeader>
              <CardContent className='max-h-64 overflow-y-auto text-sm'>
                {chunkDetails.ai_field_2 || 'Not available'}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>Topics</CardTitle>
              </CardHeader>
              <CardContent className='max-h-48 overflow-y-auto text-sm'>
                {chunkDetails.ai_field_3 || 'Not available'}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>
                  {isBook ? 'Chapter' : 'Chunk'} Text
                </CardTitle>
              </CardHeader>
              <CardContent className='max-h-48 overflow-y-auto text-sm'>
                {chunkDetails.chunk_text || 'Not available'}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className='p-3 pb-2'>
              <div className='flex items-center justify-between'>
                <CardTitle className='text-sm'>
                  {isBook ? 'Chapter' : 'Chunk'} Notes{' '}
                  {hasUnsavedChanges && (
                    <span className='text-amber-500'>*</span>
                  )}
                </CardTitle>
                <Button
                  size='sm'
                  onClick={saveChunkNote}
                  disabled={isSavingNote || !hasUnsavedChanges}
                  variant='default'
                >
                  {isSavingNote ? (
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
            </CardHeader>
            <CardContent className='p-3'>
              <TiptapMarkdownEditor
                value={noteContent}
                onChange={handleEditorChange}
                placeholder={`Add your notes for this ${
                  isBook ? 'chapter' : 'chunk'
                }...`}
                onInitialLoad={handleInitialLoad}
              />
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
