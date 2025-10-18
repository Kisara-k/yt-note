'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, Filter } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { validateAndNormalizeBookId } from '@/lib/book-id-validation';

// Utility to clean JSON (remove trailing commas, comments, etc.)
function cleanJSON(jsonStr: string): string {
  // Remove trailing commas before closing brackets/braces
  let cleaned = jsonStr.replace(/,(\s*[}\]])/g, '$1');

  // Remove single-line comments (// style)
  cleaned = cleaned.replace(/\/\/.*$/gm, '');

  // Remove multi-line comments (/* */ style)
  cleaned = cleaned.replace(/\/\*[\s\S]*?\*\//g, '');

  // Trim whitespace
  cleaned = cleaned.trim();

  return cleaned;
}

// Parse JSON that may or may not be wrapped in an array
function parseFlexibleJSON(jsonStr: string): any[] {
  let cleaned = cleanJSON(jsonStr);

  // Remove trailing comma at the very end (for formats like: {...}, {...},)
  cleaned = cleaned.replace(/,\s*$/, '');

  // Try parsing as-is first
  try {
    const parsed = JSON.parse(cleaned);
    if (Array.isArray(parsed)) {
      return parsed;
    }
    // If it's a single object, wrap it in an array
    if (typeof parsed === 'object' && parsed !== null) {
      return [parsed];
    }
  } catch (e) {
    // If parsing fails, it might be multiple objects separated by commas or newlines
  }

  // Try wrapping in array brackets (for formats like: {...}, {...})
  if (!cleaned.startsWith('[')) {
    try {
      const wrapped = `[${cleaned}]`;
      const parsed = JSON.parse(wrapped);
      if (Array.isArray(parsed)) {
        return parsed;
      }
    } catch (e) {
      // Still failed, try line-separated approach
    }
  }

  // Try parsing as newline-separated JSON objects (for formats like: {...}\n{...}\n)
  try {
    const lines = cleaned.split('\n').filter((line) => line.trim());
    const objects = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
        // Remove trailing comma if exists
        const cleanLine = trimmed.replace(/,$/, '');
        objects.push(JSON.parse(cleanLine));
      } else if (trimmed.startsWith('{')) {
        // Handle multi-line objects - collect until we find closing brace
        let objStr = trimmed;
        // This is a simplified approach - for complex cases, wrapping in [] already works
        objects.push(JSON.parse(objStr));
      }
    }

    if (objects.length > 0) {
      return objects;
    }
  } catch (e) {
    // Failed
  }

  // Last resort: throw original error
  throw new Error(
    'Unable to parse JSON. Try wrapping in [] or ensure valid JSON format.'
  );
}

// Normalize chapter data (handle different field names)
function normalizeChapters(
  chapters: any[]
): Array<{ title: string; content: string }> {
  return chapters
    .map((ch, idx) => {
      // Handle different field name variations
      const title =
        ch.title ||
        ch.chapter_title ||
        ch.name ||
        ch.heading ||
        `Chapter ${idx + 1}`;
      const content = ch.content || ch.chapter_text || ch.text || ch.body || '';

      return {
        title: String(title).trim(),
        content: String(content).trim(),
      };
    })
    .filter((ch) => ch.content); // Only keep chapters with actual content
}

