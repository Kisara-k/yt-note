'use client';

import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useSettings } from '@/lib/settings-context';

export function ChunkTextToggle() {
  const { showChunkText, toggleChunkText } = useSettings();

  return (
    <div className='flex items-center space-x-2'>
      <Switch
        id='chunk-text-toggle'
        checked={showChunkText}
        onCheckedChange={toggleChunkText}
      />
      <Label
        htmlFor='chunk-text-toggle'
        className='cursor-pointer text-sm font-medium whitespace-nowrap'
      >
        Show Text
      </Label>
    </div>
  );
}
