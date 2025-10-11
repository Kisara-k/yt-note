'use client';

import React, { useEffect } from 'react';
import {
  useEditor,
  EditorContent,
  Editor as TiptapEditor,
} from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Markdown } from 'tiptap-markdown';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import Underline from '@tiptap/extension-underline';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { Separator } from '@/components/ui/separator';
import { Toggle } from '@/components/ui/toggle';
import { cn } from '@/lib/utils';
import {
  Bold,
  Italic,
  Strikethrough,
  Code,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  Quote,
  Undo,
  Redo,
  Link as LinkIcon,
  Image as ImageIcon,
  CheckSquare,
  Underline as UnderlineIcon,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface TiptapMarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
  placeholder?: string;
  onInitialLoad?: () => void;
}

interface MarkdownStorage {
  getMarkdown: () => string;
}

const getMarkdownFromEditor = (editor: TiptapEditor): string => {
  // @ts-expect-error - markdown storage is added by tiptap-markdown extension
  return (editor.storage.markdown as MarkdownStorage).getMarkdown();
};

const MenuBar = ({ editor }: { editor: any }) => {
  const [linkUrl, setLinkUrl] = React.useState('');
  const [imageUrl, setImageUrl] = React.useState('');
  const [linkOpen, setLinkOpen] = React.useState(false);
  const [imageOpen, setImageOpen] = React.useState(false);

  if (!editor) {
    return null;
  }

  const addLink = () => {
    if (linkUrl) {
      editor.chain().focus().setLink({ href: linkUrl }).run();
      setLinkUrl('');
      setLinkOpen(false);
    }
  };

  const addImage = () => {
    if (imageUrl) {
      editor.chain().focus().setImage({ src: imageUrl }).run();
      setImageUrl('');
      setImageOpen(false);
    }
  };

  return (
    <div className='border-b p-2 flex flex-wrap items-center gap-1'>
      <Toggle
        size='sm'
        pressed={editor.isActive('bold')}
        onPressedChange={() => editor.chain().focus().toggleBold().run()}
      >
        <Bold className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('italic')}
        onPressedChange={() => editor.chain().focus().toggleItalic().run()}
      >
        <Italic className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('underline')}
        onPressedChange={() => editor.chain().focus().toggleUnderline().run()}
      >
        <UnderlineIcon className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('strike')}
        onPressedChange={() => editor.chain().focus().toggleStrike().run()}
      >
        <Strikethrough className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('code')}
        onPressedChange={() => editor.chain().focus().toggleCode().run()}
      >
        <Code className='h-4 w-4' />
      </Toggle>

      <Separator orientation='vertical' className='mx-1 h-8' />

      <Toggle
        size='sm'
        pressed={editor.isActive('heading', { level: 1 })}
        onPressedChange={() =>
          editor.chain().focus().toggleHeading({ level: 1 }).run()
        }
      >
        <Heading1 className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('heading', { level: 2 })}
        onPressedChange={() =>
          editor.chain().focus().toggleHeading({ level: 2 }).run()
        }
      >
        <Heading2 className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('heading', { level: 3 })}
        onPressedChange={() =>
          editor.chain().focus().toggleHeading({ level: 3 }).run()
        }
      >
        <Heading3 className='h-4 w-4' />
      </Toggle>

      <Separator orientation='vertical' className='mx-1 h-8' />

      <Toggle
        size='sm'
        pressed={editor.isActive('bulletList')}
        onPressedChange={() => editor.chain().focus().toggleBulletList().run()}
      >
        <List className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('orderedList')}
        onPressedChange={() => editor.chain().focus().toggleOrderedList().run()}
      >
        <ListOrdered className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('taskList')}
        onPressedChange={() => editor.chain().focus().toggleTaskList().run()}
      >
        <CheckSquare className='h-4 w-4' />
      </Toggle>

      <Toggle
        size='sm'
        pressed={editor.isActive('blockquote')}
        onPressedChange={() => editor.chain().focus().toggleBlockquote().run()}
      >
        <Quote className='h-4 w-4' />
      </Toggle>

      <Separator orientation='vertical' className='mx-1 h-8' />

      <Popover open={linkOpen} onOpenChange={setLinkOpen}>
        <PopoverTrigger asChild>
          <Button
            variant='ghost'
            size='sm'
            className={cn(
              'h-8 w-8 p-0',
              editor.isActive('link') && 'bg-accent'
            )}
          >
            <LinkIcon className='h-4 w-4' />
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-80'>
          <div className='grid gap-4'>
            <div className='space-y-2'>
              <h4 className='font-medium leading-none'>Insert Link</h4>
            </div>
            <div className='grid gap-2'>
              <Label htmlFor='link'>URL</Label>
              <Input
                id='link'
                placeholder='https://example.com'
                value={linkUrl}
                onChange={(e) => setLinkUrl(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    addLink();
                  }
                }}
              />
              <Button onClick={addLink} size='sm'>
                Add Link
              </Button>
            </div>
          </div>
        </PopoverContent>
      </Popover>

      <Popover open={imageOpen} onOpenChange={setImageOpen}>
        <PopoverTrigger asChild>
          <Button variant='ghost' size='sm' className='h-8 w-8 p-0'>
            <ImageIcon className='h-4 w-4' />
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-80'>
          <div className='grid gap-4'>
            <div className='space-y-2'>
              <h4 className='font-medium leading-none'>Insert Image</h4>
            </div>
            <div className='grid gap-2'>
              <Label htmlFor='image'>Image URL</Label>
              <Input
                id='image'
                placeholder='https://example.com/image.jpg'
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    addImage();
                  }
                }}
              />
              <Button onClick={addImage} size='sm'>
                Add Image
              </Button>
            </div>
          </div>
        </PopoverContent>
      </Popover>

      <Separator orientation='vertical' className='mx-1 h-8' />

      <Button
        variant='ghost'
        size='sm'
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
        className='h-8 w-8 p-0'
      >
        <Undo className='h-4 w-4' />
      </Button>

      <Button
        variant='ghost'
        size='sm'
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
        className='h-8 w-8 p-0'
      >
        <Redo className='h-4 w-4' />
      </Button>
    </div>
  );
};

