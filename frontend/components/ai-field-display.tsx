'use client';

import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface AIFieldDisplayProps {
  title: string;
  content: string | null | undefined;
  maxHeight?: string;
}

export function AIFieldDisplay({
  title,
  content,
  maxHeight = 'max-h-64',
}: AIFieldDisplayProps) {
  return (
    <Card>
      <CardHeader className='p-3 pb-2'>
        <CardTitle className='text-sm'>{title}</CardTitle>
      </CardHeader>
      <CardContent className={`${maxHeight} overflow-y-auto`}>
        {/* 
          Styling explanation:
          - text-xs: Base Tailwind utility for extra small text (0.75rem / 12px)
          - prose: Tailwind Typography plugin that adds beautiful default styles for markdown/HTML content
          - prose-sm: Small prose variant (reduces default prose sizing)
          - prose-*:text-xs: Overrides specific prose element sizes (p, headings, ul, ol, li, strong, em) to text-xs
          - prose-*:my-*: Controls vertical spacing between elements (my-1 = 0.25rem, my-0.5 = 0.125rem)
          
          Why both prose and text-xs?
          - prose provides semantic markdown styling (spacing, colors, line-height, etc.)
          - text-xs sets the base font size small, then prose-*:text-xs enforces it on all markdown elements
          - Without prose: plain unstyled text. Without text-xs: prose's default sizes are too large.
        */}
        <div className='text-xs prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-p:text-xs prose-headings:my-1 prose-headings:text-xs prose-ul:my-1 prose-ul:text-xs prose-ol:my-1 prose-ol:text-xs prose-li:my-0.5 prose-li:text-xs prose-strong:text-xs prose-em:text-xs'>
          {content ? (
            <ReactMarkdown>{content}</ReactMarkdown>
          ) : (
            <span className='text-muted-foreground text-xs'>Not available</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
