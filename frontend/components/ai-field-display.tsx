'use client';

import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';

interface AIFieldDisplayProps {
  title: string;
  content: string | null | undefined;
  height?: string;
  onRegenerate?: () => void;
  isRegenerating?: boolean;
  isLoading?: boolean;
  useMarkdown?: boolean;
}

export function AIFieldDisplay({
  title,
  content,
  height = 'h-48',
  onRegenerate,
  isRegenerating = false,
  isLoading = false,
  useMarkdown = true,
}: AIFieldDisplayProps) {
  return (
    <Card className='flex flex-col'>
      <CardHeader className='px-3 pt-1.5 pb-1.5 pr-1.5 shrink-0'>
        <div className='flex items-center justify-between gap-2'>
          <CardTitle className='text-sm'>{title}</CardTitle>
          {onRegenerate && (
            <Button
              size='sm'
              variant='ghost'
              onClick={onRegenerate}
              disabled={isRegenerating || isLoading}
              className='h-5 w-5 p-0 shrink-0'
              title='Regenerate this field'
            >
              <RefreshCw
                className={`h-3 w-3 ${isRegenerating ? 'animate-spin' : ''}`}
              />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent
        className={`${height} overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent hover:scrollbar-thumb-gray-500`}
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgb(156 163 175) transparent',
        }}
      >
        {isLoading && !isRegenerating ? (
          <div className='flex items-center justify-center py-4'>
            <RefreshCw className='h-4 w-4 animate-spin text-muted-foreground' />
          </div>
        ) : (
          <div className='text-xs prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-p:text-xs prose-headings:my-1 prose-headings:text-xs prose-ul:my-1 prose-ul:text-xs prose-ol:my-1 prose-ol:text-xs prose-li:my-0.5 prose-li:text-xs prose-strong:text-xs prose-em:text-xs'>
            {content ? (
              useMarkdown ? (
                <ReactMarkdown>{content}</ReactMarkdown>
              ) : (
                <div className='whitespace-pre-wrap'>{content}</div>
              )
            ) : (
              <span className='text-muted-foreground text-xs'>
                Not available
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