export function TiptapMarkdownEditor({
  value,
  onChange,
  className,
  placeholder = 'Start writing...',
  onInitialLoad,
}: TiptapMarkdownEditorProps) {
  const isUpdatingFromProps = React.useRef(false);

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6],
        },
      }),
      Markdown.configure({
        html: true,
        tightLists: true,
        bulletListMarker: '-',
        linkify: true,
        breaks: false,
        transformPastedText: true,
        transformCopiedText: true,
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-500 underline cursor-pointer',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full h-auto rounded-lg',
        },
      }),
      Underline,
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
    ],
    content: value,
    editorProps: {
      attributes: {
        class:
          'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none min-h-[500px] p-5',
      },
    },
    onUpdate: ({ editor }) => {
      if (!isUpdatingFromProps.current) {
        const markdown = getMarkdownFromEditor(editor);
        onChange(markdown);
      }
    },
  });

  // Update editor content when value changes externally
  useEffect(() => {
    if (editor) {
      const currentMarkdown = getMarkdownFromEditor(editor);
      if (value !== currentMarkdown) {
        isUpdatingFromProps.current = true;
        editor.commands.setContent(value);
        // Clear undo history to prevent undoing back to empty state
        editor.commands.clearContent();
        editor.commands.setContent(value);
        // Reset flag after a short delay to allow the update to complete
        setTimeout(() => {
          isUpdatingFromProps.current = false;
          onInitialLoad?.();
        }, 0);
      }
    }
  }, [value, editor, onInitialLoad]);

  if (!editor) {
    return null;
  }

  return (
    <div className={cn('border rounded-lg shadow-sm bg-background', className)}>
      <MenuBar editor={editor} />
      <EditorContent editor={editor} />
    </div>
  );
}
