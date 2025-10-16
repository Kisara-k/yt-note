'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { Save, Loader2 } from 'lucide-react';

interface NoteEditorProps {
  title?: string;
  value: string;
  onChange: (value: string) => void;
  onSave: () => void;
  onInitialLoad?: () => void;
  isSaving: boolean;
  hasUnsavedChanges: boolean;
  placeholder?: string;
  minHeight?: string;
  disabled?: boolean;
}

export function NoteEditor({
  title = 'Note',
  value,
  onChange,
  onSave,
  onInitialLoad,
  isSaving,
  hasUnsavedChanges,
  placeholder = 'Start writing your notes here...',
  minHeight = 'min-h-[100px]',
  disabled = false,
}: NoteEditorProps) {
  // Handle Ctrl+S to save the note
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (!isSaving && hasUnsavedChanges && !disabled) {
          onSave();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onSave, isSaving, hasUnsavedChanges, disabled]);

  return (
    <Card>
      <CardHeader className='px-3 pt-1.5 pb-1.5'>
        <div className='flex items-center justify-between'>
          <CardTitle className='text-sm'>
            {title}{' '}
            {hasUnsavedChanges && <span className='text-amber-500'>*</span>}
          </CardTitle>
          <Button
            onClick={onSave}
            disabled={isSaving || !hasUnsavedChanges || disabled}
            variant='outline'
            size='sm'
            className='h-7 px-2 w-20 relative'
          >
            {isSaving ? (
              <div className='flex items-center justify-center w-full pl-5'>
                <Loader2 className='absolute left-2 h-3 w-3 animate-spin' />
                <span className='text-xs'>Saving...</span>
              </div>
            ) : (
              <div className='flex items-center justify-center w-full pl-5'>
                <Save className='absolute left-2 h-3 w-3' />
                <span className='text-xs'>Save</span>
              </div>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className='p-3 pt-0'>
        <TiptapMarkdownEditor
          value={value}
          onChange={onChange}
          className={minHeight}
          placeholder={placeholder}
          onInitialLoad={onInitialLoad}
        />
      </CardContent>
    </Card>
  );
}
