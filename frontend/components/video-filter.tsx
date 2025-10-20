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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
  Trash2,
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/lib/auth-context';
import { API_BASE_URL } from '@/lib/config';
import Link from 'next/link';

interface VideoInfo {
  id: string;
  title: string;
  channel_title: string;
  channel_id: string;
  duration: string;
  view_count: number;
  published_at: string;
  tags: string[];
}

type SortField =
  | 'title'
  | 'channel_title'
  | 'duration'
  | 'view_count'
  | 'published_at';
type SortDirection = 'asc' | 'desc' | null;

export function VideoFilter() {
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [videoToDelete, setVideoToDelete] = useState<{
    id: string;
    title: string;
  } | null>(null);
  const [sortField, setSortField] = useState<SortField | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [filters, setFilters] = useState({
    channel: '',
    creator: '',
    minDuration: '',
    maxDuration: '',
    selectedTags: [] as string[],
  });
  const { getAccessToken } = useAuth();

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch('/api/videos', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load videos');
      }

      const data = await response.json();
      setVideos(data.videos || []);
    } catch (error) {
      console.error('Error loading videos:', error);
      toast.error('Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  const parseDuration = (duration: string | null | undefined): number => {
    if (!duration) return 0;
    const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    if (!match) return 0;
    const hours = parseInt(match[1] || '0');
    const minutes = parseInt(match[2] || '0');
    const seconds = parseInt(match[3] || '0');
    return hours * 3600 + minutes * 60 + seconds;
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs
        .toString()
        .padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
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
      channel: '',
      creator: '',
      minDuration: '',
      maxDuration: '',
      selectedTags: [],
    });
  };

  const openDeleteDialog = (videoId: string, videoTitle: string) => {
    setVideoToDelete({ id: videoId, title: videoTitle });
    setDeleteDialogOpen(true);
  };

  const handleDeleteVideo = async () => {
    if (!videoToDelete) return;

    setDeletingId(videoToDelete.id);
    try {
      const token = await getAccessToken();
      if (!token) {
        return;
      }

      const response = await fetch(
        `${API_BASE_URL}/api/video/${videoToDelete.id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete video');
      }

      // Remove video from local state
      setVideos((prev) => prev.filter((v) => v.id !== videoToDelete.id));
      setDeleteDialogOpen(false);
      setVideoToDelete(null);
    } catch (error) {
      console.error('Error deleting video:', error);
    } finally {
      setDeletingId(null);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle through: asc -> desc -> null
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
      return <ArrowUpDown className='h-4 w-4' />;
    }
    if (sortDirection === 'asc') {
      return <ArrowUp className='h-4 w-4' />;
    }
    return <ArrowDown className='h-4 w-4' />;
  };

  // Get unique channels for dropdown
  const uniqueChannels = useMemo(() => {
    const channels = [...new Set(videos.map((v) => v.channel_title))];
    return channels.sort();
  }, [videos]);

  const filteredVideos = videos.filter((video) => {
    if (
      filters.channel &&
      !video.channel_title.toLowerCase().includes(filters.channel.toLowerCase())
    ) {
      return false;
    }

    if (
      filters.creator &&
      filters.creator !== '__all__' &&
      video.channel_title !== filters.creator
    ) {
      return false;
    }

    if (filters.minDuration || filters.maxDuration) {
      const duration = parseDuration(video.duration);
      const minDur = filters.minDuration
        ? parseInt(filters.minDuration) * 60
        : 0;
      const maxDur = filters.maxDuration
        ? parseInt(filters.maxDuration) * 60
        : Infinity;
      if (duration < minDur || duration > maxDur) {
        return false;
      }
    }

    if (filters.selectedTags.length > 0) {
      const videoTags = video.tags || [];
      const hasTag = filters.selectedTags.some((tag) =>
        videoTags.includes(tag)
      );
      if (!hasTag) {
        return false;
      }
    }

    return true;
  });

  const sortedVideos = useMemo(() => {
    if (!sortField || !sortDirection) {
      return filteredVideos;
    }

    return [...filteredVideos].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      if (sortField === 'duration') {
        aValue = parseDuration(a.duration);
        bValue = parseDuration(b.duration);
      } else if (sortField === 'view_count') {
        aValue = a.view_count || 0;
        bValue = b.view_count || 0;
      } else if (sortField === 'published_at') {
        aValue = new Date(a.published_at).getTime();
        bValue = new Date(b.published_at).getTime();
      } else {
        aValue = a[sortField].toLowerCase();
        bValue = b[sortField].toLowerCase();
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredVideos, sortField, sortDirection]);

  return (
    <div className='min-h-screen bg-background p-6'>
      <div className='max-w-7xl mx-auto space-y-6'>
        <div className='flex justify-between items-center'>
          <h1 className='text-3xl font-bold'>Filter Videos</h1>
          <div className='flex-1 flex justify-center'>
            <Link href='/video'>
              <Button variant='outline'>Back to Notes</Button>
            </Link>
          </div>
          <div className='w-[140px]'></div>
        </div>

        <Card>
          <CardContent className='pt-6 pb-4'>
            <div className='grid grid-cols-1 md:grid-cols-12 gap-3 items-end'>
              <div className='md:col-span-4'>
                <Label htmlFor='channel' className='text-xs font-medium mb-1.5'>
                  Channel Name
                </Label>
                <Input
                  id='channel'
                  placeholder='Search by channel...'
                  className='h-9'
                  value={filters.channel}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, channel: e.target.value }))
                  }
                />
              </div>

              <div className='md:col-span-4'>
                <Label htmlFor='creator' className='text-xs font-medium mb-1.5'>
                  Creator Filter
                </Label>
                <Select
                  value={filters.creator}
                  onValueChange={(value) =>
                    setFilters((prev) => ({ ...prev, creator: value }))
                  }
                >
                  <SelectTrigger id='creator' className='h-9'>
                    <SelectValue placeholder='All creators' />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value='__all__'>All creators</SelectItem>
                    {uniqueChannels.map((channel) => (
                      <SelectItem key={channel} value={channel}>
                        {channel}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className='md:col-span-1'>
                <Label
                  htmlFor='minDuration'
                  className='text-xs font-medium mb-1.5'
                >
                  Min
                </Label>
                <Input
                  id='minDuration'
                  type='number'
                  placeholder='0'
                  className='h-9'
                  value={filters.minDuration}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      minDuration: e.target.value,
                    }))
                  }
                />
              </div>

              <div className='md:col-span-1'>
                <Label
                  htmlFor='maxDuration'
                  className='text-xs font-medium mb-1.5'
                >
                  Max
                </Label>
                <Input
                  id='maxDuration'
                  type='number'
                  placeholder='60'
                  className='h-9'
                  value={filters.maxDuration}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      maxDuration: e.target.value,
                    }))
                  }
                />
              </div>

              <div className='md:col-span-1 flex justify-end'>
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
              Showing {sortedVideos.length} of {videos.length} videos
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className='flex items-center justify-center p-12'>
            <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
          </div>
        ) : sortedVideos.length > 0 ? (
          <Card>
            <CardContent className='p-0'>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className='w-[40%]'>
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
                        onClick={() => handleSort('channel_title')}
                      >
                        Channel
                        {getSortIcon('channel_title')}
                      </Button>
                    </TableHead>
                    <TableHead className='w-[10%]'>
                      <Button
                        variant='ghost'
                        size='sm'
                        className='h-8 font-medium'
                        onClick={() => handleSort('duration')}
                      >
                        Duration
                        {getSortIcon('duration')}
                      </Button>
                    </TableHead>
                    <TableHead className='w-[10%]'>
                      <Button
                        variant='ghost'
                        size='sm'
                        className='h-8 font-medium'
                        onClick={() => handleSort('view_count')}
                      >
                        Views
                        {getSortIcon('view_count')}
                      </Button>
                    </TableHead>
                    <TableHead className='w-[10%]'>
                      <Button
                        variant='ghost'
                        size='sm'
                        className='h-8 font-medium'
                        onClick={() => handleSort('published_at')}
                      >
                        Published
                        {getSortIcon('published_at')}
                      </Button>
                    </TableHead>
                    <TableHead className='w-[15%]'>Tags</TableHead>
                    <TableHead className='w-[10%]'>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedVideos.map((video) => (
                    <TableRow key={video.id} className='h-12'>
                      <TableCell className='font-medium py-2'>
                        <Link
                          href={`/video?v=${video.id}`}
                          className='line-clamp-2 hover:underline text-primary'
                        >
                          {video.title}
                        </Link>
                      </TableCell>
                      <TableCell className='py-2'>
                        {video.channel_title}
                      </TableCell>
                      <TableCell className='py-2'>
                        {formatDuration(parseDuration(video.duration))}
                      </TableCell>
                      <TableCell className='py-2'>
                        {video.view_count?.toLocaleString() || 0}
                      </TableCell>
                      <TableCell className='py-2'>
                        {new Date(video.published_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className='py-2'>
                        <div className='flex flex-wrap gap-1'>
                          {video.tags?.slice(0, 2).map((tag: string) => (
                            <span
                              key={tag}
                              className='text-xs bg-secondary px-2 py-0.5 rounded'
                            >
                              {tag}
                            </span>
                          ))}
                          {video.tags?.length > 2 && (
                            <span className='text-xs text-muted-foreground'>
                              +{video.tags.length - 2}
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className='py-2'>
                        <Button
                          variant='outline'
                          size='sm'
                          onClick={() =>
                            openDeleteDialog(video.id, video.title)
                          }
                          disabled={deletingId === video.id}
                        >
                          {deletingId === video.id ? (
                            <Loader2 className='h-4 w-4 animate-spin' />
                          ) : (
                            <Trash2 className='h-4 w-4' />
                          )}
                        </Button>
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
              No videos match your filters. Try adjusting your search criteria.
            </CardContent>
          </Card>
        )}
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Video</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &ldquo;{videoToDelete?.title}
              &rdquo;? This action cannot be undone. All chunks will be deleted,
              but your notes will be preserved.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant='outline'
              onClick={() => {
                setDeleteDialogOpen(false);
                setVideoToDelete(null);
              }}
              disabled={deletingId !== null}
            >
              Cancel
            </Button>
            <Button
              variant='outline'
              onClick={handleDeleteVideo}
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
