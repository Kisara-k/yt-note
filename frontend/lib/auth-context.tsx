'use client';

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Validate environment variables
if (
  !supabaseUrl ||
  !supabaseAnonKey ||
  supabaseUrl.includes('your-project') ||
  supabaseAnonKey.includes('your_anon_key')
) {
  console.error(
    '❌ Supabase credentials not configured!\n\n' +
      'Please set up your Supabase credentials in frontend/.env.local:\n' +
      '  NEXT_PUBLIC_SUPABASE_URL=your_actual_supabase_url\n' +
      '  NEXT_PUBLIC_SUPABASE_ANON_KEY=your_actual_anon_key\n\n' +
      'See AUTHENTICATION_SETUP.md for detailed setup instructions.'
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check active session
    supabase.auth
      .getSession()
      .then(({ data: { session } }: { data: { session: any } }) => {
        if (session?.user) {
          setUser({
            id: session.user.id,
            email: session.user.email!,
          });
        }
        setLoading(false);
      })
      .catch((error) => {
        console.error(
          'Failed to get session. Please check your Supabase credentials in .env.local',
          error
        );
        setLoading(false);
      });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event: any, session: any) => {
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email!,
        });
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signIn = async (email: string, password: string) => {
    // First, verify the email is in the allowed list
    const verifyResponse = await fetch(
      'http://localhost:8000/api/auth/verify-email',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      }
    );

    const verifyData = await verifyResponse.json();

    if (!verifyData.is_verified) {
      throw new Error('This email is not authorized to access the application');
    }

    // If verified, proceed with Supabase authentication
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) throw error;

    if (data.user) {
      setUser({
        id: data.user.id,
        email: data.user.email!,
      });
    }
  };

  const signUp = async (email: string, password: string) => {
    // First, verify the email is in the allowed list
    const verifyResponse = await fetch(
      'http://localhost:8000/api/auth/verify-email',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      }
    );

    const verifyData = await verifyResponse.json();

    if (!verifyData.is_verified) {
      throw new Error('This email is not authorized to access the application');
    }

    // If verified, proceed with Supabase sign up
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (error) throw error;

    // Note: User will need to verify their email before they can sign in
    // Supabase will send a verification email automatically
  };

  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    setUser(null);
  };

  const getAccessToken = useCallback(async (): Promise<string | null> => {
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token || null;
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, signIn, signUp, signOut, getAccessToken }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
