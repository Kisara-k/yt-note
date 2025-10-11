'use client';

import { VideoNotesEditor } from '@/components/video-notes-editor';
import { LoginForm } from '@/components/login-form';
import { useAuth } from '@/lib/auth-context';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className='min-h-screen flex items-center justify-center bg-background'>
        <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
      </div>
    );
  }

  if (!user) {
    return <LoginForm />;
  }

  return <VideoNotesEditor />;
}
