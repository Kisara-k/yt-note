"""
Generate remaining book components - book-add and book-filter
"""

# Book Add Component
BOOK_ADD = """'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, BookOpen, LogOut, User, Filter } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';

export function BookAdd() {
  const [bookId, setBookId] = useState('');
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [description, setDescription] = useState('');
  const [chaptersJson, setChaptersJson] = useState('');
  const [uploading, setUploading] = useState(false);
  const { getAccessToken, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Failed to sign out:', error);
    }
  };

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
      <div className='bg-card border-b sticky top-0 z-10'>
        <div className='container mx-auto px-6 py-4'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center gap-4'>
              <BookOpen className='h-6 w-6' />
              <span className='text-lg font-semibold'>Add New Book</span>
            </div>
            <div className='flex items-center gap-2'>
              <Button
                variant='ghost'
                size='sm'
                onClick={() => router.push('/book')}
              >
                <BookOpen className='h-4 w-4 mr-2' />
                Books
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={() => router.push('/book/filter')}
              >
                <Filter className='h-4 w-4 mr-2' />
                Filter
              </Button>
              <Button variant='ghost' size='sm' onClick={handleSignOut}>
                <User className='h-4 w-4 mr-2' />
                <LogOut className='h-4 w-4' />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className='container mx-auto px-6 py-8 max-w-3xl'>
        <Card>
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
                placeholder={'[\\n  {\\n    "chapter_title": "Chapter 1: Title",\\n    "chapter_text": "Chapter content here..."\\n  }\\n]'}
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
                uploading || !bookId.trim() || !title.trim() || !chaptersJson.trim()
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
"""

