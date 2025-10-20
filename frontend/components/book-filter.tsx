'use client';

import { useState, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Loader2,
  Filter,
  X,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Trash2,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { API_BASE_URL } from '@/lib/config';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface BookInfo {
  id: string;
  title: string;
  author: string;
  publisher: string;
  publication_year: number;
  tags: string[];
  type: string;
  created_at: string;
}

type SortField = 'title' | 'author' | 'publication_year' | 'created_at';
type SortDirection = 'asc' | 'desc' | null;

export function BookFilter() {
  const [books, setBooks] = useState<BookInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [bookToDelete, setBookToDelete] = useState<{
    id: string;
    title: string;
  } | null>(null);
  const [sortField, setSortField] = useState<SortField | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [filters, setFilters] = useState({
    author: '',
    title: '',
    type: 'all' as 'all' | 'book' | 'lecture',
    selectedTags: [] as string[],
  });
  const { getAccessToken } = useAuth();
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

      const response = await fetch(`${API_BASE_URL}/api/books`, {
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
      type: 'all',
      selectedTags: [],
    });
  };

  const openDeleteDialog = (bookId: string, bookTitle: string) => {
    setBookToDelete({ id: bookId, title: bookTitle });
    setDeleteDialogOpen(true);
  };

  const handleDeleteBook = async () => {
    if (!bookToDelete) return;

    setDeletingId(bookToDelete.id);
    try {
      const token = await getAccessToken();
      if (!token) {
        return;
      }

      const response = await fetch(
        `${API_BASE_URL}/api/book/${bookToDelete.id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete book');
      }

      // Remove book from local state
      setBooks((prev) => prev.filter((b) => b.id !== bookToDelete.id));
      setDeleteDialogOpen(false);
      setBookToDelete(null);
    } catch (error) {
      console.error('Error deleting book:', error);
    } finally {
      setDeletingId(null);
    }
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

    if (filters.type !== 'all') {
      result = result.filter((book) => book.type === filters.type);
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
    <div className='min-h-screen bg-background p-6'>
      <div className='max-w-7xl mx-auto space-y-6'>
        <div className='flex justify-between items-center'>
          <h1 className='text-3xl font-bold'>Filter Books</h1>
          <div className='flex-1 flex justify-center'>
            <Link href='/book'>
              <Button variant='outline'>Back to Notes</Button>
            </Link>
          </div>
          <div className='w-[140px]'></div>
        </div>

        <Card>
          <CardContent className='pt-6 pb-4'>
            <div className='grid grid-cols-1 md:grid-cols-12 gap-3 items-end'>
              <div className='md:col-span-4'>
                <Label htmlFor='title' className='text-xs font-medium mb-1.5'>
                  Title
                </Label>
                <Input
                  id='title'
                  placeholder='Search by title...'
                  className='h-9'
                  value={filters.title}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, title: e.target.value }))
                  }
                />
              </div>

              <div className='md:col-span-3'>
                <Label htmlFor='author' className='text-xs font-medium mb-1.5'>
                  Author
                </Label>
                <Input
                  id='author'
                  placeholder='Search by author...'
                  className='h-9'
                  value={filters.author}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, author: e.target.value }))
                  }
                />
              </div>

              <div className='md:col-span-2'>
                <Label htmlFor='type' className='text-xs font-medium mb-1.5'>
                  Type
                </Label>
                <Select
                  value={filters.type}
                  onValueChange={(value: 'all' | 'book' | 'lecture') =>
                    setFilters((prev) => ({ ...prev, type: value }))
                  }
                >
                  <SelectTrigger id='type' className='h-9 w-full'>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value='all'>All Types</SelectItem>
                    <SelectItem value='book'>Book</SelectItem>
                    <SelectItem value='lecture'>Lecture</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className='md:col-span-2 flex justify-end'>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={clearFilters}
                  className='h-9 px-3'
                  title='Clear Filters'
                >
                  <X className='h-4 w-4' />
                </Button>
              </div>
            </div>

            <div className='mt-3 text-xs text-muted-foreground'>
              Showing {filteredAndSortedBooks.length} of {books.length} books
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className='flex items-center justify-center p-12'>
            <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
          </div>
        ) : filteredAndSortedBooks.length > 0 ? (
          <Card>
            <CardContent className='p-0'>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className='w-[30%]'>
                      <Button
                        variant='ghost'
                        size='sm'
                        className='h-8 font-medium'
                        onClick={() => handleSort('title')}
                      >
                        Title
                        {getSortIcon('title')}
                      </Button>
                    </TableHead>
                    <TableHead className='w-[15%]'>
                      <Button
                        variant='ghost'
                        size='sm'
                        className='h-8 font-medium'
                        onClick={() => handleSort('author')}
                      >
                        Author
                        {getSortIcon('author')}
                      </Button>
                    </TableHead>
                    <TableHead className='w-[10%]'>Type</TableHead>
                    <TableHead className='w-[10%]'>
                      <Button
                        variant='ghost'
                        size='sm'
                        className='h-8 font-medium'
                        onClick={() => handleSort('publication_year')}
                      >
                        Year
                        {getSortIcon('publication_year')}
                      </Button>
                    </TableHead>
                    <TableHead className='w-[15%]'>Tags</TableHead>
                    <TableHead className='w-[15%]'>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAndSortedBooks.map((book) => (
                    <TableRow key={book.id} className='h-12'>
                      <TableCell className='font-medium py-2'>
                        <Link
                          href={`/book?b=${book.id}`}
                          className='line-clamp-2 hover:underline text-primary'
                        >
                          {book.title}
                        </Link>
                      </TableCell>
                      <TableCell className='py-2'>
                        {book.author || '-'}
                      </TableCell>
                      <TableCell className='py-2'>
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${
                            book.type === 'lecture'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                              : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                          }`}
                        >
                          {book.type === 'lecture' ? '📚 Lecture' : '📖 Book'}
                        </span>
                      </TableCell>
                      <TableCell className='py-2'>
                        {book.publication_year || '-'}
                      </TableCell>
                      <TableCell className='py-2'>
                        <div className='flex flex-wrap gap-1'>
                          {book.tags?.slice(0, 2).map((tag: string) => (
                            <span
                              key={tag}
                              className='text-xs bg-secondary px-2 py-0.5 rounded'
                            >
                              {tag}
                            </span>
                          ))}
                          {book.tags?.length > 2 && (
                            <span className='text-xs text-muted-foreground'>
                              +{book.tags.length - 2}
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className='py-2'>
                        <div className='flex gap-2'>
                          <Link href={`/book?b=${book.id}`}>
                            <Button variant='outline' size='sm'>
                              View
                            </Button>
                          </Link>
                          <Button
                            variant='outline'
                            size='sm'
                            onClick={() =>
                              openDeleteDialog(book.id, book.title)
                            }
                            disabled={deletingId === book.id}
                          >
                            {deletingId === book.id ? (
                              <Loader2 className='h-4 w-4 animate-spin' />
                            ) : (
                              <Trash2 className='h-4 w-4' />
                            )}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className='p-12 text-center text-muted-foreground'>
              No books match your filters. Try adjusting your search criteria.
            </CardContent>
          </Card>
        )}
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Book</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &ldquo;{bookToDelete?.title}
              &rdquo;? This action cannot be undone. All chapters will be
              deleted, but your notes will be preserved.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant='outline'
              onClick={() => {
                setDeleteDialogOpen(false);
                setBookToDelete(null);
              }}
              disabled={deletingId !== null}
            >
              Cancel
            </Button>
            <Button
              variant='outline'
              onClick={handleDeleteBook}
              disabled={deletingId !== null}
            >
              {deletingId ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
