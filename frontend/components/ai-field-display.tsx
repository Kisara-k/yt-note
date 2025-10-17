'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
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
  height = 'h-64',
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
      <CardContent
        className={`${height} overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent hover:scrollbar-thumb-gray-500`}
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgba(156, 163, 175, 0.3) transparent',
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
          <div className='text-xs'>
            {content ? (
              useMarkdown ? (
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                  components={{
                    h1: ({ node, ...props }) => (
                      <h1
                        className='text-base font-medium mt-3 mb-2 first:mt-0'
                        {...props}
                      />
                    ),
                    h2: ({ node, ...props }) => (
                      <h2
                        className='text-sm font-medium mt-2.5 mb-1.5 first:mt-0'
                        {...props}
                      />
                    ),
                    h3: ({ node, ...props }) => (
                      <h3
                        className='text-xs font-medium mt-2 mb-1 first:mt-0'
                        {...props}
                      />
                    ),
                    h4: ({ node, ...props }) => (
                      <h4
                        className='text-xs font-semibold mt-2 mb-1 first:mt-0'
                        {...props}
                      />
                    ),
                    h5: ({ node, ...props }) => (
                      <h5
                        className='text-xs font-semibold mt-1.5 mb-0.5 first:mt-0'
                        {...props}
                      />
                    ),
                    h6: ({ node, ...props }) => (
                      <h6
                        className='text-xs font-semibold mt-1.5 mb-0.5 first:mt-0'
                        {...props}
                      />
                    ),
                    p: ({ node, ...props }) => (
                      <p className='text-xs my-1 leading-relaxed' {...props} />
                    ),
                    ul: ({ node, ...props }) => (
                      <ul className='text-xs my-1 ml-4 list-disc' {...props} />
                    ),
                    ol: ({ node, ...props }) => (
                      <ol
                        className='text-xs my-1 ml-4 list-decimal'
                        {...props}
                      />
                    ),
                    li: ({ node, ...props }) => (
                      <li className='text-xs my-0.5' {...props} />
                    ),
                    strong: ({ node, ...props }) => (
                      <strong className='font-bold' {...props} />
                    ),
                    em: ({ node, ...props }) => (
                      <em className='italic' {...props} />
                    ),
                    code: ({ node, className, ...props }) => {
                      const isInline = !className?.includes('language-');
                      return isInline ? (
                        <code
                          className='text-xs bg-muted px-1 py-0.5 rounded font-mono'
                          {...props}
                        />
                      ) : (
                        <code
                          className={`text-xs font-mono ${className || ''}`}
                          {...props}
                        />
                      );
                    },
                    pre: ({ node, ...props }) => (
                      <pre
                        className='text-xs bg-muted p-2 rounded my-2 overflow-x-auto'
                        {...props}
                      />
                    ),
                    blockquote: ({ node, ...props }) => (
                      <blockquote
                        className='text-xs border-l-2 border-gray-300 dark:border-gray-700 pl-3 my-2 italic'
                        {...props}
                      />
                    ),
                    a: ({ node, ...props }) => (
                      <a
                        className='text-xs text-blue-500 hover:underline'
                        {...props}
                      />
                    ),
                    hr: ({ node, ...props }) => (
                      <hr
                        className='my-2 border-gray-300 dark:border-gray-700'
                        {...props}
                      />
                    ),
                  }}
                >
                  {content}
                </ReactMarkdown>
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
