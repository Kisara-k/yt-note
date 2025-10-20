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
import { API_BASE_URL } from '@/lib/config';
import { useRouter } from 'next/navigation';
import { validateAndNormalizeBookId } from '@/lib/book-id-validation';
import { parseAndNormalizeChapters } from '@/lib/book-json-parser';

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

      // Use the shared parser and normalizer
      const normalizedChapters = parseAndNormalizeChapters(chaptersJson);

      const response = await fetch(`${API_BASE_URL}/api/book`, {
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
