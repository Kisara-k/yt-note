'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { BookChunkEditor } from '@/components/book-chunk-editor';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

function BookChunksContent() {
  const { user, loading } = useAuth();
  const searchParams = useSearchParams();
  const [bookId, setBookId] = useState<string | null>(null);

  useEffect(() => {
    const b = searchParams.get('b');
    if (b) {
      setBookId(b);
    }
  }, [searchParams]);

  if (loading) {
    return (
      <div className='flex items-center justify-center min-h-screen'>
        <Loader2 className='h-8 w-8 animate-spin' />
      </div>
    );
  }

  if (!user) {
    return (
      <div className='flex items-center justify-center min-h-screen'>
        <p>Please sign in to access book chunk editor.</p>
      </div>
    );
  }

  return <BookChunkEditor bookId={bookId} />;
}

export default function BookChunksPage() {
  return (
    <Suspense
      fallback={
        <div className='flex items-center justify-center min-h-screen'>
          <Loader2 className='h-8 w-8 animate-spin' />
        </div>
      }
    >
      <BookChunksContent />
    </Suspense>
  );
}
