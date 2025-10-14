'use client';

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
  minHeight = 'min-h-[150px]',
  disabled = false,
}: NoteEditorProps) {
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
            variant='default'
            size='sm'
            className='h-7 px-2'
          >
            {isSaving ? (
              <>
                <Loader2 className='mr-2 h-3 w-3 animate-spin' />
                Saving...
              </>
            ) : (
              <>
                <Save className='mr-2 h-3 w-3' />
                Save Note
              </>
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
