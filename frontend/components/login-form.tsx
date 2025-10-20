'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Loader2, LogIn, UserPlus } from 'lucide-react';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const { signIn, signUp } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      if (isSignUp) {
        await signUp(email, password);
        toast.success(
          'Account created! Please check your email to verify your account.'
        );
        setIsSignUp(false);
        setPassword('');
      } else {
        await signIn(email, password);
        toast.success('Successfully signed in!');
      }
    } catch (error) {
      console.error('Authentication error:', error);

      // Check if it's a network/connection error
      const errorMessage =
        error instanceof Error ? error.message : 'Authentication failed';
      if (
        errorMessage.includes('fetch') ||
        errorMessage.includes('network') ||
        errorMessage.includes('Failed to fetch')
      ) {
        toast.error(
          'Connection Error: Unable to reach the backend server. Please check that the backend is running and NEXT_PUBLIC_BACKEND_URL is configured correctly.',
          { duration: 5000 }
        );
      } else {
        toast.error(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-background p-4'>
      <div className='w-full max-w-md space-y-8'>
        <div className='text-center'>
          <h1 className='text-4xl font-bold mb-2'>YouTube Notes</h1>
          <p className='text-muted-foreground'>
            {isSignUp
              ? 'Create an account to get started'
              : 'Sign in to your account'}
          </p>
        </div>

        <div className='bg-card border rounded-lg p-8 space-y-6'>
          <form onSubmit={handleSubmit} className='space-y-4'>
            <div className='space-y-2'>
              <Label htmlFor='email'>Email</Label>
              <Input
                id='email'
                type='email'
                placeholder='Enter your email'
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className='space-y-2'>
              <Label htmlFor='password'>Password</Label>
              <Input
                id='password'
                type='password'
                placeholder='Enter your password'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
                minLength={6}
              />
              {isSignUp && (
                <p className='text-xs text-muted-foreground'>
                  Password must be at least 6 characters
                </p>
              )}
            </div>

            <Button type='submit' className='w-full' disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  {isSignUp ? 'Creating account...' : 'Signing in...'}
                </>
              ) : (
                <>
                  {isSignUp ? (
                    <>
                      <UserPlus className='mr-2 h-4 w-4' />
                      Sign Up
                    </>
                  ) : (
                    <>
                      <LogIn className='mr-2 h-4 w-4' />
                      Sign In
                    </>
                  )}
                </>
              )}
            </Button>
          </form>

          <div className='text-center'>
            <button
              type='button'
              onClick={() => setIsSignUp(!isSignUp)}
              className='text-sm text-muted-foreground hover:text-foreground transition-colors'
              disabled={loading}
            >
              {isSignUp
                ? 'Already have an account? Sign in'
                : "Don't have an account? Sign up"}
            </button>
          </div>
        </div>

        <div className='bg-muted/50 border rounded-lg p-4'>
          <p className='text-sm text-muted-foreground text-center'>
            <strong>Note:</strong> Only verified email addresses can access this
            application. Contact the administrator if you need access.
          </p>
        </div>
      </div>
    </div>
  );
}
