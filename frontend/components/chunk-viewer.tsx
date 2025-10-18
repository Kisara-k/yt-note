'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { ActionButton } from '@/components/ui/action-button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Save, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/lib/auth-context';
import { useSettings } from '@/lib/settings-context';
import { CustomTooltip } from '@/components/custom-tooltip';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { NoteEditor } from '@/components/note-editor';
import { API_BASE_URL } from '@/lib/config';
import { AIFieldDisplay } from '@/components/ai-field-display';
import { useAIPolling } from '@/lib/use-ai-polling';

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
  refreshAIFields?: number; // Increment this to trigger AI field refresh
}

export function ChunkViewer({
  videoId,
  bookId,
  isBook = false,
  refreshAIFields = 0,
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
  const [processingChapter, setProcessingChapter] = useState(false);
  const [regeneratingField, setRegeneratingField] = useState<string | null>(
    null
  );
  const { getAccessToken } = useAuth();
  const { showChunkText } = useSettings();
  const { startPolling, stopPolling } = useAIPolling();

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

      // Only set selectedChunkId if not already set (initial load)
      if (mappedIndex.length > 0 && selectedChunkId === null) {
        setSelectedChunkId(mappedIndex[0].chunk_id);
      }
    } catch (error) {
      console.error('Error loading chunk index:', error);
      setChunkIndex([]);
    } finally {
      setLoadingChunks(false);
    }
  }, [resourceId, isBook, getAccessToken, selectedChunkId]); // Added selectedChunkId to dependencies

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
          ? `${API_BASE_URL}/api/book/${resourceId}/chapter/${chunkId}?include_text=${showChunkText}`
          : `${API_BASE_URL}/api/chunks/${resourceId}/${chunkId}?include_text=${showChunkText}`;

        const response = await fetch(endpoint, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          // Silently handle failed responses
          console.error(
            'Failed to load chunk details, status:',
            response.status
          );
          setLoading(false);
          return;
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
        // Silently handle the error - no user notification
      } finally {
        setLoading(false);
      }
    },
    [resourceId, isBook, getAccessToken, showChunkText]
  );

  useEffect(() => {
    if (resourceId) {
      loadChunkIndex();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resourceId]); // Only re-run when resourceId changes, not when loadChunkIndex changes

  useEffect(() => {
    if (selectedChunkId !== null) {
      loadChunkDetails(selectedChunkId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedChunkId]); // Only re-run when selectedChunkId changes, not when loadChunkDetails changes

  // Reload chunk details when showChunkText setting changes
  useEffect(() => {
    if (selectedChunkId !== null) {
      loadChunkDetails(selectedChunkId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showChunkText]); // Reload when the setting changes

  // Refresh AI fields when refreshAIFields prop changes (both books and videos)
  useEffect(() => {
    const refreshAIFieldsOnly = async () => {
      if (
        selectedChunkId !== null &&
        refreshAIFields > 0 &&
        chunkDetails !== null
      ) {
        const aiFields = await loadCompleteAIFields(selectedChunkId);
        if (aiFields) {
          setChunkDetails((prev) =>
            prev
              ? {
                  ...prev,
                  short_title: aiFields.short_title || prev.short_title,
                  ai_field_1: aiFields.ai_field_1,
                  ai_field_2: aiFields.ai_field_2,
                  ai_field_3: aiFields.ai_field_3,
                }
              : prev
          );
          // Reload chunk index to update titles in the dropdown
          // This is now safe because we fixed the useEffect dependencies to prevent cascade
          loadChunkIndex();
        }
      }
    };
    refreshAIFieldsOnly();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshAIFields]); // Only trigger when refreshAIFields changes, not selectedChunkId

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

  /**
   * Load complete AI fields (used for refresh effect)
   */
  const loadCompleteAIFields = async (chunkId: number) => {
    if (!resourceId) return null;

    try {
      const token = await getAccessToken();
      if (!token) return null;

      const endpoint = isBook
        ? `${API_BASE_URL}/api/book/${resourceId}/chapters`
        : `${API_BASE_URL}/api/chunks/${resourceId}`;

      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error(
          'Failed to load complete AI fields, status:',
          response.status
        );
        return null;
      }

      const data = await response.json();
      const item = isBook
        ? data.chapters?.find((ch: any) => ch.chapter_id === chunkId)
        : data.chunks?.find((ch: any) => ch.chunk_id === chunkId);

      if (!item) {
        console.error('Item not found in list');
        return null;
      }

      return {
        short_title: isBook ? item.chapter_title : item.short_title,
        ai_field_1: item.ai_field_1 || '',
        ai_field_2: item.ai_field_2 || '',
        ai_field_3: item.ai_field_3 || '',
      };
    } catch (error) {
      console.error('Error loading complete AI fields:', error);
      return null;
    }
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  const handleProcessChapterAI = async () => {
    if (!chunkDetails || !resourceId) return;

    setProcessingChapter(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        setProcessingChapter(false);
        return;
      }

      const endpoint = isBook
        ? `${API_BASE_URL}/api/jobs/process-book-chapter-ai`
        : `${API_BASE_URL}/api/jobs/process-video-chunk-ai`;

      const body = isBook
        ? {
            book_id: resourceId,
            chapter_id: chunkDetails.chunk_id,
            chapter_text: chunkDetails.chunk_text,
          }
        : {
            video_id: resourceId,
            chunk_id: chunkDetails.chunk_id,
            chunk_text: chunkDetails.chunk_text,
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
        throw new Error(error.detail || 'Failed to start AI enrichment');
      }

      const result = await response.json();
      toast.success(
        `${
          isBook ? 'Chapter' : 'Chunk'
        } AI enrichment started! This may take a minute.`
      );
      console.log(
        `${isBook ? 'Chapter' : 'Chunk'} AI enrichment started:`,
        result
      );

      // Store the current AI fields to compare against
      const currentAIState = {
        short_title: chunkDetails.short_title,
        ai_field_1: chunkDetails.ai_field_1,
      };

      // Start polling using the custom hook
      startPolling({
        resourceId,
        chunkId: chunkDetails.chunk_id,
        isBook,
        initialState: currentAIState,
        onComplete: (completeAIFields) => {
          console.log('AI enrichment complete, updating UI...');

          // Update chunk details with complete AI fields
          setChunkDetails((prev) =>
            prev
              ? {
                  ...prev,
                  short_title: completeAIFields.short_title || prev.short_title,
                  ai_field_1: completeAIFields.ai_field_1 || '',
                  ai_field_2: completeAIFields.ai_field_2 || '',
                  ai_field_3: completeAIFields.ai_field_3 || '',
                }
              : prev
          );

          // Reload chunk index to update titles in the dropdown
          loadChunkIndex();
          setProcessingChapter(false);
          toast.success(
            `${isBook ? 'Chapter' : 'Chunk'} AI enrichment complete!`
          );
        },
        onTimeout: () => {
          console.log('AI enrichment timeout');
          setProcessingChapter(false);
          toast.info(
            'AI enrichment is taking longer than expected. Manually refresh to see updates.'
          );
        },
        onError: (error) => {
          console.error('AI enrichment polling error:', error);
          setProcessingChapter(false);
          toast.error('Failed to check AI enrichment status');
        },
        maxPolls: 180, // 3 minutes
        pollInterval: 1000, // 1 second
      });
    } catch (error) {
      console.error('AI enrichment error:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to start AI enrichment'
      );
      setProcessingChapter(false);
    }
  };

  const handleRegenerateField = async (fieldName: string) => {
    if (!chunkDetails) return;

    setRegeneratingField(fieldName);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const endpoint = isBook
        ? `${API_BASE_URL}/api/book/${resourceId}/chapter/${chunkDetails.chunk_id}/regenerate-ai-field`
        : `${API_BASE_URL}/api/chunks/${resourceId}/${chunkDetails.chunk_id}/regenerate-ai-field`;

      const body = isBook
        ? {
            book_id: resourceId,
            chapter_id: chunkDetails.chunk_id,
            field_name: fieldName,
            chapter_text: chunkDetails.chunk_text, // Pass chapter text to avoid backend loading
          }
        : {
            video_id: resourceId,
            chunk_id: chunkDetails.chunk_id,
            field_name: fieldName,
            chunk_text: chunkDetails.chunk_text, // Pass chunk text to avoid backend loading
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
        throw new Error(error.detail || 'Failed to regenerate field');
      }

      const result = await response.json();

      // Update the local state with the new value
      setChunkDetails((prev) => {
        if (!prev) return prev;

        const fieldMap: Record<string, keyof ChunkDetails> = {
          title: 'short_title',
          field_1: 'ai_field_1',
          field_2: 'ai_field_2',
          field_3: 'ai_field_3',
        };

        const dbField = fieldMap[fieldName];
        if (dbField) {
          return {
            ...prev,
            [dbField]: result.value,
          };
        }
        return prev;
      });

      toast.success('Field regenerated successfully!');
    } catch (error) {
      console.error('Regenerate field error:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to regenerate field'
      );
    } finally {
      setRegeneratingField(null);
    }
  };

  const handleUpdateField = async (fieldName: string, newContent: string) => {
    if (!chunkDetails || !resourceId) return;

    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const endpoint = isBook
        ? `${API_BASE_URL}/api/book/${resourceId}/chapter/${chunkDetails.chunk_id}/update-ai-field`
        : `${API_BASE_URL}/api/chunks/${resourceId}/${chunkDetails.chunk_id}/update-ai-field`;

      const response = await fetch(endpoint, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          field_name: fieldName,
          field_value: newContent,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update field');
      }

      const result = await response.json();

      // Update local state with the new value
      setChunkDetails((prev) => {
        if (!prev) return prev;
        const fieldKey =
          fieldName === 'field_1'
            ? 'ai_field_1'
            : fieldName === 'field_2'
            ? 'ai_field_2'
            : 'ai_field_3';
        return {
          ...prev,
          [fieldKey]: newContent,
        };
      });

      toast.success('Field updated successfully');
    } catch (error) {
      console.error('Update field error:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to update field'
      );
      throw error; // Re-throw so the component knows it failed
    }
  };

  const handleUpdateChunkText = async (newContent: string) => {
    if (!chunkDetails || !resourceId) return;

    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const endpoint = isBook
        ? `${API_BASE_URL}/api/book/${resourceId}/chapter/${chunkDetails.chunk_id}/text`
        : `${API_BASE_URL}/api/chunks/${resourceId}/${chunkDetails.chunk_id}/text`;

      const response = await fetch(endpoint, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(
          isBook ? { chapter_text: newContent } : { chunk_text: newContent }
        ),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update chunk text');
      }

      // Update local state with the new value
      setChunkDetails((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          chunk_text: newContent,
        };
      });

      toast.success('Chunk text updated successfully');
    } catch (error) {
      console.error('Update chunk text error:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to update chunk text'
      );
      throw error; // Re-throw so the component knows it failed
    }
  };

  const handleInitialLoad = useCallback(() => {
    setHasUnsavedChanges(false);
  }, []);

  return (
    <div className='space-y-4'>
      <div className='flex items-center gap-2'>
        <Select
          value={selectedChunkId?.toString()}
          onValueChange={(value) => setSelectedChunkId(parseInt(value))}
          disabled={loadingChunks || chunkIndex.length === 0}
        >
          <SelectTrigger className='w-full' hideIcon={chunkIndex.length <= 1}>
            <SelectValue
              placeholder={
                loadingChunks
                  ? 'Loading...'
                  : chunkIndex.length === 0
                  ? 'No chunks available'
                  : 'Select a chunk'
              }
            />
          </SelectTrigger>
          <SelectContent>
            {chunkIndex.map((chunk) => (
              <SelectItem
                key={chunk.chunk_id}
                value={chunk.chunk_id.toString()}
              >
                {isBook
                  ? chunk.short_title || 'Untitled'
                  : `${chunk.chunk_id}. ${chunk.short_title || 'Untitled'}`}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <CustomTooltip
          content={`Process AI enrichment for this ${
            isBook ? 'chapter' : 'chunk'
          }`}
        >
          <ActionButton
            onClick={handleProcessChapterAI}
            disabled={processingChapter || !chunkDetails || loadingChunks}
            loading={processingChapter}
            icon={Sparkles}
          >
            AI Process
          </ActionButton>
        </CustomTooltip>
      </div>

      <div className='space-y-4'>
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <AIFieldDisplay
            title='Summary'
            content={chunkDetails?.ai_field_1}
            // height='h-48'
            onRegenerate={() => handleRegenerateField('field_1')}
            onUpdate={(newContent) => handleUpdateField('field_1', newContent)}
            isRegenerating={regeneratingField === 'field_1'}
            isLoading={loading || loadingChunks}
          />

          <AIFieldDisplay
            title='Key Points'
            content={chunkDetails?.ai_field_2}
            // height='h-48'
            onRegenerate={() => handleRegenerateField('field_2')}
            onUpdate={(newContent) => handleUpdateField('field_2', newContent)}
            isRegenerating={regeneratingField === 'field_2'}
            isLoading={loading || loadingChunks}
          />

          <AIFieldDisplay
            title='Topics'
            content={chunkDetails?.ai_field_3}
            // height='h-48'
            onRegenerate={() => handleRegenerateField('field_3')}
            onUpdate={(newContent) => handleUpdateField('field_3', newContent)}
            isRegenerating={regeneratingField === 'field_3'}
            isLoading={loading || loadingChunks}
          />

          {showChunkText && (
            <AIFieldDisplay
              title={isBook ? 'Chapter Text' : 'Chunk Text'}
              content={chunkDetails?.chunk_text}
              // height='h-48'
              onUpdate={handleUpdateChunkText}
              isLoading={loading || loadingChunks}
              useMarkdown={false}
            />
          )}
        </div>

        {loading || loadingChunks ? (
          <Card>
            <CardContent className='p-12'>
              <div className='flex items-center justify-center'>
                <Loader2 className='h-6 w-6 animate-spin text-muted-foreground' />
              </div>
            </CardContent>
          </Card>
        ) : (
          <NoteEditor
            title={`${isBook ? 'Chapter' : 'Chunk'} Notes`}
            value={noteContent}
            onChange={handleEditorChange}
            onSave={saveChunkNote}
            onInitialLoad={handleInitialLoad}
            isSaving={isSavingNote}
            hasUnsavedChanges={hasUnsavedChanges}
            placeholder={`Add your notes for this ${
              isBook ? 'chapter' : 'chunk'
            }...`}
            disabled={loading || loadingChunks}
          />
        )}
      </div>
    </div>
  );
}
