'use client';

import { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { RefreshCw, SquarePen, Save, X } from 'lucide-react';
import { reactMarkdownComponents } from '@/lib/markdown-styles';

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
  scrollableHeader?: boolean;
}

export function AIFieldDisplay({
  title,
  content,
  height = 'h-96',
  onRegenerate,
  onUpdate,
  isRegenerating = false,
  isLoading = false,
  useMarkdown = true,
  scrollableHeader = false,
}: AIFieldDisplayProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Check if there are unsaved changes
  const hasUnsavedChanges = isEditing && editedContent !== originalContent;

  // Define handleSaveEdit before useEffect
  const handleSaveEdit = useCallback(async () => {
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
  }, [onUpdate, editedContent]);

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
  }, [isEditing, hasUnsavedChanges, isSaving, handleSaveEdit, onUpdate]);

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

  const scrollbarClasses =
    'scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent hover:scrollbar-thumb-gray-500';
  const scrollbarStyles = {
    scrollbarWidth: 'thin' as const,
    scrollbarColor: 'rgba(156, 163, 175, 0.3) transparent',
  };

  const headerContent = (
    <CardHeader
      className={`px-3 pt-0.5 pb-0.5 pr-1.5 bg-muted text-muted-foreground/40 ${
        scrollableHeader ? '' : 'shrink-0 rounded-t-lg'
      }`}
    >
      <div className='flex items-center justify-between gap-2'>
        <CardTitle className='text-sm'>
          {title}
          {hasUnsavedChanges && <span className='text-amber-500'> *</span>}
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
  );

  const contentArea = (
    <CardContent
      className={`pt-1 ${
        scrollableHeader ? '' : `${height} overflow-y-auto ${scrollbarClasses}`
      }`}
      style={scrollableHeader ? undefined : scrollbarStyles}
    >
      {isLoading && !isRegenerating ? (
        <div className='flex items-center justify-center py-4'>
          <RefreshCw className='h-4 w-4 animate-spin text-muted-foreground' />
        </div>
      ) : isEditing ? (
        <Textarea
          value={editedContent}
          onChange={(e) => setEditedContent(e.target.value)}
          className={`w-full text-xs resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 p-0 ${
            scrollableHeader
              ? 'min-h-[500px]'
              : `h-full min-h-full ${scrollbarClasses}`
          }`}
          style={scrollableHeader ? undefined : scrollbarStyles}
          placeholder='Enter markdown content...'
          disabled={isSaving}
        />
      ) : (
        <div className='text-xs'>
          {content ? (
            useMarkdown ? (
              <ReactMarkdown
                remarkPlugins={[remarkMath, remarkGfm]}
                rehypePlugins={[rehypeKatex]}
                components={reactMarkdownComponents}
              >
                {content}
              </ReactMarkdown>
            ) : (
              <div className='whitespace-pre-wrap'>{content}</div>
            )
          ) : (
            <span className='text-muted-foreground text-xs'>Not available</span>
          )}
        </div>
      )}
    </CardContent>
  );

  return (
    <Card
      className={`flex flex-col ${
        scrollableHeader ? `${height} overflow-hidden` : ''
      }`}
    >
      {scrollableHeader ? (
        <div
          className={`overflow-y-auto ${scrollbarClasses}`}
          style={scrollbarStyles}
        >
          {headerContent}
          {contentArea}
        </div>
      ) : (
        <>
          {headerContent}
          {contentArea}
        </>
      )}
    </Card>
  );
}
