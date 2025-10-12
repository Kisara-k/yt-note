'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/lib/auth-context';

interface ChunkIndex {
  chunk_id: number;
  short_title: string;
}

interface ChunkDetails {
  chunk_id: number;
  short_title: string;
  chunk_text: string;
  ai_field_1: string;
  ai_field_2: string;
  ai_field_3: string;
}

interface ChunkViewerProps {
  videoId: string;
}

export function ChunkViewer({ videoId }: ChunkViewerProps) {
  const [chunkIndex, setChunkIndex] = useState<ChunkIndex[]>([]);
  const [selectedChunkId, setSelectedChunkId] = useState<number | null>(null);
  const [chunkDetails, setChunkDetails] = useState<ChunkDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingChunks, setLoadingChunks] = useState(true);
  const { getAccessToken } = useAuth();

  useEffect(() => {
    if (videoId) {
      loadChunkIndex();
    }
  }, [videoId]);

  useEffect(() => {
    if (selectedChunkId !== null) {
      loadChunkDetails(selectedChunkId);
    }
  }, [selectedChunkId]);

  const loadChunkIndex = async () => {
    setLoadingChunks(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        console.error('No access token available');
        setChunkIndex([]);
        setLoadingChunks(false);
        return;
      }

      const response = await fetch(`/api/chunks/${videoId}/index`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        // If it's a 404 or 500, might just mean no chunks exist yet
        if (response.status === 404 || response.status === 500) {
          setChunkIndex([]);
          setLoadingChunks(false);
          return;
        }
        throw new Error('Failed to load chunk index');
      }

      const data = await response.json();
      setChunkIndex(data.index || []);

      if (data.index && data.index.length > 0) {
        setSelectedChunkId(data.index[0].chunk_id);
      }
    } catch (error) {
      console.error('Error loading chunk index:', error);
      // Don't show error toast if chunks simply don't exist yet
      setChunkIndex([]);
    } finally {
      setLoadingChunks(false);
    }
  };

  const loadChunkDetails = async (chunkId: number) => {
    setLoading(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        setLoading(false);
        return;
      }

      const response = await fetch(`/api/chunks/${videoId}/${chunkId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load chunk details');
      }

      const data = await response.json();
      setChunkDetails(data);
    } catch (error) {
      console.error('Error loading chunk details:', error);
      toast.error('Failed to load chunk details');
    } finally {
      setLoading(false);
    }
  };

  if (loadingChunks) {
    return (
      <div className='flex items-center justify-center p-8'>
        <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
      </div>
    );
  }

  if (chunkIndex.length === 0) {
    return (
      <Card>
        <CardContent className='p-6 text-center text-muted-foreground'>
          No chunks available for this video. Process the video to generate
          chunks.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className='space-y-4'>
      <div className='flex items-center gap-4'>
        <Select
          value={selectedChunkId?.toString()}
          onValueChange={(value) => setSelectedChunkId(parseInt(value))}
        >
          <SelectTrigger className='w-full'>
            <SelectValue placeholder='Select a chunk' />
          </SelectTrigger>
          <SelectContent>
            {chunkIndex.map((chunk) => (
              <SelectItem
                key={chunk.chunk_id}
                value={chunk.chunk_id.toString()}
              >
                {chunk.chunk_id + 1}. {chunk.short_title || 'Untitled'}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className='flex items-center justify-center p-8'>
          <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
        </div>
      ) : chunkDetails ? (
        <div className='space-y-4'>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>Summary</CardTitle>
              </CardHeader>
              <CardContent className='max-h-64 overflow-y-auto text-sm'>
                {chunkDetails.ai_field_1 || 'Not available'}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>Key Points</CardTitle>
              </CardHeader>
              <CardContent className='max-h-64 overflow-y-auto text-sm'>
                {chunkDetails.ai_field_2 || 'Not available'}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>Topics</CardTitle>
              </CardHeader>
              <CardContent className='max-h-48 overflow-y-auto text-sm'>
                {chunkDetails.ai_field_3 || 'Not available'}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className='p-3 pb-2'>
                <CardTitle className='text-sm'>Chunk Text</CardTitle>
              </CardHeader>
              <CardContent className='max-h-48 overflow-y-auto text-sm'>
                {chunkDetails.chunk_text || 'Not available'}
              </CardContent>
            </Card>
          </div>
        </div>
      ) : null}
    </div>
  );
}
