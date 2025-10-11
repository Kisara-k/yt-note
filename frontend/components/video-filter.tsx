'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, Filter, X } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/lib/auth-context';
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

export function VideoFilter() {
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    channel: '',
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

  const parseDuration = (duration: string): number => {
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
      minDuration: '',
      maxDuration: '',
      selectedTags: [],
    });
  };

  const filteredVideos = videos.filter((video) => {
    if (
      filters.channel &&
      !video.channel_title.toLowerCase().includes(filters.channel.toLowerCase())
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

  return (
    <div className='min-h-screen bg-background p-6'>
      <div className='max-w-7xl mx-auto space-y-6'>
        <div className='flex justify-between items-center'>
          <h1 className='text-3xl font-bold'>Filter Videos</h1>
          <Link href='/'>
            <Button variant='outline'>Back to Notes</Button>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <Filter className='h-5 w-5' />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
              <div>
                <Label htmlFor='channel'>Channel Name</Label>
                <Input
                  id='channel'
                  placeholder='Search by channel...'
                  value={filters.channel}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, channel: e.target.value }))
                  }
                />
              </div>

              <div>
                <Label htmlFor='minDuration'>Min Duration (minutes)</Label>
                <Input
                  id='minDuration'
                  type='number'
                  placeholder='0'
                  value={filters.minDuration}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      minDuration: e.target.value,
                    }))
                  }
                />
              </div>

              <div>
                <Label htmlFor='maxDuration'>Max Duration (minutes)</Label>
                <Input
                  id='maxDuration'
                  type='number'
                  placeholder='60'
                  value={filters.maxDuration}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      maxDuration: e.target.value,
                    }))
                  }
                />
              </div>
            </div>

            <div className='flex justify-between items-center'>
              <div className='text-sm text-muted-foreground'>
                Showing {filteredVideos.length} of {videos.length} videos
              </div>
              <Button variant='ghost' size='sm' onClick={clearFilters}>
                <X className='h-4 w-4 mr-2' />
                Clear Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className='flex items-center justify-center p-12'>
            <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
          </div>
        ) : (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
            {filteredVideos.map((video) => (
              <Card
                key={video.id}
                className='hover:shadow-lg transition-shadow'
              >
                <CardHeader>
                  <CardTitle className='text-base line-clamp-2'>
                    {video.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className='space-y-2'>
                  <div className='text-sm text-muted-foreground space-y-1'>
                    <div>Channel: {video.channel_title}</div>
                    <div>
                      Duration: {formatDuration(parseDuration(video.duration))}
                    </div>
                    <div>Views: {video.view_count?.toLocaleString() || 0}</div>
                  </div>
                  <div className='flex flex-wrap gap-1 mt-2'>
                    {video.tags?.slice(0, 3).map((tag: string) => (
                      <span
                        key={tag}
                        className='text-xs bg-secondary px-2 py-1 rounded'
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <Link href={`/?video=${video.id}`}>
                    <Button className='w-full mt-2' size='sm'>
                      View Video
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && filteredVideos.length === 0 && (
          <Card>
            <CardContent className='p-12 text-center text-muted-foreground'>
              No videos match your filters. Try adjusting your search criteria.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
