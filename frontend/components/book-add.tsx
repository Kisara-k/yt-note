'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Filter } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';

export function BookAdd() {
  const [bookId, setBookId] = useState('');
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [description, setDescription] = useState('');
  const [chaptersJson, setChaptersJson] = useState('');
  const [uploading, setUploading] = useState(false);
  const { getAccessToken } = useAuth();
  const router = useRouter();

  const handleUpload = async () => {
    if (!bookId.trim() || !title.trim() || !chaptersJson.trim()) {
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
        chaptersData = JSON.parse(chaptersJson);
        if (!Array.isArray(chaptersData)) {
          throw new Error('JSON must be an array of chapters');
        }
      } catch (err) {
        throw new Error(
          'Invalid JSON format. Expected array of {chapter_title, chapter_text}'
        );
      }

      const response = await fetch('http://localhost:8000/api/book', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          book_id: bookId,
          title: title,
          author: author || null,
          description: description || null,
          chapters: chaptersData,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        const errorMessage =
          typeof error.detail === 'string'
            ? error.detail
            : error.error || error.message || 'Failed to upload book';
        throw new Error(errorMessage);
      }

      router.push(`/book?b=${bookId}`);
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
                Books
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
                placeholder='e.g., practical_guide_123'
                value={bookId}
                onChange={(e) => setBookId(e.target.value)}
                disabled={uploading}
              />
              <p className='text-sm text-muted-foreground'>
                Unique identifier for this book
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
                  '[\n  {\n    "chapter_title": "Chapter 1: Title",\n    "chapter_text": "Chapter content here..."\n  }\n]'
                }
                value={chaptersJson}
                onChange={(e) => setChaptersJson(e.target.value)}
                disabled={uploading}
                rows={10}
                className='font-mono text-sm'
              />
              <p className='text-sm text-muted-foreground'>
                JSON array with chapter_title and chapter_text for each chapter
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
