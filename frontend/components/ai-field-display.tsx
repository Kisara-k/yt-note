'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { RefreshCw, SquarePen, Save, X } from 'lucide-react';

const BUTTON_OPACITY_CLASS =
  'opacity-30 hover:opacity-100 hover:bg-transparent';

interface AIFieldDisplayProps {
  title: string;
  content: string | null | undefined;
  height?: string;
  onRegenerate?: () => void;
  onUpdate?: (newContent: string) => Promise<void>;
  isRegenerating?: boolean;
  isLoading?: boolean;
  useMarkdown?: boolean;
}

export function AIFieldDisplay({
  title,
  content,
  height = 'h-48',
  onRegenerate,
  onUpdate,
  isRegenerating = false,
  isLoading = false,
  useMarkdown = true,
}: AIFieldDisplayProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Check if there are unsaved changes
  const hasUnsavedChanges = isEditing && editedContent !== originalContent;

  // Handle Ctrl+S to save changes
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (isEditing && hasUnsavedChanges && !isSaving && onUpdate) {
          handleSaveEdit();
        }
      }
    };

    if (isEditing) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isEditing, hasUnsavedChanges, isSaving, editedContent, originalContent]);

  const handleEditClick = () => {
    setOriginalContent(content || '');
    setEditedContent(content || '');
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setEditedContent('');
    setOriginalContent('');
    setIsEditing(false);
  };

  const handleSaveEdit = async () => {
    if (!onUpdate) return;

    setIsSaving(true);
    try {
      await onUpdate(editedContent);
      setIsEditing(false);
      setOriginalContent('');
    } catch (error) {
      console.error('Failed to save edit:', error);
      // Error handling is done in the parent component
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className='flex flex-col'>
      <CardHeader className='px-3 pt-1.5 pb-1.5 pr-1.5 shrink-0'>
        <div className='flex items-center justify-between gap-2'>
          <CardTitle className='text-sm'>
            {title}
            {hasUnsavedChanges && <span className='text-amber-500'>*</span>}
          </CardTitle>
          <div className='flex items-center gap-1 shrink-0'>
            {onUpdate && !isEditing && (
              <Button
                size='sm'
                variant='ghost'
                onClick={handleEditClick}
                disabled={isRegenerating || isLoading}
                className={`h-5 w-5 p-0 ${BUTTON_OPACITY_CLASS}`}
                title='Edit this field'
              >
                <SquarePen className='h-3 w-3' />
              </Button>
            )}
            {isEditing && (
              <>
                <Button
                  size='sm'
                  variant='ghost'
                  onClick={handleCancelEdit}
                  disabled={isSaving}
                  className={`h-5 w-5 p-0 ${BUTTON_OPACITY_CLASS}`}
                  title='Cancel editing'
                >
                  <X className='h-3 w-3' />
                </Button>
                <Button
                  size='sm'
                  variant='ghost'
                  onClick={handleSaveEdit}
                  disabled={isSaving || !hasUnsavedChanges}
                  className={`h-5 w-5 p-0 ${BUTTON_OPACITY_CLASS}`}
                  title='Save changes'
                >
                  <Save
                    className={`h-3 w-3 ${isSaving ? 'animate-pulse' : ''}`}
                  />
                </Button>
              </>
            )}
            {onRegenerate && !isEditing && (
              <Button
                size='sm'
                variant='ghost'
                onClick={onRegenerate}
                disabled={isRegenerating || isLoading}
                className={`h-5 w-5 p-0 ${BUTTON_OPACITY_CLASS}`}
                title='Regenerate this field'
              >
                <RefreshCw
                  className={`h-3 w-3 ${isRegenerating ? 'animate-spin' : ''}`}
                />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent
        className={`${height} overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent hover:scrollbar-thumb-gray-500`}
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgb(156 163 175) transparent',
        }}
      >
        {isLoading && !isRegenerating ? (
          <div className='flex items-center justify-center py-4'>
            <RefreshCw className='h-4 w-4 animate-spin text-muted-foreground' />
          </div>
        ) : isEditing ? (
          <Textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className='w-full h-full min-h-full text-xs resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 p-0 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent hover:scrollbar-thumb-gray-500'
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: 'rgb(156 163 175) transparent',
            }}
            placeholder='Enter markdown content...'
            disabled={isSaving}
          />
        ) : (
          <div className='text-xs prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-p:text-xs prose-headings:my-1 prose-headings:text-xs prose-ul:my-1 prose-ul:text-xs prose-ol:my-1 prose-ol:text-xs prose-li:my-0.5 prose-li:text-xs prose-strong:text-xs prose-em:text-xs'>
            {content ? (
              useMarkdown ? (
                <ReactMarkdown>{content}</ReactMarkdown>
              ) : (
                <div className='whitespace-pre-wrap'>{content}</div>
              )
            ) : (
              <span className='text-muted-foreground text-xs'>
                Not available
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
