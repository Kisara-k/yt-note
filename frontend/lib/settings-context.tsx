'use client';

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react';

interface SettingsContextType {
  showChunkText: boolean;
  toggleChunkText: () => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(
  undefined
);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [showChunkText, setShowChunkText] = useState(true);
  const [isClient, setIsClient] = useState(false);

  // Load setting from localStorage on mount
  useEffect(() => {
    setIsClient(true);
    const stored = localStorage.getItem('showChunkText');
    if (stored !== null) {
      setShowChunkText(stored === 'true');
    }
  }, []);

  // Save setting to localStorage when changed
  useEffect(() => {
    if (isClient) {
      localStorage.setItem('showChunkText', showChunkText.toString());
    }
  }, [showChunkText, isClient]);

  const toggleChunkText = () => {
    setShowChunkText((prev) => !prev);
  };

  return (
    <SettingsContext.Provider value={{ showChunkText, toggleChunkText }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
}
