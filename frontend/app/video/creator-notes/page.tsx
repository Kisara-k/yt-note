'use client';

import { useAuth } from '@/lib/auth-context';
import { CreatorNotes } from '@/components/creator-notes';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function CreatorNotesPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className='flex items-center justify-center min-h-screen'>
        <div className='text-lg'>Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className='min-h-screen bg-background'>
      <CreatorNotes />
    </div>
  );
}
