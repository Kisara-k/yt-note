'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Search, Calendar } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

interface NoteWithVideo {
  video_id: string;
  note_content: string;
  created_at: string;
  updated_at: string;
  video_title: string;
  channel_title: string;
  channel_id: string;
  published_at: string;
}

export function CreatorNotes() {
  const [channelName, setChannelName] = useState('');
  const [notes, setNotes] = useState<NoteWithVideo[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const { getAccessToken } = useAuth();

  const searchNotes = async () => {
    if (!channelName.trim()) {
      toast.error('Please enter a channel name');
      return;
    }

    setLoading(true);
    setHasSearched(true);
    try {
      const token = await getAccessToken();
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch(
        `/api/creator-notes?channel=${encodeURIComponent(channelName)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load notes');
      }

      const data = await response.json();
      setNotes(data.notes || []);
    } catch (error) {
      console.error('Error loading notes:', error);
      toast.error('Failed to load creator notes');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      searchNotes();
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className='min-h-screen bg-background p-6'>
      <div className='max-w-4xl mx-auto space-y-6'>
        <div className='flex justify-between items-center'>
          <h1 className='text-3xl font-bold'>Creator Notes</h1>
          <div className='flex gap-2'>
            <Link href='/filter'>
              <Button variant='outline'>Filter Videos</Button>
            </Link>
            <Link href='/'>
              <Button variant='outline'>Back to Notes</Button>
            </Link>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <Search className='h-5 w-5' />
              Search by Creator
            </CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='flex gap-2'>
              <div className='flex-1'>
                <Label htmlFor='channel' className='sr-only'>
                  Channel Name
                </Label>
                <Input
                  id='channel'
                  placeholder='Enter channel name or ID...'
                  value={channelName}
                  onChange={(e) => setChannelName(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                />
              </div>
              <Button
                onClick={searchNotes}
                disabled={loading || !channelName.trim()}
              >
                {loading ? (
                  <>
                    <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className='mr-2 h-4 w-4' />
                    Search
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className='flex items-center justify-center p-12'>
            <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
          </div>
        ) : hasSearched && notes.length === 0 ? (
          <Card>
            <CardContent className='p-12 text-center text-muted-foreground'>
              No notes found for this creator. Make sure you've created notes
              for their videos.
            </CardContent>
          </Card>
        ) : (
          <div className='space-y-4'>
            {notes.map((note) => (
              <Card key={note.video_id}>
                <CardHeader>
                  <div className='flex justify-between items-start gap-4'>
                    <div className='flex-1'>
                      <CardTitle className='text-lg mb-2'>
                        {note.video_title}
                      </CardTitle>
                      <div className='flex items-center gap-4 text-sm text-muted-foreground'>
                        <span>Video ID: {note.video_id}</span>
                        <span className='flex items-center gap-1'>
                          <Calendar className='h-3 w-3' />
                          {formatDate(note.created_at)}
                        </span>
                      </div>
                    </div>
                    <Link href={`/?video=${note.video_id}`}>
                      <Button size='sm' variant='outline'>
                        View Video
                      </Button>
                    </Link>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className='prose prose-sm dark:prose-invert max-w-none'>
                    <ReactMarkdown>{note.note_content}</ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && !hasSearched && (
          <Card>
            <CardContent className='p-12 text-center text-muted-foreground'>
              <Search className='h-16 w-16 mx-auto mb-4 opacity-20' />
              <p className='text-lg'>
                Enter a channel name above to view all notes for that creator
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