# Book Filter Component  
BOOK_FILTER = """'use client';

import { useState, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Loader2,
  Filter,
  X,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  BookOpen,
  LogOut,
  User,
  Plus,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface BookInfo {
  id: string;
  title: string;
  author: string;
  publisher: string;
  publication_year: number;
  tags: string[];
  created_at: string;
}

type SortField = 'title' | 'author' | 'publication_year' | 'created_at';
type SortDirection = 'asc' | 'desc' | null;

export function BookFilter() {
  const [books, setBooks] = useState<BookInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortField, setSortField] = useState<SortField | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [filters, setFilters] = useState({
    author: '',
    title: '',
    selectedTags: [] as string[],
  });
  const { getAccessToken, signOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        return;
      }

      const response = await fetch('http://localhost:8000/api/books', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load books');
      }

      const data = await response.json();
      setBooks(data.books || []);
    } catch (error) {
      console.error('Error loading books:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Failed to sign out:', error);
    }
  };

  const toggleTag = (tagKey: string) => {
    setFilters((prev) => ({
      ...prev,
      selectedTags: prev.selectedTags.includes(tagKey)
        ? prev.selectedTags.filter((t) => t !== tagKey)
        : [...prev.selectedTags, tagKey],
    }));
  };

  const clearFilters = () => {
    setFilters({
      author: '',
      title: '',
      selectedTags: [],
    });
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortField(null);
      }
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className='h-4 w-4 ml-1 text-muted-foreground' />;
    }
    if (sortDirection === 'asc') {
      return <ArrowUp className='h-4 w-4 ml-1' />;
    }
    if (sortDirection === 'desc') {
      return <ArrowDown className='h-4 w-4 ml-1' />;
    }
    return <ArrowUpDown className='h-4 w-4 ml-1 text-muted-foreground' />;
  };

  const allTags = useMemo(() => {
    const tagSet = new Set<string>();
    books.forEach((book) => {
      if (book.tags) {
        book.tags.forEach((tag) => tagSet.add(tag));
      }
    });
    return Array.from(tagSet).sort();
  }, [books]);

  const filteredAndSortedBooks = useMemo(() => {
    let result = [...books];

    if (filters.title) {
      result = result.filter((book) =>
        book.title.toLowerCase().includes(filters.title.toLowerCase())
      );
    }

    if (filters.author) {
      result = result.filter((book) =>
        book.author?.toLowerCase().includes(filters.author.toLowerCase())
      );
    }

    if (filters.selectedTags.length > 0) {
      result = result.filter((book) =>
        filters.selectedTags.some((tag) => book.tags?.includes(tag))
      );
    }

    if (sortField && sortDirection) {
      result.sort((a, b) => {
        let aVal = a[sortField];
        let bVal = b[sortField];

        if (typeof aVal === 'string') aVal = aVal.toLowerCase();
        if (typeof bVal === 'string') bVal = bVal.toLowerCase();

        if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [books, filters, sortField, sortDirection]);

  return (
    <div className='min-h-screen bg-background'>
      <div className='bg-card border-b sticky top-0 z-10'>
        <div className='container mx-auto px-6 py-4'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center gap-4'>
              <BookOpen className='h-6 w-6' />
              <span className='text-lg font-semibold'>Filter Books</span>
            </div>
            <div className='flex items-center gap-2'>
              <Button
                variant='ghost'
                size='sm'
                onClick={() => router.push('/book')}
              >
                <BookOpen className='h-4 w-4 mr-2' />
                Books
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={() => router.push('/book/add')}
              >
                <Plus className='h-4 w-4 mr-2' />
                Add Book
              </Button>
              <Button variant='ghost' size='sm' onClick={handleSignOut}>
                <User className='h-4 w-4 mr-2' />
                <LogOut className='h-4 w-4' />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className='container mx-auto px-6 py-8 max-w-6xl'>
        <Card className='mb-6'>
          <CardHeader>
            <div className='flex items-center justify-between'>
              <CardTitle>Filters</CardTitle>
              <Button
                variant='ghost'
                size='sm'
                onClick={clearFilters}
                disabled={
                  !filters.author &&
                  !filters.title &&
                  filters.selectedTags.length === 0
                }
              >
                <X className='h-4 w-4 mr-2' />
                Clear
              </Button>
            </div>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid grid-cols-2 gap-4'>
              <div className='space-y-2'>
                <Label htmlFor='filter-title'>Title</Label>
                <Input
                  id='filter-title'
                  type='text'
                  placeholder='Search by title...'
                  value={filters.title}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, title: e.target.value }))
                  }
                />
              </div>

              <div className='space-y-2'>
                <Label htmlFor='filter-author'>Author</Label>
                <Input
                  id='filter-author'
                  type='text'
                  placeholder='Search by author...'
                  value={filters.author}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, author: e.target.value }))
                  }
                />
              </div>
            </div>

            {allTags.length > 0 && (
              <div className='space-y-2'>
                <Label>Tags</Label>
                <div className='flex flex-wrap gap-2'>
                  {allTags.map((tag) => (
                    <Button
                      key={tag}
                      variant={
                        filters.selectedTags.includes(tag) ? 'default' : 'outline'
                      }
                      size='sm'
                      onClick={() => toggleTag(tag)}
                    >
                      {tag}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              Books ({filteredAndSortedBooks.length} of {books.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className='flex items-center justify-center py-8'>
                <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
              </div>
            ) : filteredAndSortedBooks.length === 0 ? (
              <div className='text-center py-8 text-muted-foreground'>
                <BookOpen className='h-12 w-12 mx-auto mb-4 opacity-20' />
                <p>No books found</p>
              </div>
            ) : (
              <div className='border rounded-lg overflow-hidden'>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>
                        <Button
                          variant='ghost'
                          size='sm'
                          className='h-8 p-0 hover:bg-transparent'
                          onClick={() => handleSort('title')}
                        >
                          Title
                          {getSortIcon('title')}
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button
                          variant='ghost'
                          size='sm'
                          className='h-8 p-0 hover:bg-transparent'
                          onClick={() => handleSort('author')}
                        >
                          Author
                          {getSortIcon('author')}
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button
                          variant='ghost'
                          size='sm'
                          className='h-8 p-0 hover:bg-transparent'
                          onClick={() => handleSort('publication_year')}
                        >
                          Year
                          {getSortIcon('publication_year')}
                        </Button>
                      </TableHead>
                      <TableHead>Tags</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredAndSortedBooks.map((book) => (
                      <TableRow key={book.id}>
                        <TableCell className='font-medium'>
                          {book.title}
                        </TableCell>
                        <TableCell>{book.author || '-'}</TableCell>
                        <TableCell>{book.publication_year || '-'}</TableCell>
                        <TableCell>
                          <div className='flex gap-1 flex-wrap'>
                            {book.tags?.slice(0, 3).map((tag, i) => (
                              <span
                                key={i}
                                className='text-xs bg-secondary px-2 py-1 rounded'
                              >
                                {tag}
                              </span>
                            ))}
                            {book.tags?.length > 3 && (
                              <span className='text-xs text-muted-foreground'>
                                +{book.tags.length - 3}
                              </span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Link href={`/book?b=${book.id}`}>
                            <Button variant='outline' size='sm'>
                              View
                            </Button>
                          </Link>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
"""

# Write files
with open("../frontend/components/book-add.tsx", 'w', encoding='utf-8') as f:
    f.write(BOOK_ADD)
print("✓ Created ../frontend/components/book-add.tsx")

with open("../frontend/components/book-filter.tsx", 'w', encoding='utf-8') as f:
    f.write(BOOK_FILTER)
print("✓ Created ../frontend/components/book-filter.tsx")

print("\nAll book components created successfully!")