export function BookAdd() {
  const [bookId, setBookId] = useState('');
  const [bookIdError, setBookIdError] = useState('');
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [description, setDescription] = useState('');
  const [bookType, setBookType] = useState('book');
  const [chaptersJson, setChaptersJson] = useState('');
  const [uploading, setUploading] = useState(false);
  const { getAccessToken } = useAuth();
  const router = useRouter();

  const handleBookIdChange = (value: string) => {
    setBookId(value);

    // Clear error when user starts typing
    if (bookIdError && value.trim()) {
      setBookIdError('');
    }
  };

  const handleUpload = async () => {
    if (!bookId.trim() || !title.trim() || !chaptersJson.trim()) {
      alert('Please fill in Book ID, Title, and Chapters JSON');
      return;
    }

    // Validate and normalize book ID
    const { isValid, normalized, error } = validateAndNormalizeBookId(bookId);
    if (!isValid) {
      setBookIdError(error || 'Invalid book ID');
      alert(error || 'Invalid book ID');
      return;
    }

    setUploading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        setUploading(false);
        return;
      }

      let chaptersData;
      try {
        // Use flexible parser that handles both formats:
        // - [{...}, {...}]
        // - {...}, {...}
        // - {...}\n{...}
        chaptersData = parseFlexibleJSON(chaptersJson);

        if (!Array.isArray(chaptersData)) {
          throw new Error('Unable to parse as array of chapters');
        }
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : 'Unknown error';
        throw new Error(
          `Invalid JSON format: ${errMsg}\n\nAccepted formats:\n` +
            `1. Array: [{"title": "...", "content": "..."}, ...]\n` +
            `2. Comma-separated: {...}, {...}, {...}\n` +
            `3. Line-separated: {...}\\n{...}\\n{...}`
        );
      }

      // Normalize chapters (handle different field names, remove empty ones)
      const normalizedChapters = normalizeChapters(chaptersData);

      if (normalizedChapters.length === 0) {
        throw new Error(
          'No valid chapters found. Each chapter must have content (fields: content, chapter_text, text, or body).'
        );
      }

      // Validate each chapter has both title and content
      const missingFields = [];
      for (let i = 0; i < normalizedChapters.length; i++) {
        const chapter = normalizedChapters[i];
        const chapterNum = i + 1;

        if (!chapter.title || !chapter.title.trim()) {
          missingFields.push(`Chapter ${chapterNum}: empty title`);
        }
        if (!chapter.content || !chapter.content.trim()) {
          missingFields.push(`Chapter ${chapterNum}: empty content`);
        }
      }

      if (missingFields.length > 0) {
        throw new Error(`Invalid chapters:\n${missingFields.join('\n')}`);
      }

      const response = await fetch('http://localhost:8000/api/book', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          book_id: normalized, // Use normalized book ID
          title: title,
          author: author || null,
          book_type: bookType,
          description: description || null,
          chapters: normalizedChapters,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        const errorMessage =
          typeof error.detail === 'string'
            ? error.detail
            : error.error || error.message || 'Failed to upload book';

        // Handle duplicate book ID error specifically
        if (
          response.status === 409 ||
          errorMessage.includes('already exists')
        ) {
          setBookIdError(errorMessage);
        }

        throw new Error(errorMessage);
      }

      router.push(`/book?b=${normalized}`); // Use normalized book ID in URL
    } catch (error) {
      console.error('Error uploading book:', error);
      alert(error instanceof Error ? error.message : 'Failed to upload book');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto p-6 max-w-7xl'>
        <div className='mb-8'>
          <div className='flex justify-between items-center mb-4'>
            <h1 className='text-3xl font-bold'>Add New Book</h1>
            <div className='flex items-center gap-2'>
              <Button
                variant='outline'
                size='sm'
                onClick={() => router.push('/book')}
              >
                Back to Notes
              </Button>
              <Button
                variant='outline'
                size='sm'
                onClick={() => router.push('/book/filter')}
              >
                <Filter className='mr-2 h-4 w-4' />
                All Books
              </Button>
            </div>
          </div>
        </div>

        <Card className='max-w-3xl mx-auto'>
          <CardHeader>
            <CardTitle>Upload a New Book</CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='space-y-2'>
              <Label htmlFor='book-id'>Book ID *</Label>
              <Input
                id='book-id'
                type='text'
                placeholder='e.g., practical_guide_123 or Practical Guide 123'
                value={bookId}
                onChange={(e) => handleBookIdChange(e.target.value)}
                disabled={uploading}
                className={bookIdError ? 'border-red-500' : ''}
              />
              {bookIdError && (
                <p className='text-sm text-red-500'>{bookIdError}</p>
              )}
              <p className='text-sm text-muted-foreground'>
                Unique identifier - letters, numbers, spaces, and underscores
                allowed (auto-normalized to lowercase with underscores)
              </p>
            </div>

            <div className='space-y-2'>
              <Label htmlFor='title'>Title *</Label>
              <Input
                id='title'
                type='text'
                placeholder='Book title'
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={uploading}
              />
            </div>

            <div className='space-y-2'>
              <Label htmlFor='author'>Author</Label>
              <Input
                id='author'
                type='text'
                placeholder='Author name'
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                disabled={uploading}
              />
            </div>

            <div className='space-y-2'>
              <Label htmlFor='book-type'>Type</Label>
              <Select
                value={bookType}
                onValueChange={setBookType}
                disabled={uploading}
              >
                <SelectTrigger id='book-type' className='w-full'>
                  <SelectValue placeholder='Select book type' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='book'>Book</SelectItem>
                  <SelectItem value='lecture'>Lecture</SelectItem>
                </SelectContent>
              </Select>
              <p className='text-sm text-muted-foreground'>
                Type affects AI prompt selection for content analysis
              </p>
            </div>

            <div className='space-y-2'>
              <Label htmlFor='description'>Description</Label>
              <Textarea
                id='description'
                placeholder='Book description'
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={uploading}
                rows={3}
              />
            </div>

            <div className='space-y-2'>
              <Label htmlFor='chapters'>Chapters JSON *</Label>
              <Textarea
                id='chapters'
                placeholder={
                  '[\n  {\n    "title": "Chapter 1: Introduction",\n    "content": "Chapter content here..."\n  },\n  {\n    "title": "Chapter 2: Getting Started",\n    "content": "More content..."\n  }\n]'
                }
                value={chaptersJson}
                onChange={(e) => setChaptersJson(e.target.value)}
                disabled={uploading}
                rows={10}
                className='font-mono text-sm'
              />
              <p className='text-sm text-muted-foreground'>
                JSON array with &quot;title&quot; and &quot;content&quot; for
                each chapter. Any other fields will be ignored.
              </p>
            </div>

            <Button
              onClick={handleUpload}
              disabled={
                uploading ||
                !bookId.trim() ||
                !title.trim() ||
                !chaptersJson.trim()
              }
              className='w-full'
            >
              {uploading ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Uploading...
                </>
              ) : (
                'Upload Book'
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
